import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.outfit import OutfitItem, SavedOutfit

_LOAD_ITEMS = selectinload(SavedOutfit.items).selectinload(OutfitItem.clothing)
_LOAD_WARDROBE = selectinload(SavedOutfit.items).selectinload(OutfitItem.wardrobe_item)


@dataclass
class OutfitItemSpec:
    slot: str
    clothing_id: uuid.UUID | None = None
    wardrobe_item_id: uuid.UUID | None = None


def create_outfit(
    db: Session,
    user_id: uuid.UUID,
    item_specs: list[OutfitItemSpec],
    name: str | None,
    occasion: str | None,
) -> SavedOutfit:
    outfit = SavedOutfit(user_id=user_id, name=name, occasion=occasion)
    db.add(outfit)
    db.flush()
    for spec in item_specs:
        db.add(
            OutfitItem(
                saved_outfit_id=outfit.id,
                clothing_id=spec.clothing_id,
                wardrobe_item_id=spec.wardrobe_item_id,
                slot=spec.slot,
            )
        )
    db.commit()
    db.refresh(outfit)
    return get_by_id(db, outfit.id)


def get_by_id(db: Session, outfit_id: uuid.UUID) -> SavedOutfit | None:
    query = select(SavedOutfit).options(_LOAD_ITEMS, _LOAD_WARDROBE).filter(SavedOutfit.id == outfit_id)
    return db.execute(query).scalar_one_or_none()


def get_many_for_user(
    db: Session, outfit_ids: list[uuid.UUID], user_id: uuid.UUID
) -> list[SavedOutfit]:
    query = (
        select(SavedOutfit)
        .options(_LOAD_ITEMS, _LOAD_WARDROBE)
        .filter(SavedOutfit.id.in_(outfit_ids), SavedOutfit.user_id == user_id)
    )
    return list(db.execute(query).scalars().all())


def list_for_user(
    db: Session, user_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[SavedOutfit], int]:
    query = (
        select(SavedOutfit)
        .options(_LOAD_ITEMS, _LOAD_WARDROBE)
        .filter(SavedOutfit.user_id == user_id)
        .order_by(SavedOutfit.created_at.desc())
    )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (
        db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    )
    return list(items), total


def update(db: Session, outfit: SavedOutfit, fields: dict) -> SavedOutfit:
    for key, value in fields.items():
        setattr(outfit, key, value)
    db.commit()
    return get_by_id(db, outfit.id)


def delete(db: Session, outfit: SavedOutfit) -> None:
    db.delete(outfit)
    db.commit()
