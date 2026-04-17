from datetime import datetime, timezone
import json

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import Analysis, FileRecord, Job, JobLog, Worker
from app.storage.local_storage import LocalStorage

storage = LocalStorage()


def get_job_for_user(db: Session, job_id: int, user_id: int) -> Job | None:
    return (
        db.query(Job)
        .join(Analysis, Job.analysis_id == Analysis.id)
        .options(joinedload(Job.logs), joinedload(Job.file_records))
        .filter(Job.id == job_id, Analysis.created_by == user_id)
        .first()
    )


def list_pending_jobs(db: Session) -> list[Job]:
    return db.query(Job).filter(Job.status == "pending").order_by(Job.created_at.asc()).all()


def claim_job(db: Session, job_id: int, worker: Worker) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "pending":
        raise HTTPException(status_code=409, detail="Job is not pending")
    job.status = "downloading"
    job.worker_id = worker.id
    job.started_at = datetime.now(timezone.utc)
    worker.status = "busy"
    worker.last_seen_at = datetime.now(timezone.utc)
    db.add(JobLog(job_id=job.id, level="info", message=f"Job claimed by worker {worker.name}"))
    db.commit()
    db.refresh(job)
    return job


def update_job_status(
    db: Session,
    job_id: int,
    worker: Worker,
    status: str,
    message: str | None = None,
    error_message: str | None = None,
    exit_code: int | None = None,
) -> Job:
    job = db.get(Job, job_id)
    if not job or job.worker_id != worker.id:
        raise HTTPException(status_code=404, detail="Job not available for this worker")
    job.status = status
    job.error_message = error_message
    job.exit_code = exit_code
    worker.last_seen_at = datetime.now(timezone.utc)
    worker.status = "busy" if status in {"downloading", "running", "uploading_results"} else "idle"
    if status in {"completed", "failed", "cancelled"}:
        job.finished_at = datetime.now(timezone.utc)
    if message:
        db.add(JobLog(job_id=job.id, level="info", message=message))
    db.commit()
    db.refresh(job)
    return job


def append_job_log(db: Session, job_id: int, worker: Worker, level: str, message: str) -> None:
    job = db.get(Job, job_id)
    if not job or job.worker_id != worker.id:
        raise HTTPException(status_code=404, detail="Job not available for this worker")
    worker.last_seen_at = datetime.now(timezone.utc)
    db.add(JobLog(job_id=job.id, level=level, message=message))
    db.commit()


def cancel_pending_job_for_user(db: Session, job_id: int, user_id: int) -> Job:
    job = (
        db.query(Job)
        .join(Analysis, Job.analysis_id == Analysis.id)
        .filter(Job.id == job_id, Analysis.created_by == user_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending jobs can be cancelled in this MVP")
    job.status = "cancelled"
    job.finished_at = datetime.now(timezone.utc)
    db.add(JobLog(job_id=job.id, level="info", message="Job cancelled by user before worker claim"))
    db.commit()
    db.refresh(job)
    return job


def store_job_results(
    db: Session,
    job_id: int,
    worker: Worker,
    manifest: dict,
    uploaded_files: list[dict],
) -> Job:
    job = db.get(Job, job_id)
    if not job or job.worker_id != worker.id:
        raise HTTPException(status_code=404, detail="Job not available for this worker")

    file_records: list[FileRecord] = []
    for item in uploaded_files:
        file_records.append(
            FileRecord(
                analysis_id=job.analysis_id,
                job_id=job.id,
                file_type=item["file_type"],
                category=item["category"],
                original_name=item["friendly_name"],
                stored_name=item["stored_name"],
                relative_path=item["relative_path"],
                size_bytes=item["size_bytes"],
                checksum=item.get("checksum"),
                previewable=item.get("previewable", False),
            )
        )
    db.add_all(file_records)
    job.output_manifest_json = manifest
    db.add(JobLog(job_id=job.id, level="info", message="Worker uploaded result bundle"))
    storage.write_json_metadata(job.analysis_id, job.id, json.dumps(manifest, indent=2))
    db.commit()
    db.refresh(job)
    return job
