import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.size_chart import SizeChart


class Clothing(Base):
    __tablename__ = "clothing"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150))
    # No Brand table exists yet (docs/04: "brand_id exists as a plain
    # FK placeholder" for the future B2B phase) — a plain name is enough
    # to display for now and avoids a foreign key with nothing to point at.
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_color: Mapped[str] = mapped_column(String(30))
    available_colors: Mapped[list] = mapped_column(JSON, default=list)
    material: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Float is fine for a demo catalog; a real payments-grade system would
    # store money as integer minor units (cents) instead.
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    product_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    affiliate_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    size_chart_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("size_charts.id"), nullable=True
    )
    fit_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    size_chart: Mapped[SizeChart | None] = relationship("SizeChart")


class ClothingImage(Base):
    """Exists now so the schema is ready for real product photography;
    left unpopulated by the Phase 6 seed data (see docs/50: never fake
    real photos with placeholder files pretending to be genuine)."""

    __tablename__ = "clothing_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    clothing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clothing.id", ondelete="CASCADE"), index=True
    )
    storage_path: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
