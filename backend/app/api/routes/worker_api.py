import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_worker
from app.db.session import get_db
from app.models import Analysis, FileRecord, Job, Worker
from app.schemas.file_record import FileRecordResponse
from app.schemas.job import JobResponse
from app.schemas.worker import (
    WorkerClaimResponse,
    WorkerHeartbeat,
    WorkerIdentityResponse,
    WorkerJobBundle,
    WorkerLogCreate,
    WorkerPollResponse,
    WorkerStatusUpdate,
)
from app.services.job_service import append_job_log, claim_job, list_pending_jobs, store_job_results, update_job_status
from app.services.worker_service import heartbeat_worker
from app.storage.local_storage import LocalStorage

router = APIRouter(prefix="/worker", tags=["worker"])
storage = LocalStorage()


@router.post("/poll", response_model=WorkerPollResponse)
def poll_jobs(
    db: Session = Depends(get_db),
    worker: Worker = Depends(get_current_worker),
) -> WorkerPollResponse:
    jobs = list_pending_jobs(db)
    heartbeat_worker(db, worker, worker.status)
    return WorkerPollResponse(jobs=[JobResponse.model_validate(job) for job in jobs[:1]])


@router.post("/heartbeat", response_model=WorkerIdentityResponse)
def heartbeat(
    payload: WorkerHeartbeat,
    db: Session = Depends(get_db),
    worker: Worker = Depends(get_current_worker),
) -> WorkerIdentityResponse:
    worker = heartbeat_worker(db, worker, payload.status)
    return WorkerIdentityResponse.model_validate(worker)


@router.post("/jobs/{job_id}/claim", response_model=WorkerClaimResponse)
def claim(
    job_id: int,
    db: Session = Depends(get_db),
    worker: Worker = Depends(get_current_worker),
) -> WorkerClaimResponse:
    job = claim_job(db, job_id, worker)
    return WorkerClaimResponse(claimed=True, job=JobResponse.model_validate(job))


@router.get("/jobs/{job_id}/bundle", response_model=WorkerJobBundle)
def get_job_bundle(
    job_id: int,
    db: Session = Depends(get_db),
    worker: Worker = Depends(get_current_worker),
) -> WorkerJobBundle:
    job = db.get(Job, job_id)
    if not job or job.worker_id != worker.id:
        raise HTTPException(status_code=404, detail="Job not claimed by this worker")
    analysis = db.get(Analysis, job.analysis_id)
    files = db.query(FileRecord).filter(FileRecord.analysis_id == analysis.id, FileRecord.category == "input").all()
    return WorkerJobBundle(
        job=JobResponse.model_validate(job),
        input_files=[FileRecordResponse.model_validate(item) for item in files],
        analysis_metadata={
            "analysis_id": analysis.id,
            "analysis_name": analysis.name,
            "sample_id": analysis.sample_id,
            "project_name": analysis.project_name,
            "notes": analysis.notes,
            "pipeline_name": analysis.pipeline_name,
        },
    )


@router.get("/files/{file_id}/download")
def worker_download_input(
    file_id: int,
    db: Session = Depends(get_db),
    worker: Worker = Depends(get_current_worker),
):
    record = db.get(FileRecord, file_id)
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    if record.category != "input":
        raise HTTPException(status_code=400, detail="Only input files can be downloaded here")
    _ = worker
    path = storage.get_absolute_path(record.relative_path)
    return FileResponse(path, media_type="application/octet-stream", filename=record.original_name)


@router.post("/jobs/{job_id}/status", response_model=JobResponse)
def update_status(
    job_id: int,
    payload: WorkerStatusUpdate,
    db: Session = Depends(get_db),
    worker: Worker = Depends(get_current_worker),
) -> JobResponse:
    job = update_job_status(
        db,
        job_id,
        worker,
        payload.status,
        message=payload.message,
        error_message=payload.error_message,
        exit_code=payload.exit_code,
    )
    return JobResponse.model_validate(job)


@router.post("/jobs/{job_id}/logs")
def append_log(
    job_id: int,
    payload: WorkerLogCreate,
    db: Session = Depends(get_db),
    worker: Worker = Depends(get_current_worker),
) -> dict:
    append_job_log(db, job_id, worker, payload.level, payload.message)
    return {"ok": True}


@router.post("/jobs/{job_id}/results", response_model=JobResponse)
async def upload_results(
    job_id: int,
    manifest_json: str = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    worker: Worker = Depends(get_current_worker),
) -> JobResponse:
    manifest = json.loads(manifest_json)
    uploaded: list[dict] = []
    for file in files:
        relative_path = file.filename or Path(file.filename or "result.bin").name
        category = "other"
        friendly_name = Path(relative_path).name
        previewable = relative_path.lower().endswith((".png", ".jpg", ".jpeg", ".pdf", ".html"))
        target = storage.prepare_result_target(
            analysis_id=manifest["analysis_id"],
            job_id=job_id,
            relative_path=relative_path,
        )
        size_bytes = 0
        with target.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size_bytes += len(chunk)
                output.write(chunk)
        item = next((entry for entry in manifest["items"] if entry["relative_path"] == relative_path), None)
        if item:
            category = item["category"]
            friendly_name = item["friendly_name"]
        uploaded.append(
            {
                "file_type": Path(relative_path).suffix.lstrip(".") or "bin",
                "category": category,
                "friendly_name": friendly_name,
                "stored_name": Path(relative_path).name,
                "relative_path": str(target.relative_to(storage.settings.storage_root)),
                "size_bytes": size_bytes,
                "checksum": item.get("checksum") if item else None,
                "previewable": previewable,
            }
        )
    job = store_job_results(db, job_id, worker, manifest, uploaded)
    return JobResponse.model_validate(job)
