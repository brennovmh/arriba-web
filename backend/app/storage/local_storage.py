from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


class LocalStorage:
    def __init__(self) -> None:
        self.settings = get_settings()

    @staticmethod
    def _safe_name(filename: str) -> str:
        return Path(filename).name.replace("..", "_")

    def _ensure_within_root(self, path: Path, root: Path) -> Path:
        path = path.resolve()
        root = root.resolve()
        if root not in path.parents and path != root:
            raise ValueError("Path traversal detected")
        return path

    async def save_upload(self, analysis_id: int, file: UploadFile) -> dict:
        original_name = self._safe_name(file.filename or "upload.fastq")
        suffix = "".join(Path(original_name).suffixes)
        stored_name = f"{uuid4().hex}{suffix}"
        target_dir = self.settings.temp_upload_root / f"analysis_{analysis_id}"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = self._ensure_within_root(target_dir / stored_name, self.settings.temp_upload_root)

        checksum = hashlib.sha256()
        total_size = 0
        with target_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)
                if total_size > self.settings.max_upload_size_bytes:
                    raise ValueError("Uploaded file exceeds configured size limit")
                checksum.update(chunk)
                output.write(chunk)

        relative_path = str(target_path.relative_to(self.settings.storage_root))
        return {
            "original_name": original_name,
            "stored_name": stored_name,
            "relative_path": relative_path,
            "size_bytes": total_size,
            "checksum": checksum.hexdigest(),
        }

    def get_absolute_path(self, relative_path: str) -> Path:
        path = self._ensure_within_root(self.settings.storage_root / relative_path, self.settings.storage_root)
        if not path.exists():
            raise FileNotFoundError(relative_path)
        return path

    def open_for_write(self, relative_path: str):
        path = self._ensure_within_root(self.settings.storage_root / relative_path, self.settings.storage_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path.open("wb"), path

    def save_worker_result_file(self, source_path: Path, analysis_id: int, job_id: int, category: str) -> dict:
        source_path = source_path.resolve()
        stored_name = source_path.name
        target_dir = self.settings.result_root / f"analysis_{analysis_id}" / f"job_{job_id}" / category
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = self._ensure_within_root(target_dir / stored_name, self.settings.result_root)
        shutil.copy2(source_path, target_path)
        checksum = hashlib.sha256(target_path.read_bytes()).hexdigest()
        relative_path = str(target_path.relative_to(self.settings.storage_root))
        return {
            "stored_name": stored_name,
            "relative_path": relative_path,
            "size_bytes": target_path.stat().st_size,
            "checksum": checksum,
        }

    def prepare_result_target(self, analysis_id: int, job_id: int, relative_path: str) -> Path:
        base_dir = self.settings.result_root / f"analysis_{analysis_id}" / f"job_{job_id}"
        target = self._ensure_within_root(base_dir / relative_path, base_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def write_json_metadata(self, analysis_id: int, job_id: int, payload: str) -> None:
        target_dir = self.settings.metadata_root / f"analysis_{analysis_id}"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / f"job_{job_id}.json"
        target_file.write_text(payload, encoding="utf-8")

    def stream_size(self, file_path: Path) -> int:
        return os.path.getsize(file_path)
