from __future__ import annotations

from pathlib import Path
import subprocess

from app.config.settings import get_settings
from app.pipeline_runner.registry import get_pipeline


class DockerPipelineRunner:
    def __init__(self) -> None:
        self.settings = get_settings()

    def build_command(
        self,
        input_dir: Path,
        output_dir: Path,
        refs_dir: Path,
        metadata_path: Path,
        pipeline_name: str,
    ) -> list[str]:
        pipeline = get_pipeline(pipeline_name)
        return [
            self.settings.docker_binary,
            "run",
            "--rm",
            "-v",
            f"{input_dir}:/data/input:ro",
            "-v",
            f"{output_dir}:/data/output",
            "-v",
            f"{refs_dir}:/data/refs:ro",
            "-v",
            f"{metadata_path}:/data/metadata/job.json:ro",
            pipeline["worker_image"],
            *pipeline["entry_command"],
            "--pipeline-name",
            pipeline_name,
            "--metadata",
            "/data/metadata/job.json",
            "--input-dir",
            "/data/input",
            "--output-dir",
            "/data/output",
            "--refs-dir",
            "/data/refs",
        ]

    def run(
        self,
        input_dir: Path,
        output_dir: Path,
        refs_dir: Path,
        metadata_path: Path,
        pipeline_name: str,
        log_path: Path,
    ) -> subprocess.CompletedProcess[str]:
        command = self.build_command(input_dir, output_dir, refs_dir, metadata_path, pipeline_name)
        with log_path.open("w", encoding="utf-8") as handle:
            return subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, text=True, check=False)
