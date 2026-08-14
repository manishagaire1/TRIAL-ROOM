import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SizeChart(Base):
    __tablename__ = "size_charts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(100))

    # Ordered by waist_cm (not size_label) because size labels sort
    # alphabetically wrong — "L" < "M" < "S" as strings — while waist_cm
    # increases with size across every chart we seed.
    sizes: Mapped[list["ClothingSize"]] = relationship(
        "ClothingSize", cascade="all, delete-orphan", order_by="ClothingSize.waist_cm"
    )


class ClothingSize(Base):
    """One row per size within a SizeChart — the real numbers the size
    recommendation engine (Phase 8) compares a user's measurements
    against. docs/10: never depend on S/M/L/XL labels alone."""

    __tablename__ = "clothing_sizes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    size_chart_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("size_charts.id", ondelete="CASCADE"), index=True
    )
    size_label: Mapped[str] = mapped_column(String(10))
    chest_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    hip_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    length_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    stock_qty: Mapped[int] = mapped_column(Integer, default=0)
