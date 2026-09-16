"""Task-management API endpoints."""

from datetime import date
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.crud.task import create_task, delete_task, get_task, list_tasks, update_task
from app.db.session import get_db
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskPage, TaskRead, TaskUpdate
from app.tasks.celery_tasks import notify_task_completed

try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
except ImportError:  # pragma: no cover
    limiter = None

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


def _rate_limit(func):
    """Apply the configured rate limit when rate limiting is available."""
    if limiter is None:
        logger.debug("Rate limiting is unavailable; using endpoint without rate limiting")
        return func
    logger.debug("Applying rate limit to endpoint: %s", getattr(func, "__name__", repr(func)))
    return limiter.limit(settings.RATE_LIMIT_DEFAULT)(func)


def _notify_completed(task) -> None:
    """Queue an asynchronous completion notification without failing the request."""
    assignee_email = task.assignee.email if task.assignee else None
    logger.info("Queueing task completion notification: task_id=%s", task.id)
    try:
        notify_task_completed.delay(task.id, task.title, assignee_email)
        logger.debug("Task completion notification queued: task_id=%s", task.id)
    except Exception as exc:  # pragma: no cover - broker not available in some environments
        logger.exception(
            "Failed to enqueue task completion notification: "
            "task_id=%s, task_title=%r, assignee_email=%r, "
            "exception_type=%s, exception=%r",
            task.id,
            task.title,
            assignee_email,
            type(exc).__name__,
            exc,
            exc_info=True,
        )
        pass


def _get_owned_task(db: Session, task_id: int, user_id: int):
    """Return a task accessible to the user or raise an appropriate HTTP error."""
    logger.debug("Looking up task: task_id=%s, user_id=%s", task_id, user_id)
    task = get_task(db, task_id)
    if task is None:
        logger.warning("Task not found: task_id=%s, user_id=%s", task_id, user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != user_id and task.assignee_id != user_id:
        logger.warning("Unauthorized task access: task_id=%s, user_id=%s", task_id, user_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return task


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
@_rate_limit
def create_new_task(
    request: Request,
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a task owned by the authenticated user."""
    logger.info("Creating task: user_id=%s", current_user.id)
    return create_task(db, task_in, owner_id=current_user.id)


@router.get("/", response_model=TaskPage)
def read_tasks(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    due_date: date | None = Query(default=None),
    due_before: date | None = Query(default=None),
    due_after: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the authenticated user's accessible tasks with optional filters."""
    logger.debug(
        "Listing tasks: user_id=%s, page=%s, page_size=%s, status=%s, due_date=%s, due_before=%s, due_after=%s",
        current_user.id,
        page,
        page_size,
        status_filter,
        due_date,
        due_before,
        due_after,
    )
    items, total = list_tasks(
        db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status_filter,
        due_date=due_date,
        due_before=due_before,
        due_after=due_after,
    )
    logger.debug("Listed tasks: user_id=%s, total=%s, returned=%s", current_user.id, total, len(items))
    return TaskPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskRead)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single task accessible to the authenticated user."""
    logger.debug("Reading task: task_id=%s, user_id=%s", task_id, current_user.id)
    return _get_owned_task(db, task_id, current_user.id)


@router.patch("/{task_id}", response_model=TaskRead)
def edit_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an accessible task and notify when it is completed."""
    logger.info("Updating task: task_id=%s, user_id=%s", task_id, current_user.id)
    task = _get_owned_task(db, task_id, current_user.id)
    updated = update_task(db, task, task_in)

    if updated.status == TaskStatus.DONE:
        _notify_completed(updated)

    logger.info("Task updated: task_id=%s, status=%s", task_id, updated.status)
    return updated


@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an accessible task as completed and queue a notification."""
    logger.info("Completing task: task_id=%s, user_id=%s", task_id, current_user.id)
    task = _get_owned_task(db, task_id, current_user.id)
    updated = update_task(db, task, TaskUpdate(status=TaskStatus.DONE))
    _notify_completed(updated)
    logger.info("Task completed: task_id=%s", task_id)
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an accessible task."""
    logger.info("Deleting task: task_id=%s, user_id=%s", task_id, current_user.id)
    task = _get_owned_task(db, task_id, current_user.id)
    delete_task(db, task)
    logger.info("Task deleted: task_id=%s", task_id)
