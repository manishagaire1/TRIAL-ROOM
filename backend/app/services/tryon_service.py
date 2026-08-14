import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.registry import get_provider
from app.core import storage
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.exceptions import NotFoundError, TryOnGenerationError, ValidationError
from app.models.clothing import Clothing
from app.models.tryon import TryOnJob
from app.models.user import User
from app.repositories import clothing_repository, photo_repository, tryon_repository
from app.schemas.tryon import PaginatedTryOnHistory, TryOnJobCreate, TryOnJobRead, TryOnResultRead

logger = logging.getLogger("virtualfit")


def _validate_job_input(db: Session, user: User, data: TryOnJobCreate) -> tuple[Clothing, uuid.UUID]:
    photo = photo_repository.get_by_user(db, user.id)
    if photo is None:
        raise ValidationError("Please upload a photo before generating a try-on.")

    clothing = clothing_repository.get_by_id(db, data.clothing_id)
    if clothing is None:
        raise NotFoundError("This clothing item no longer exists.")

    if clothing.size_chart and clothing.size_chart.sizes:
        valid_sizes = {size.size_label for size in clothing.size_chart.sizes}
        if data.selected_size not in valid_sizes:
            raise ValidationError(f"Size '{data.selected_size}' isn't available for this item.")

    valid_colors = {c.lower() for c in clothing.available_colors}
    if valid_colors and data.selected_color.lower() not in valid_colors:
        raise ValidationError(f"Color '{data.selected_color}' isn't available for this item.")

    return clothing, photo.id


def create_job(db: Session, user: User, data: TryOnJobCreate) -> TryOnJob:
    clothing, photo_id = _validate_job_input(db, user, data)
    return tryon_repository.create_job(
        db,
        {
            "user_id": user.id,
            "user_photo_id": photo_id,
            "clothing_id": clothing.id,
            "selected_size": data.selected_size,
            "selected_color": data.selected_color,
            "status": "pending",
            "ai_provider": settings.ai_provider,
        },
    )


def process_job(job_id: uuid.UUID, db: Session | None = None) -> None:
    """
    Runs as a FastAPI BackgroundTask, after the 202 response has already
    been sent — so by default it opens its own DB session, since the
    request's session is long closed by the time this executes.

    Tests pass their own `db` explicitly (the same session their test
    transaction uses) — otherwise a real background task's independent
    session couldn't see a job that only exists inside the test's
    not-yet-committed transaction.
    """
    owns_session = db is None
    if db is None:
        db = SessionLocal()
    try:
        job = tryon_repository.get_job(db, job_id)
        if job is None:
            return

        tryon_repository.set_status(db, job, "processing")

        try:
            photo = photo_repository.get_by_id(db, job.user_photo_id)
            person_bytes = storage.read_bytes(photo.storage_key)
            provider = get_provider()
            generated = provider.generate_try_on(person_bytes, job.clothing, job.selected_color)
            result_key = storage.save_bytes("tryon_results", "jpg", generated.image_bytes)
            tryon_repository.create_result(db, job.id, result_key, generated.metadata)
            tryon_repository.set_status(db, job, "completed", completed_at=datetime.now(timezone.utc))
        except TryOnGenerationError as exc:
            tryon_repository.set_status(
                db, job, "failed", failure_reason=exc.message, completed_at=datetime.now(timezone.utc)
            )
        except Exception:
            logger.exception("Try-on job %s failed unexpectedly", job_id)
            tryon_repository.set_status(
                db,
                job,
                "failed",
                failure_reason="Something went wrong while generating your try-on.",
                completed_at=datetime.now(timezone.utc),
            )
    finally:
        if owns_session:
            db.close()


def _to_read_model(job: TryOnJob) -> TryOnJobRead:
    result = None
    if job.result:
        result = TryOnResultRead(
            # API-relative (no "/api" prefix) — the frontend's apiClient
            # base URL already includes /api, same as every other
            # endpoint it calls.
            image_url=f"/tryon/{job.id}/image",
            provider=job.ai_provider,
            created_at=job.result.created_at,
        )
    return TryOnJobRead(
        id=job.id,
        status=job.status,
        clothing_id=job.clothing_id,
        clothing_name=job.clothing.name,
        selected_size=job.selected_size,
        selected_color=job.selected_color,
        failure_reason=job.failure_reason,
        created_at=job.created_at,
        completed_at=job.completed_at,
        result=result,
    )


def get_job_for_user(db: Session, user: User, job_id: uuid.UUID) -> TryOnJobRead:
    job = tryon_repository.get_job(db, job_id)
    if job is None or job.user_id != user.id:
        raise NotFoundError("Try-on job not found.")
    return _to_read_model(job)


def get_result_image_bytes(db: Session, user: User, job_id: uuid.UUID) -> bytes:
    job = tryon_repository.get_job(db, job_id)
    if job is None or job.user_id != user.id or job.result is None:
        raise NotFoundError("Result not found.")
    return storage.read_bytes(job.result.storage_key)


def list_history(db: Session, user: User, page: int, page_size: int) -> PaginatedTryOnHistory:
    jobs, total = tryon_repository.list_jobs_for_user(db, user.id, page, page_size)
    return PaginatedTryOnHistory(
        items=[_to_read_model(job) for job in jobs], total=total, page=page, page_size=page_size
    )


def delete_job_for_user(db: Session, user: User, job_id: uuid.UUID) -> None:
    job = tryon_repository.get_job(db, job_id)
    if job is None or job.user_id != user.id:
        raise NotFoundError("Try-on job not found.")
    if job.result:
        storage.delete(job.result.storage_key)
    tryon_repository.delete_job(db, job)
