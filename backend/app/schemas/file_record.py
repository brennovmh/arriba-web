from datetime import datetime

from pydantic import BaseModel


class FileRecordResponse(BaseModel):
    id: int
    analysis_id: int
    job_id: int | None
    file_type: str
    category: str
    original_name: str
    stored_name: str
    relative_path: str
    size_bytes: int
    checksum: str | None
    previewable: bool
    created_at: datetime

    model_config = {"from_attributes": True}
