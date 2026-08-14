import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User
from app.schemas.tryon import PaginatedTryOnHistory, TryOnJobCreate, TryOnJobRead
from app.services import tryon_service

router = APIRouter(prefix="/tryon", tags=["tryon"])


@router.post("", response_model=TryOnJobRead, status_code=status.HTTP_202_ACCEPTED)
def create_try_on(
    data: TryOnJobCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        job = tryon_service.create_job(db, current_user, data)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

    # Returns immediately with status=pending; the real work happens
    # after this response is sent (Section 32's async flow).
    background_tasks.add_task(tryon_service.process_job, job.id)
    return tryon_service.get_job_for_user(db, current_user, job.id)


@router.get("/history", response_model=PaginatedTryOnHistory)
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return tryon_service.list_history(db, current_user, page, page_size)


@router.get("/{job_id}", response_model=TryOnJobRead)
def get_try_on(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return tryon_service.get_job_for_user(db, current_user, job_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get("/{job_id}/image")
def get_try_on_image(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        data = tryon_service.get_result_image_bytes(db, current_user, job_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    return Response(content=data, media_type="image/jpeg")


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_try_on(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        tryon_service.delete_job_for_user(db, current_user, job_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
