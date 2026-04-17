from pathlib import Path
import json

import requests

from app.config.settings import get_settings


class ApiClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.session = requests.Session()
        self.session.headers.update({"X-Worker-Token": self.settings.worker_token})

    def _url(self, path: str) -> str:
        return f"{self.settings.api_base_url.rstrip('/')}{path}"

    def heartbeat(self, status: str) -> dict:
        response = self.session.post(
            self._url("/worker/heartbeat"),
            json={"status": status},
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def poll_jobs(self) -> list[dict]:
        response = self.session.post(self._url("/worker/poll"), timeout=self.settings.request_timeout_seconds)
        response.raise_for_status()
        return response.json().get("jobs", [])

    def claim_job(self, job_id: int) -> dict:
        response = self.session.post(
            self._url(f"/worker/jobs/{job_id}/claim"),
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def get_job_bundle(self, job_id: int) -> dict:
        response = self.session.get(
            self._url(f"/worker/jobs/{job_id}/bundle"),
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def update_job_status(
        self,
        job_id: int,
        status: str,
        message: str | None = None,
        error_message: str | None = None,
        exit_code: int | None = None,
    ) -> dict:
        response = self.session.post(
            self._url(f"/worker/jobs/{job_id}/status"),
            json={
                "status": status,
                "message": message,
                "error_message": error_message,
                "exit_code": exit_code,
            },
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def append_log(self, job_id: int, message: str, level: str = "info") -> None:
        response = self.session.post(
            self._url(f"/worker/jobs/{job_id}/logs"),
            json={"level": level, "message": message},
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()

    def download_input_file(self, file_id: int, destination: Path) -> None:
        response = self.session.get(
            self._url(f"/worker/files/{file_id}/download"),
            stream=True,
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)

    def upload_results(self, job_id: int, manifest: dict, files: list[tuple[str, tuple]]) -> dict:
        response = self.session.post(
            self._url(f"/worker/jobs/{job_id}/results"),
            data={"manifest_json": json.dumps(manifest)},
            files=files,
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()
