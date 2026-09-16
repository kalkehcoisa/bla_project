"""SQLAlchemy models for task management."""

import enum
import logging
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

logger = logging.getLogger(__name__)


class TaskStatus(str, enum.Enum):
    """Lifecycle states available for a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    """A task owned by a user and optionally assigned to another user."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, index=True
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner = relationship("User", back_populates="owned_tasks", foreign_keys=[owner_id])
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
