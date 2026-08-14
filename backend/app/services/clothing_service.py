import uuid

from sqlalchemy.orm import Session

from app.models.clothing import Clothing
from app.repositories import clothing_repository
from app.schemas.clothing import ClothingCreate, ClothingListItem, PaginatedClothing


def _available_sizes(item: Clothing) -> list[str]:
    if not item.size_chart:
        return []
    return [size.size_label for size in item.size_chart.sizes]


def list_clothing(
    db: Session,
    category: str | None,
    color: str | None,
    brand: str | None,
    page: int,
    page_size: int,
) -> PaginatedClothing:
    items, total = clothing_repository.list_clothing(
        db, category, color, brand, page, page_size
    )
    list_items = [
        ClothingListItem.model_validate(item, from_attributes=True).model_copy(
            update={"available_sizes": _available_sizes(item)}
        )
        for item in items
    ]
    return PaginatedClothing(items=list_items, total=total, page=page, page_size=page_size)


def get_clothing(db: Session, clothing_id: uuid.UUID) -> Clothing | None:
    return clothing_repository.get_by_id(db, clothing_id)


def create_clothing(db: Session, data: ClothingCreate) -> Clothing:
    return clothing_repository.create_clothing(db, data.model_dump())
