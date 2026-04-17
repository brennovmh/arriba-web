from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.file_record import FileRecordResponse
from app.schemas.job import JobResponse


class AnalysisCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sample_id: str = Field(min_length=1, max_length=255)
    project_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    pipeline_name: str = Field(default="dummy-ngs", max_length=100)


class AnalysisResponse(BaseModel):
    id: int
    name: str
    sample_id: str
    project_name: str | None
    notes: str | None
    pipeline_name: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    latest_job: JobResponse | None = None
    files: list[FileRecordResponse] = []

    model_config = {"from_attributes": True}


class SubmitAnalysisResponse(BaseModel):
    analysis_id: int
    job: JobResponse


class ReprocessAnalysisRequest(BaseModel):
    pipeline_name: str | None = None
