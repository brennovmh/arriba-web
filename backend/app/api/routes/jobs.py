from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import FileRecord, User
from app.schemas.file_record import FileRecordResponse
from app.schemas.job import JobDetailsResponse, JobLogResponse, JobResponse
from app.services.job_service import cancel_pending_job_for_user, get_job_for_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobDetailsResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobDetailsResponse:
    job = get_job_for_user(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobDetailsResponse(
        **JobResponse.model_validate(job).model_dump(),
        files=[FileRecordResponse.model_validate(item) for item in job.file_records],
        logs=[JobLogResponse.model_validate(log) for log in sorted(job.logs, key=lambda x: x.created_at)],
    )


@router.get("/{job_id}/logs", response_model=list[JobLogResponse])
def get_job_logs(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[JobLogResponse]:
    job = get_job_for_user(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return [JobLogResponse.model_validate(log) for log in sorted(job.logs, key=lambda x: x.created_at)]


@router.get("/{job_id}/results", response_model=list[FileRecordResponse])
def get_job_results(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FileRecordResponse]:
    job = get_job_for_user(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    result_files = [item for item in job.file_records if item.category != "input"]
    return [FileRecordResponse.model_validate(item) for item in result_files]


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobResponse:
    job = cancel_pending_job_for_user(db, job_id, current_user.id)
    return JobResponse.model_validate(job)
