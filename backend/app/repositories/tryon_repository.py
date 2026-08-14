import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.tryon import TryOnJob, TryOnResult


def create_job(db: Session, fields: dict) -> TryOnJob:
    job = TryOnJob(**fields)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: uuid.UUID) -> TryOnJob | None:
    query = (
        select(TryOnJob)
        .options(selectinload(TryOnJob.result), selectinload(TryOnJob.clothing))
        .filter(TryOnJob.id == job_id)
    )
    return db.execute(query).scalar_one_or_none()


def list_jobs_for_user(
    db: Session, user_id: uuid.UUID, page: int, page_size: int
) -> tuple[list[TryOnJob], int]:
    query = (
        select(TryOnJob)
        .options(selectinload(TryOnJob.result), selectinload(TryOnJob.clothing))
        .filter(TryOnJob.user_id == user_id)
        .order_by(TryOnJob.created_at.desc())
    )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (
        db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    )
    return list(items), total


def set_status(
    db: Session,
    job: TryOnJob,
    status: str,
    failure_reason: str | None = None,
    completed_at: datetime | None = None,
) -> TryOnJob:
    job.status = status
    job.failure_reason = failure_reason
    job.completed_at = completed_at
    db.commit()
    db.refresh(job)
    return job


def create_result(
    db: Session, job_id: uuid.UUID, storage_key: str, metadata: dict
) -> TryOnResult:
    result = TryOnResult(try_on_job_id=job_id, storage_key=storage_key, result_metadata=metadata)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def delete_job(db: Session, job: TryOnJob) -> None:
    db.delete(job)
    db.commit()
