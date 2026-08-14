import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.wardrobe_item import WardrobeItem


def create(db: Session, user_id: uuid.UUID, category: str, color: str, storage_key: str, label: str | None) -> WardrobeItem:
    item = WardrobeItem(
        user_id=user_id, category=category, color=color, storage_key=storage_key, label=label
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_by_id(db: Session, item_id: uuid.UUID) -> WardrobeItem | None:
    return db.query(WardrobeItem).filter(WardrobeItem.id == item_id).first()


def list_for_user(
    db: Session, user_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[WardrobeItem], int]:
    query = (
        select(WardrobeItem)
        .filter(WardrobeItem.user_id == user_id)
        .order_by(WardrobeItem.created_at.desc())
    )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (
        db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    )
    return list(items), total


def delete(db: Session, item: WardrobeItem) -> None:
    db.delete(item)
    db.commit()
