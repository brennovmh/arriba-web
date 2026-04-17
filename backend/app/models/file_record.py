from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class FileRecord(TimestampMixin, Base):
    __tablename__ = "file_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"), index=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True, index=True)
    file_type: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50), default="input")
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255))
    relative_path: Mapped[str] = mapped_column(String(1024))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    previewable: Mapped[bool] = mapped_column(default=False)

    analysis = relationship("Analysis", back_populates="files")
    job = relationship("Job", back_populates="file_records")
