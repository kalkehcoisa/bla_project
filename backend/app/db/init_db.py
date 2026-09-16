"""Database schema creation and demo-data seeding utilities."""

import logging

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.task import Task, TaskStatus
from app.models.user import User


logger = logging.getLogger(__name__)


def init_db() -> None:
    """Create database tables and seed initial data when needed."""
    logger.info("Initializing database")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed(db)
    finally:
        db.close()
        logger.info("Database initialization complete")


def _seed(db: Session) -> None:
    """Insert demo users and tasks if the database is empty."""
    if db.query(User).count() > 0:
        logger.info("Skipping demo-data seeding; users already exist")
        return

    demo_user = User(
        email="demo@example.com",
        full_name="Demo User",
        hashed_password=hash_password("demo1234"),
    )
    second_user = User(
        email="alice@example.com",
        full_name="Alice Example",
        hashed_password=hash_password("alice1234"),
    )
    db.add_all([demo_user, second_user])
    db.commit()
    db.refresh(demo_user)
    db.refresh(second_user)

    demo_tasks = [
        Task(
            title="Set up project repository",
            description="Initialize the repo and CI pipeline",
            status=TaskStatus.DONE,
            owner_id=demo_user.id,
            assignee_id=demo_user.id,
        ),
        Task(
            title="Design database schema",
            description="Model users and tasks",
            status=TaskStatus.IN_PROGRESS,
            owner_id=demo_user.id,
            assignee_id=second_user.id,
        ),
        Task(
            title="Write API tests",
            description="Cover auth and task endpoints",
            status=TaskStatus.PENDING,
            owner_id=second_user.id,
            assignee_id=demo_user.id,
        ),
    ]
    db.add_all(demo_tasks)
    db.commit()
    logger.info("Seeded demo users and tasks")
