import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.clothing import Clothing
from app.models.wardrobe_item import WardrobeItem


class SavedOutfit(Base):
    __tablename__ = "saved_outfits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    occasion: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # "Like button" from master spec Section 17 — not in the original
    # docs/04 ERD, added here since the comparison screen needs it.
    liked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    items: Mapped[list["OutfitItem"]] = relationship(
        "OutfitItem", cascade="all, delete-orphan"
    )


class OutfitItem(Base):
    """
    One row per garment in an outfit. Each row points at EITHER a
    catalog Clothing item OR a user's own WardrobeItem — never both,
    enforced by the check constraint below (docs/04's original design:
    "exactly one of clothing_id/wardrobe_item_id set"). Phase 10 only
    ever created one row per outfit; Phase 11's Outfit Builder is what
    actually uses multiple rows per outfit.
    """

    __tablename__ = "outfit_items"
    __table_args__ = (
        CheckConstraint(
            "(clothing_id IS NOT NULL) != (wardrobe_item_id IS NOT NULL)",
            name="outfit_item_exactly_one_source",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    saved_outfit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("saved_outfits.id", ondelete="CASCADE"), index=True
    )
    clothing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clothing.id"), nullable=True
    )
    wardrobe_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wardrobe_items.id"), nullable=True
    )
    slot: Mapped[str] = mapped_column(String(20))

    clothing: Mapped[Clothing | None] = relationship("Clothing")
    wardrobe_item: Mapped[WardrobeItem | None] = relationship("WardrobeItem")

    # Convenience proxies so OutfitItemRead (Pydantic, from_attributes)
    # can read these directly regardless of which source this item came
    # from — the schema output shape stays flat either way.
    @property
    def name(self) -> str:
        if self.clothing:
            return self.clothing.name
        return self.wardrobe_item.label or self.wardrobe_item.category

    @property
    def category(self) -> str:
        return self.clothing.category if self.clothing else self.wardrobe_item.category

    @property
    def primary_color(self) -> str:
        return self.clothing.primary_color if self.clothing else self.wardrobe_item.color

    @property
    def source(self) -> str:
        return "catalog" if self.clothing else "wardrobe"
