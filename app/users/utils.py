import re
import secrets
import string
from datetime import timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.config import settings
from app.utils import get_current_time

from .exceptions import PasswordGenerationError

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")

PASSWORD_HASH = PasswordHash((Argon2Hasher(),))

ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    return PASSWORD_HASH.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PASSWORD_HASH.verify(plain_password, hashed_password)


def decode_jwt(token: str) -> Any:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = get_current_time() + expires_delta
    else:
        expire = get_current_time() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_random_password(max_attempts: int = 100) -> str:
    """
    Generates a random password that matches the strong password pattern.
    Attempts a maximum number of times to avoid infinite loops.

    Args:
        max_attempts (int): Maximum number of attempts to generate a valid password.

    Raises:
        PasswordGenerationError: Raised if a password isn't able to be generated within `max_attempts`

    Returns:
        str: A strong password matching the specified pattern
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    for _ in range(max_attempts):
        password = "".join(secrets.choice(alphabet) for _ in range(20))
        if STRONG_PASSWORD_PATTERN.match(password):
            return password
    raise PasswordGenerationError
