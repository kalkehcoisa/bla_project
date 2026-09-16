from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    assignee_id: int | None = None


class TaskCreate(TaskBase):
    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    assignee_id: int | None = None
    status: TaskStatus | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TaskStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime


class TaskPage(BaseModel):
    items: list[TaskRead]
    total: int
    page: int
    page_size: int
