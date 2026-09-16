from datetime import date
import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


def create_task(db: Session, task_in: TaskCreate, owner_id: int) -> Task:
    """Create and persist a task for the specified owner."""
    logger.info("Creating task for owner_id=%s", owner_id)
    task = Task(**task_in.model_dump(), owner_id=owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info("Created task id=%s for owner_id=%s", task.id, owner_id)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    """Retrieve a task by its identifier, if it exists."""
    logger.debug("Fetching task id=%s", task_id)
    return db.query(Task).filter(Task.id == task_id).first()


def list_tasks(
    db: Session,
    user_id: int,
    *,
    page: int = 1,
    page_size: int = 10,
    status: TaskStatus | None = None,
    due_date: date | None = None,
    due_before: date | None = None,
    due_after: date | None = None,
) -> tuple[list[Task], int]:
    """Return a paginated list of a user's tasks and the total count."""
    logger.debug(
        "Listing tasks for user_id=%s, page=%s, page_size=%s, status=%s, "
        "due_date=%s, due_before=%s, due_after=%s",
        user_id,
        page,
        page_size,
        status,
        due_date,
        due_before,
        due_after,
    )
    query = db.query(Task).filter(Task.owner_id == user_id and Task.assignee_id == user_id)

    if status is not None:
        query = query.filter(Task.status == status)
    if due_date is not None:
        query = query.filter(Task.due_date == due_date)
    if due_before is not None:
        query = query.filter(Task.due_date <= due_before)
    if due_after is not None:
        query = query.filter(Task.due_date >= due_after)

    total = query.with_entities(func.count(Task.id)).scalar() or 0
    items = (
        query.order_by(Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    logger.debug("Found %s tasks for user_id=%s (total=%s)", len(items), user_id, total)
    return items, total


def update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
    """Apply provided changes to a task and persist the updated task."""
    update_data = task_in.model_dump(exclude_unset=True)
    logger.info("Updating task id=%s with fields=%s", task.id, list(update_data))
    for field, value in update_data.items():
        setattr(task, field, value)
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info("Updated task id=%s", task.id)
    return task


def delete_task(db: Session, task: Task) -> None:
    """Delete a task and commit the deletion."""
    logger.info("Deleting task id=%s", task.id)
    db.delete(task)
    db.commit()
    logger.info("Deleted task id=%s", task.id)
