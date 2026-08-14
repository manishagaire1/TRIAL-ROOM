import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.clothing import Clothing

# Plain strings, not a DB enum type — keeps adding a future status
# (e.g. "cancelled") a one-line change instead of a migration that
# alters a Postgres enum type.
JOB_STATUSES = ("pending", "processing", "completed", "failed")


class TryOnJob(Base):
    __tablename__ = "try_on_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    user_photo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_photos.id")
    )
    clothing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clothing.id")
    )
    selected_size: Mapped[str] = mapped_column(String(10))
    selected_color: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    ai_provider: Mapped[str] = mapped_column(String(30))
    failure_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    result: Mapped["TryOnResult | None"] = relationship(
        "TryOnResult", back_populates="job", uselist=False, cascade="all, delete-orphan"
    )
    clothing: Mapped[Clothing] = relationship("Clothing")


class TryOnResult(Base):
    __tablename__ = "try_on_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    try_on_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("try_on_jobs.id", ondelete="CASCADE"),
        unique=True,
    )
    storage_key: Mapped[str] = mapped_column(String(300))
    result_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    job: Mapped[TryOnJob] = relationship("TryOnJob", back_populates="result")
