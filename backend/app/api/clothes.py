import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.user import User
from app.schemas.clothing import ClothingCreate, ClothingDetailRead, PaginatedClothing
from app.services import clothing_service

router = APIRouter(prefix="/clothes", tags=["clothing"])


@router.get("", response_model=PaginatedClothing)
def list_clothes(
    category: str | None = None,
    color: str | None = None,
    brand: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    # Public — guests browse the catalog without logging in (Section 24).
    return clothing_service.list_clothing(db, category, color, brand, page, page_size)


@router.get("/{clothing_id}", response_model=ClothingDetailRead)
def get_clothing(clothing_id: uuid.UUID, db: Session = Depends(get_db)):
    item = clothing_service.get_clothing(db, clothing_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found."
        )
    return item


@router.post("", response_model=ClothingDetailRead, status_code=status.HTTP_201_CREATED)
def create_clothing(
    data: ClothingCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return clothing_service.create_clothing(db, data)
