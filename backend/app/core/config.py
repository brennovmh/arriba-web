from functools import lru_cache
import json
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "lab-ngs-platform"
    environment: str = "development"
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720

    database_url: str = "postgresql://ngs:ngs@postgres:5432/ngs_platform"
    storage_root: Path = Path("/data/platform_storage")
    temp_upload_root: Path = Path("/data/platform_storage/uploads")
    result_root: Path = Path("/data/platform_storage/results")
    log_root: Path = Path("/data/platform_storage/logs")
    metadata_root: Path = Path("/data/platform_storage/metadata")

    max_upload_size_bytes: int = 20 * 1024 * 1024 * 1024
    allowed_upload_extensions: list[str] = [".fastq", ".fastq.gz", ".fq", ".fq.gz"]
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    initial_admin_email: str = "admin@lab.local"
    initial_admin_password: str = "admin123"
    initial_admin_name: str = "Lab Admin"
    available_pipelines_json: list[dict] = Field(
        default_factory=lambda: [
            {
                "name": "dummy-ngs",
                "version": "0.1.0",
                "description": "Dummy pipeline for architecture validation",
                "worker_image": "lab-ngs-dummy:latest",
                "entry_command": ["python", "/app/run_pipeline.py"],
            },
            {
                "name": "dummy-ngs-report",
                "version": "0.1.0",
                "description": "Alternate dummy profile using the same container runner",
                "worker_image": "lab-ngs-dummy:latest",
                "entry_command": ["python", "/app/run_pipeline.py"],
            },
        ]
    )

    @field_validator("available_pipelines_json", mode="before")
    @classmethod
    def parse_pipeline_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    for path in [
        settings.storage_root,
        settings.temp_upload_root,
        settings.result_root,
        settings.log_root,
        settings.metadata_root,
    ]:
        path.mkdir(parents=True, exist_ok=True)
    return settings
