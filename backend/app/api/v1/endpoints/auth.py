import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user if the email is not already registered."""
    logger.info("Registration attempt for email=%s", user_in.email)
    if get_user_by_email(db, user_in.email):
        logger.warning("Registration rejected: email already registered, email=%s", user_in.email)
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, user_in)
    logger.info("User registered successfully, email=%s", user_in.email)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate a user and return a bearer access token."""
    logger.info("Login attempt for email=%s", form_data.username)
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning("Login failed for email=%s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.email)
    logger.info("Login succeeded for email=%s", form_data.username)
    return Token(access_token=access_token)
