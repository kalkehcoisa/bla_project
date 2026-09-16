import logging

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str) -> User | None:
    """Return the user with the specified email address, if found."""
    logger.debug("Looking up user by email")
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> User | None:
    """Return the user with the specified ID, if found."""
    logger.debug("Looking up user by ID: %s", user_id)
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session) -> list[User]:
    """Return all users."""
    logger.debug("Listing users")
    return db.query(User).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create, persist, and return a user from the supplied input data."""
    logger.info("Creating user")
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Created user with ID: %s", user.id)
    return user
