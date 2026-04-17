from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.worker import WorkerIdentityResponse, WorkerRegisterRequest, WorkerRegisterResponse
from app.services.worker_service import register_worker

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("/register", response_model=WorkerRegisterResponse)
def register_worker_route(
    payload: WorkerRegisterRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
) -> WorkerRegisterResponse:
    worker, token = register_worker(db, payload.name, payload.capabilities_json)
    return WorkerRegisterResponse(worker_id=worker.id, worker_name=worker.name, token=token)
