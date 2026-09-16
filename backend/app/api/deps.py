import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.crud.user import get_user_by_email
from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate the access token and return the corresponding active user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = decode_access_token(token)
    if email is None:
        logger.warning("Access token validation failed")
        raise credentials_exception

    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        logger.warning("Authentication failed for email=%s", email)
        raise credentials_exception
    logger.debug("Authenticated user email=%s", email)
    return user
