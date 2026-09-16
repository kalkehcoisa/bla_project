"""Schemas used for authentication tokens."""

from pydantic import BaseModel


class Token(BaseModel):
    """Represent an access token returned by the authentication API."""

    access_token: str
    token_type: str = "bearer"
