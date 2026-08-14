from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = auth_service.register_user(db, data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        user = auth_service.authenticate_user(db, data)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    return Token(access_token=auth_service.issue_token_for(user))


@router.post("/guest", response_model=Token, status_code=status.HTTP_201_CREATED)
def guest_session(db: Session = Depends(get_db)):
    user = auth_service.create_guest_user(db)
    return Token(access_token=auth_service.issue_token_for(user))
