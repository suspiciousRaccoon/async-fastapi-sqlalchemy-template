from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.database.dependencies import DbSession
from app.email.utils import decode_email_token
from app.users.exceptions import InvalidToken
from app.users.schema import (
    AuthUser,
    PasswordModel,
    Token,
    UserCreate,
    UserResetPassword,
    UserSchema,
)
from app.users.service import UserService
from app.users.utils import create_access_token, generate_random_password

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(
    session: DbSession,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user_data = AuthUser(password=form_data.password, email=form_data.username)

    user = await UserService(session).authenticate(user_data.email, user_data.password)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/generate-password", response_model=PasswordModel)
async def generate_password() -> PasswordModel:
    password = generate_random_password()
    return PasswordModel(password=password)


@router.post("/users/register")
async def register_user(session: DbSession, user: UserCreate) -> Any:
    """
    Unlike `create_user`, `register_user` sends a confirmation email to activate the account
    """
    await UserService(session).register_user(user_data=user.model_dump())
    return {
        "description": "A link to activate your account has been emailed to the address provided."
    }


@router.get("/users/verify", response_model=UserSchema)
async def verify_user(session: DbSession, token: Annotated[str, Query()] = "") -> Any:
    """
    Verifies the user with the `token` query param
    """
    email_token = decode_email_token(token)
    if not email_token:
        raise InvalidToken

    email = email_token.get("sub", "")
    user = await UserService(session).activate_user(email=email)

    return user


@router.post("/users/{user_email}/password-recovery")
async def recover_password(session: DbSession, user_email: str) -> Any:
    await UserService(session).start_password_reset(email=user_email)
    return {
        "description": "If that email address is in our database, we will send you an email to reset your password."
    }


@router.post("/users/reset_password")
async def reset_password(session: DbSession, password_data: UserResetPassword) -> Any:
    token = decode_email_token(password_data.token)
    if not token:
        raise InvalidToken
    email = token["sub"]
    password = password_data.password
    await UserService(session).finish_password_reset(email=email, password=password)
    return {"description": "Password updated succesfully."}
