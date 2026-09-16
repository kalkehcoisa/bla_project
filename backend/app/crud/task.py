from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, task_in: TaskCreate, owner_id: int) -> Task:
    task = Task(**task_in.model_dump(), owner_id=owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def list_tasks(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    status: TaskStatus | None = None,
    due_date: date | None = None,
    due_before: date | None = None,
    due_after: date | None = None,
) -> tuple[list[Task], int]:
    query = db.query(Task)

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
    return items, total


def update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
