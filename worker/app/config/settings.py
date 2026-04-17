from functools import lru_cache
import json
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_base_url: str = "http://localhost:8000"
    worker_token: str = "replace-me"
    worker_name: str = "lab-workstation-01"
    poll_interval_seconds: int = 15
    request_timeout_seconds: int = 120

    work_root: Path = Path("/tmp/ngs-worker")
    input_root: Path = Path("/tmp/ngs-worker/input")
    run_root: Path = Path("/tmp/ngs-worker/run")
    output_root: Path = Path("/tmp/ngs-worker/output")
    log_root: Path = Path("/tmp/ngs-worker/logs")
    refs_dir: Path = Path("/data/ngs_refs")
    cleanup_after_upload: bool = False

    docker_binary: str = "docker"
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
    for path in [settings.work_root, settings.input_root, settings.run_root, settings.output_root, settings.log_root]:
        path.mkdir(parents=True, exist_ok=True)
    return settings
