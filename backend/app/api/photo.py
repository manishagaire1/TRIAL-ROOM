from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.exceptions import ImageValidationError
from app.models.user import User
from app.schemas.photo import UserPhotoRead
from app.services import photo_service
from app.utils.image_validation import read_upload_with_limit

router = APIRouter(prefix="/users/photo", tags=["photo"])


@router.get("", response_model=UserPhotoRead)
def read_photo_status(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    photo = photo_service.get_photo(db, current_user.id)
    return UserPhotoRead(has_photo=photo is not None, updated_at=photo.created_at if photo else None)


@router.post("", response_model=UserPhotoRead, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        raw_bytes = await read_upload_with_limit(file)
        photo = photo_service.upload_photo(db, current_user, raw_bytes)
    except ImageValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    return UserPhotoRead(has_photo=True, updated_at=photo.created_at)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    photo_service.delete_photo(db, current_user)


@router.get("/file")
def read_photo_file(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    data = photo_service.get_photo_bytes(db, current_user.id)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No photo uploaded.")
    return Response(content=data, media_type="image/jpeg")
