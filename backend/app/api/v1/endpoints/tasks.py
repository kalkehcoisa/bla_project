from datetime import date

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


def _rate_limit(func):
    if limiter is None:
        return func
    return limiter.limit(settings.RATE_LIMIT_DEFAULT)(func)


def _notify_completed(task) -> None:
    """Fires the async notification, but never lets a broker outage break the request."""
    assignee_email = task.assignee.email if task.assignee else None
    try:
        notify_task_completed.delay(task.id, task.title, assignee_email)
    except Exception:  # pragma: no cover - broker not available in some environments
        pass


def _get_owned_task(db: Session, task_id: int, current_user: User):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id and task.assignee_id != current_user.id:
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
    items, total = list_tasks(
        db,
        page=page,
        page_size=page_size,
        status=status_filter,
        due_date=due_date,
        due_before=due_before,
        due_after=due_after,
    )
    return TaskPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskRead)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_task(db, task_id, current_user)


@router.patch("/{task_id}", response_model=TaskRead)
def edit_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_owned_task(db, task_id, current_user)
    updated = update_task(db, task, task_in)

    if updated.status == TaskStatus.DONE:
        _notify_completed(updated)

    return updated


@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_owned_task(db, task_id, current_user)
    updated = update_task(db, task, TaskUpdate(status=TaskStatus.DONE))
    _notify_completed(updated)
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_owned_task(db, task_id, current_user)
    delete_task(db, task)
