import uuid

from sqlalchemy.orm import Session

from app.core import storage
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.models.wardrobe_item import WardrobeItem
from app.repositories import wardrobe_repository
from app.schemas.wardrobe import PaginatedWardrobe, WardrobeItemRead
from app.utils.image_validation import validate_and_normalize_image


def _to_read_model(item: WardrobeItem) -> WardrobeItemRead:
    return WardrobeItemRead(
        id=item.id,
        category=item.category,
        color=item.color,
        label=item.label,
        created_at=item.created_at,
        image_url=f"/wardrobe/{item.id}/file",
    )


def upload_item(
    db: Session, user: User, category: str, color: str, label: str | None, raw_bytes: bytes
) -> WardrobeItemRead:
    normalized = validate_and_normalize_image(raw_bytes)
    key = storage.save_bytes("wardrobe", "jpg", normalized)
    item = wardrobe_repository.create(db, user.id, category, color, key, label)
    return _to_read_model(item)


def list_items(db: Session, user: User, page: int, page_size: int) -> PaginatedWardrobe:
    items, total = wardrobe_repository.list_for_user(db, user.id, page, page_size)
    return PaginatedWardrobe(
        items=[_to_read_model(i) for i in items], total=total, page=page, page_size=page_size
    )


def _get_owned(db: Session, user: User, item_id: uuid.UUID) -> WardrobeItem:
    item = wardrobe_repository.get_by_id(db, item_id)
    if item is None or item.user_id != user.id:
        raise NotFoundError("Wardrobe item not found.")
    return item


def get_item_bytes(db: Session, user: User, item_id: uuid.UUID) -> bytes:
    item = _get_owned(db, user, item_id)
    return storage.read_bytes(item.storage_key)


def delete_item(db: Session, user: User, item_id: uuid.UUID) -> None:
    item = _get_owned(db, user, item_id)
    storage.delete(item.storage_key)
    wardrobe_repository.delete(db, item)
