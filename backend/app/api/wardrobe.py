import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.exceptions import ImageValidationError, NotFoundError
from app.models.user import User
from app.schemas.clothing import Category
from app.schemas.wardrobe import PaginatedWardrobe, WardrobeItemRead
from app.services import wardrobe_service
from app.utils.image_validation import read_upload_with_limit

router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])


@router.get("", response_model=PaginatedWardrobe)
def list_wardrobe(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return wardrobe_service.list_items(db, current_user, page, page_size)


@router.post("", response_model=WardrobeItemRead, status_code=status.HTTP_201_CREATED)
async def upload_wardrobe_item(
    file: UploadFile,
    category: Category = Form(...),
    color: str = Form(...),
    label: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        raw_bytes = await read_upload_with_limit(file)
        return wardrobe_service.upload_item(db, current_user, category, color, label, raw_bytes)
    except ImageValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.get("/{item_id}/file")
def get_wardrobe_item_file(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        data = wardrobe_service.get_item_bytes(db, current_user, item_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    return Response(content=data, media_type="image/jpeg")


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wardrobe_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        wardrobe_service.delete_item(db, current_user, item_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
