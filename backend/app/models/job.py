from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    worker_id: Mapped[int | None] = mapped_column(ForeignKey("workers.id"), nullable=True, index=True)
    pipeline_name: Mapped[str] = mapped_column(String(100))
    pipeline_version: Mapped[str] = mapped_column(String(50), default="0.1.0")
    input_manifest_json: Mapped[dict] = mapped_column(JSON, default=dict)
    output_manifest_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    analysis = relationship("Analysis", back_populates="jobs")
    worker = relationship("Worker", back_populates="jobs")
    file_records = relationship("FileRecord", back_populates="job")
    logs = relationship("JobLog", back_populates="job", cascade="all, delete-orphan")
