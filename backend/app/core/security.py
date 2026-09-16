from datetime import datetime, timedelta, timezone
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash a plaintext password using the configured password context."""
    logger.debug("Hashing password")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a previously generated hash."""
    logger.debug("Verifying password hash")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token for a subject."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug("Created access token expiring at %s", expire.isoformat())
    return token


def decode_access_token(token: str) -> str | None:
    """Decode an access token and return its subject, or None if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject = payload.get("sub")
        logger.debug("Decoded access token successfully")
        return subject
    except JWTError:
        logger.warning("Failed to decode access token")
        return None
