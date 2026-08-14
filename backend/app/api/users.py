from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import UserRead
from app.schemas.profile import UserProfileRead, UserProfileUpdate
from app.services import profile_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/profile", response_model=UserProfileRead)
def read_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    profile = profile_service.get_profile(db, current_user.id)
    # No row yet for a brand-new user — return an all-default object
    # instead of a 404, so the frontend always has a shape to render.
    return profile if profile else UserProfileRead()


@router.put("/profile", response_model=UserProfileRead)
def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return profile_service.update_profile(db, current_user.id, data)
