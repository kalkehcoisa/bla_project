import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.user import list_users
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[UserRead])
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the users visible to the authenticated user."""
    logger.info(
        "Listing users", extra={"user_id": getattr(current_user, "id", None)}
    )
    users = list_users(db)
    logger.info("Users listed", extra={"user_count": len(users)})
    return users


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    logger.debug(
        "Returning current user",
        extra={"user_id": getattr(current_user, "id", None)},
    )
    return current_user
