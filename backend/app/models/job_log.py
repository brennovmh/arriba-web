from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class JobLog(TimestampMixin, Base):
    __tablename__ = "job_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    level: Mapped[str] = mapped_column(default="info")
    message: Mapped[str] = mapped_column(Text)

    job = relationship("Job", back_populates="logs")
