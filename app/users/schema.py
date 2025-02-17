import re

from pydantic import AliasChoices, EmailStr, Field, field_validator

from app.config import settings
from app.schema import DefaultModel
from app.users.utils import STRONG_PASSWORD_PATTERN


class PasswordModel(DefaultModel):
    password: str = Field(min_length=8, max_length=64)

    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if (
            not re.match(STRONG_PASSWORD_PATTERN, password)
            and settings.ENVIRONMENT != "local"
        ):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or "
                "special symbol"
            )

        return password


class AuthUser(PasswordModel):
    email: EmailStr = Field(validation_alias=AliasChoices("email", "username", "sub"))


class UserSchema(DefaultModel):
    id: int
    email: EmailStr


class UserCreate(AuthUser): ...


class UserUpdate(DefaultModel):
    email: EmailStr = Field(validation_alias=AliasChoices("email", "username", "sub"))


class UserResetPassword(PasswordModel):
    token: str


class UserRegister(AuthUser): ...


class TokenData(DefaultModel):
    email: EmailStr | None = None


class Token(DefaultModel):
    access_token: str
    token_type: str
