import secrets
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_worker_token
from app.models import Worker


def register_worker(db: Session, name: str, capabilities_json: dict) -> tuple[Worker, str]:
    existing = db.query(Worker).filter(Worker.name == name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Worker name already exists")
    token = secrets.token_urlsafe(32)
    worker = Worker(
        name=name,
        token_hash=hash_worker_token(token),
        capabilities_json=capabilities_json,
        status="idle",
        last_seen_at=datetime.now(timezone.utc),
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker, token


def heartbeat_worker(db: Session, worker: Worker, status: str) -> Worker:
    worker.status = status
    worker.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(worker)
    return worker
