from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Analysis(TimestampMixin, Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    sample_id: Mapped[str] = mapped_column(String(255), index=True)
    project_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    pipeline_name: Mapped[str] = mapped_column(String(100), default="dummy-ngs")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    files = relationship("FileRecord", back_populates="analysis", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="analysis", cascade="all, delete-orphan")
