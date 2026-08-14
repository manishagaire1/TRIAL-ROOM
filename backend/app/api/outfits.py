import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User
from app.schemas.outfit import (
    CompareRequest,
    CompareResponse,
    PaginatedOutfits,
    SavedOutfitCreate,
    SavedOutfitRead,
    SavedOutfitUpdate,
)
from app.services import outfit_service

router = APIRouter(prefix="/outfits", tags=["outfits"])


@router.post("", response_model=SavedOutfitRead, status_code=status.HTTP_201_CREATED)
def create_outfit(
    data: SavedOutfitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return outfit_service.create_outfit(db, current_user, data)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get("", response_model=PaginatedOutfits)
def list_outfits(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return outfit_service.list_outfits(db, current_user, page, page_size)


@router.post("/compare", response_model=CompareResponse)
def compare_outfits(
    data: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return outfit_service.compare_outfits(db, current_user, data)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.patch("/{outfit_id}", response_model=SavedOutfitRead)
def update_outfit(
    outfit_id: uuid.UUID,
    data: SavedOutfitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return outfit_service.update_outfit(db, current_user, outfit_id, data)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outfit(
    outfit_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        outfit_service.delete_outfit(db, current_user, outfit_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
