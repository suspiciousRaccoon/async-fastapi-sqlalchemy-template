from datetime import timedelta
from typing import Any

import jwt
from pydantic import EmailStr

from app.config import settings
from app.schema import DefaultModel
from app.utils import get_current_time

ALGORITHM = "HS256"


class Email(DefaultModel):
    email: EmailStr


class EmailStatus(DefaultModel):
    email: EmailStr
    sent: bool
    error: str | None = None


def generate_email_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = get_current_time()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def decode_email_token(token: str) -> Any:
    try:
        # automatically validates "exp" and "nbf"
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None
