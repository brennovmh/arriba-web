from pathlib import Path
import shutil

from app.config.settings import get_settings


class JobLayout:
    def __init__(self, job_id: int) -> None:
        settings = get_settings()
        self.job_id = job_id
        self.root = settings.work_root / f"job_{job_id}"
        self.input_dir = settings.input_root / f"job_{job_id}"
        self.run_dir = settings.run_root / f"job_{job_id}"
        self.output_dir = settings.output_root / f"job_{job_id}"
        self.log_dir = settings.log_root / f"job_{job_id}"
        for path in [self.root, self.input_dir, self.run_dir, self.output_dir, self.log_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def cleanup(self) -> None:
        for path in [self.input_dir, self.run_dir, self.output_dir, self.log_dir]:
            if path.exists():
                shutil.rmtree(path)
