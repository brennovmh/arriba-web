from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import FileRecord, User
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, ReprocessAnalysisRequest, SubmitAnalysisResponse
from app.schemas.file_record import FileRecordResponse
from app.schemas.job import JobResponse
from app.services.analysis_service import (
    create_analysis,
    create_reprocess_job,
    create_or_reset_job,
    get_analysis_for_user,
    latest_job_for_analysis,
    list_analyses_for_user,
)
from app.storage.local_storage import LocalStorage

router = APIRouter(prefix="/analyses", tags=["analyses"])
storage = LocalStorage()
settings = get_settings()


def _analysis_to_response(analysis) -> AnalysisResponse:
    latest_job = latest_job_for_analysis(analysis)
    return AnalysisResponse(
        id=analysis.id,
        name=analysis.name,
        sample_id=analysis.sample_id,
        project_name=analysis.project_name,
        notes=analysis.notes,
        pipeline_name=analysis.pipeline_name,
        created_by=analysis.created_by,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
        latest_job=JobResponse.model_validate(latest_job) if latest_job else None,
        files=[FileRecordResponse.model_validate(item) for item in analysis.files],
    )


@router.get("", response_model=list[AnalysisResponse])
def list_analyses(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[AnalysisResponse]:
    analyses = list_analyses_for_user(db, current_user.id)
    return [_analysis_to_response(item) for item in analyses]


@router.post("", response_model=AnalysisResponse)
def create_analysis_route(
    payload: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisResponse:
    analysis = create_analysis(db, payload, current_user.id)
    return _analysis_to_response(analysis)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisResponse:
    analysis = get_analysis_for_user(db, analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _analysis_to_response(analysis)


@router.post("/{analysis_id}/upload", response_model=list[FileRecordResponse])
async def upload_fastqs(
    analysis_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FileRecordResponse]:
    analysis = get_analysis_for_user(db, analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    saved: list[FileRecord] = []
    for file in files:
        filename = file.filename or ""
        if not any(filename.endswith(ext) for ext in settings.allowed_upload_extensions):
            raise HTTPException(status_code=400, detail=f"Unsupported file extension: {filename}")
        try:
            metadata = await storage.save_upload(analysis.id, file)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        record = FileRecord(
            analysis_id=analysis.id,
            job_id=None,
            file_type="fastq",
            category="input",
            original_name=metadata["original_name"],
            stored_name=metadata["stored_name"],
            relative_path=metadata["relative_path"],
            size_bytes=metadata["size_bytes"],
            checksum=metadata["checksum"],
            previewable=False,
        )
        db.add(record)
        saved.append(record)
    db.commit()
    for item in saved:
        db.refresh(item)
    return [FileRecordResponse.model_validate(item) for item in saved]


@router.post("/{analysis_id}/submit", response_model=SubmitAnalysisResponse)
def submit_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmitAnalysisResponse:
    analysis = get_analysis_for_user(db, analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    input_files = [item for item in analysis.files if item.category == "input"]
    if not input_files:
        raise HTTPException(status_code=400, detail="Upload at least one FASTQ file before submission")
    job = create_or_reset_job(db, analysis)
    return SubmitAnalysisResponse(analysis_id=analysis.id, job=JobResponse.model_validate(job))


@router.post("/{analysis_id}/reprocess", response_model=SubmitAnalysisResponse)
def reprocess_analysis(
    analysis_id: int,
    payload: ReprocessAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmitAnalysisResponse:
    analysis = get_analysis_for_user(db, analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    input_files = [item for item in analysis.files if item.category == "input"]
    if not input_files:
        raise HTTPException(status_code=400, detail="No FASTQ files available for reprocessing")
    try:
        job = create_reprocess_job(db, analysis, payload.pipeline_name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return SubmitAnalysisResponse(analysis_id=analysis.id, job=JobResponse.model_validate(job))
