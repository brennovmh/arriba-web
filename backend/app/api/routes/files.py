from fastapi import Query
from mimetypes import guess_type

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Analysis, FileRecord, User
from app.storage.local_storage import LocalStorage

router = APIRouter(prefix="/files", tags=["files"])
storage = LocalStorage()
settings = get_settings()


def _resolve_user(db: Session, access_token: str | None, current_user: User | None) -> User:
    if current_user:
        return current_user
    if not access_token:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(access_token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    access_token: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    resolved_user = _resolve_user(db, access_token, current_user)
    record = (
        db.query(FileRecord)
        .join(Analysis, FileRecord.analysis_id == Analysis.id)
        .filter(FileRecord.id == file_id, Analysis.created_by == resolved_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    file_path = storage.get_absolute_path(record.relative_path)
    media_type = guess_type(record.original_name)[0] or "application/octet-stream"
    return FileResponse(file_path, media_type=media_type, filename=record.original_name)
