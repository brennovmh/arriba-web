from datetime import datetime

from pydantic import BaseModel

from app.schemas.file_record import FileRecordResponse


class JobLogResponse(BaseModel):
    id: int
    level: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    id: int
    analysis_id: int
    status: str
    worker_id: int | None
    pipeline_name: str
    pipeline_version: str
    input_manifest_json: dict
    output_manifest_json: dict
    error_message: str | None
    exit_code: int | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobDetailsResponse(JobResponse):
    files: list[FileRecordResponse]
    logs: list[JobLogResponse]
