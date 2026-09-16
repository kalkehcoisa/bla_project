"""Pydantic schemas used by the task API."""

import logging
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus

logger = logging.getLogger(__name__)


class TaskBase(BaseModel):
    """Common task fields shared by create and read schemas."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    assignee_id: int | None = None


class TaskCreate(TaskBase):
    """Request body for creating a task."""

    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    """Request body for partially updating a task."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    assignee_id: int | None = None
    status: TaskStatus | None = None


class TaskRead(TaskBase):
    """Task data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TaskStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime


class TaskPage(BaseModel):
    """Paginated task response."""

    items: list[TaskRead]
    total: int
    page: int
    page_size: int

    def model_post_init(self, __context: object) -> None:
        """Log pagination metadata after constructing the response."""
        logger.debug(
            "Created task page: page=%s page_size=%s total=%s items=%s",
            self.page,
            self.page_size,
            self.total,
            len(self.items),
        )
