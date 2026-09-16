"""Database model for application users."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    """Represent a user who can own and be assigned tasks."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    owned_tasks = relationship(
        "Task", back_populates="owner", foreign_keys="Task.owner_id"
    )
    assigned_tasks = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assignee_id"
    )
