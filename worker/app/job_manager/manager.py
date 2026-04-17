from __future__ import annotations

import json
import time
from pathlib import Path

import structlog

from app.api_client.client import ApiClient
from app.config.settings import get_settings
from app.pipeline_runner.docker_runner import DockerPipelineRunner
from app.storage.layout import JobLayout
from app.utils.checksum import sha256sum
from app.utils.logging import configure_logging


class WorkerManager:
    def __init__(self) -> None:
        configure_logging()
        self.settings = get_settings()
        self.api = ApiClient()
        self.runner = DockerPipelineRunner()
        self.log = structlog.get_logger("worker").bind(worker_name=self.settings.worker_name)

    def run_forever(self) -> None:
        self.log.info("worker_started", poll_interval_seconds=self.settings.poll_interval_seconds)
        while True:
            try:
                self.api.heartbeat("idle")
                jobs = self.api.poll_jobs()
                if jobs:
                    self.process_job(jobs[0]["id"])
                else:
                    time.sleep(self.settings.poll_interval_seconds)
            except Exception as exc:  # noqa: BLE001
                self.log.error("worker_loop_error", error=str(exc))
                time.sleep(self.settings.poll_interval_seconds)

    def process_job(self, job_id: int) -> None:
        claimed = self.api.claim_job(job_id)
        if not claimed.get("claimed"):
            return

        bundle = self.api.get_job_bundle(job_id)
        metadata = bundle["analysis_metadata"]
        job = bundle["job"]
        layout = JobLayout(job_id=job_id)
        metadata_path = layout.run_dir / "job.json"
        metadata_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        log_path = layout.log_dir / "pipeline.log"

        try:
            self.api.append_log(job_id, "Downloading FASTQ inputs")
            self._download_inputs(bundle["input_files"], layout)
            self.api.update_job_status(job_id, "running", message="Pipeline execution started")
            completed = self.runner.run(
                input_dir=layout.input_dir,
                output_dir=layout.output_dir,
                refs_dir=self.settings.refs_dir,
                metadata_path=metadata_path,
                pipeline_name=metadata["pipeline_name"],
                log_path=log_path,
            )
            if log_path.exists():
                tail = log_path.read_text(encoding="utf-8")[-4000:]
                self.api.append_log(job_id, tail)
            if completed.returncode != 0:
                self.api.update_job_status(
                    job_id,
                    "failed",
                    error_message="Pipeline returned non-zero exit code",
                    exit_code=completed.returncode,
                )
                return

            manifest = self._build_output_manifest(job_id, metadata["analysis_id"], layout.output_dir, log_path)
            self.api.update_job_status(job_id, "uploading_results", message="Uploading outputs to platform")
            multipart_files = self._build_result_uploads(layout.output_dir, log_path)
            try:
                self.api.upload_results(job_id, manifest, multipart_files)
            finally:
                for _, file_tuple in multipart_files:
                    file_tuple[1].close()
            self.api.update_job_status(job_id, "completed", message="Job completed successfully", exit_code=0)
        except Exception as exc:  # noqa: BLE001
            self.log.error("job_processing_failed", job_id=job_id, error=str(exc))
            self.api.update_job_status(job_id, "failed", error_message=str(exc))
        finally:
            if self.settings.cleanup_after_upload:
                layout.cleanup()

    def _download_inputs(self, input_files: list[dict], layout: JobLayout) -> None:
        self.api.update_job_status(layout.job_id, "downloading", message="Downloading FASTQ files from VPS")
        for item in input_files:
            destination = layout.input_dir / item["original_name"]
            self.api.download_input_file(item["id"], destination)

    def _build_output_manifest(
        self,
        job_id: int,
        analysis_id: int,
        output_dir: Path,
        log_path: Path,
    ) -> dict:
        items: list[dict] = []
        category_map = {
            ".tsv": "tables",
            ".html": "reports",
            ".png": "figures",
            ".jpg": "figures",
            ".jpeg": "figures",
            ".pdf": "figures",
            ".zip": "package",
            ".log": "logs",
        }
        for file_path in sorted(output_dir.rglob("*")):
            if not file_path.is_file():
                continue
            relative_path = str(file_path.relative_to(output_dir))
            suffix = file_path.suffix.lower()
            items.append(
                {
                    "friendly_name": file_path.name,
                    "relative_path": relative_path,
                    "file_type": suffix.lstrip(".") or "bin",
                    "size": file_path.stat().st_size,
                    "category": category_map.get(suffix, "other"),
                    "previewable": suffix in {".png", ".jpg", ".jpeg", ".pdf", ".html"},
                    "checksum": sha256sum(file_path),
                }
            )
        if log_path.exists():
            items.append(
                {
                    "friendly_name": "pipeline.log",
                    "relative_path": "logs/pipeline.log",
                    "file_type": "log",
                    "size": log_path.stat().st_size,
                    "category": "logs",
                    "previewable": False,
                    "checksum": sha256sum(log_path),
                }
            )
        return {"analysis_id": analysis_id, "job_id": job_id, "items": items}

    def _build_result_uploads(self, output_dir: Path, log_path: Path) -> list[tuple[str, tuple]]:
        uploads: list[tuple[str, tuple]] = []
        for file_path in sorted(output_dir.rglob("*")):
            if not file_path.is_file():
                continue
            relative_path = str(file_path.relative_to(output_dir))
            uploads.append(("files", (relative_path, file_path.open("rb"), "application/octet-stream")))
        if log_path.exists():
            uploads.append(("files", ("logs/pipeline.log", log_path.open("rb"), "text/plain")))
        return uploads
