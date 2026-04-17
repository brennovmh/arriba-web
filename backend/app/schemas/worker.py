from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.file_record import FileRecordResponse
from app.schemas.job import JobResponse


class WorkerRegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    capabilities_json: dict = Field(default_factory=dict)


class WorkerRegisterResponse(BaseModel):
    worker_id: int
    worker_name: str
    token: str


class WorkerPollResponse(BaseModel):
    jobs: list[JobResponse]


class WorkerClaimResponse(BaseModel):
    claimed: bool
    job: JobResponse | None = None


class WorkerStatusUpdate(BaseModel):
    status: str
    message: str | None = None
    error_message: str | None = None
    exit_code: int | None = None


class WorkerLogCreate(BaseModel):
    level: str = "info"
    message: str


class WorkerHeartbeat(BaseModel):
    status: str = "idle"


class WorkerIdentityResponse(BaseModel):
    id: int
    name: str
    status: str
    last_seen_at: datetime | None

    model_config = {"from_attributes": True}


class WorkerJobBundle(BaseModel):
    job: JobResponse
    input_files: list[FileRecordResponse]
    analysis_metadata: dict
