from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.base import Base

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    from app.models import Analysis, FileRecord, Job, JobLog, User, Worker  # noqa: F401

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        admin = session.query(User).filter(User.email == settings.initial_admin_email).first()
        if not admin:
            session.add(
                User(
                    name=settings.initial_admin_name,
                    email=settings.initial_admin_email,
                    password_hash=get_password_hash(settings.initial_admin_password),
                    role="admin",
                )
            )
            session.commit()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
