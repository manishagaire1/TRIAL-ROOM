import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.clothing import Clothing
from app.models.size_chart import SizeChart


def list_clothing(
    db: Session,
    category: str | None,
    color: str | None,
    brand: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Clothing], int]:
    query = select(Clothing).options(
        selectinload(Clothing.size_chart).selectinload(SizeChart.sizes)
    )
    if category:
        query = query.filter(Clothing.category == category)
    if brand:
        query = query.filter(Clothing.brand == brand)
    if color:
        # available_colors is a JSON list; a simple Python-side filter
        # keeps this readable rather than reaching for Postgres JSON
        # operators for a catalog this small.
        query = query.filter(Clothing.primary_color == color)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (
        db.execute(query.offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )
    return list(items), total


def get_by_id(db: Session, clothing_id: uuid.UUID) -> Clothing | None:
    query = (
        select(Clothing)
        .options(selectinload(Clothing.size_chart).selectinload(SizeChart.sizes))
        .filter(Clothing.id == clothing_id)
    )
    return db.execute(query).scalar_one_or_none()


def list_all(db: Session) -> list[Clothing]:
    """Small catalog (dozens of items, not thousands) — used by the
    style recommendation engine, which needs to scan every item for
    color/category matches rather than a single filtered page."""
    return list(db.execute(select(Clothing)).scalars().all())


def create_clothing(db: Session, fields: dict) -> Clothing:
    item = Clothing(**fields)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
