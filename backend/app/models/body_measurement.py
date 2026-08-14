import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    # Quick Mode
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    usual_shirt_size: Mapped[str | None] = mapped_column(String(10), nullable=True)
    usual_pants_size: Mapped[str | None] = mapped_column(String(10), nullable=True)
    usual_dress_size: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Accurate Mode (all optional — the user opts into filling these in)
    chest_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    hip_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    shoulder_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    inseam_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    arm_length_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    leg_length_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    foot_size: Mapped[float | None] = mapped_column(Float, nullable=True)

    fit_preference: Mapped[str | None] = mapped_column(String(20), nullable=True)
    body_shape: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # True only for values a future computer-vision feature fills in
    # automatically (docs/01, Section 19) — never true for anything the
    # user typed in themselves.
    ai_estimated: Mapped[bool] = mapped_column(Boolean, default=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
