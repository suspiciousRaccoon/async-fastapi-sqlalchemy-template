from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.database.dependencies import DbSession

from .exceptions import AuthorizationFailed, InactiveUser, InvalidCredentials
from .models import User
from .schema import TokenData
from .service import UserService
from .utils import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token/")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(session: DbSession, token: TokenDep) -> User | None:
    # validates the token and the email
    try:
        payload = decode_jwt(token)
        email: str = payload.get("sub")
        if email is None:
            raise InvalidCredentials
        token_data = TokenData(email=email)
    except jwt.InvalidTokenError:
        raise InvalidCredentials

    return await UserService(session).get_user(user_email=token_data.email)


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_user(
    current_user: CurrentUser,
) -> User | None:
    if not current_user.is_active:
        raise InactiveUser
    return current_user


CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]


async def get_current_superuser(current_user: CurrentActiveUser) -> User | None:
    if not current_user.is_admin:
        raise AuthorizationFailed
    return current_user


CurrentSuperUser = Annotated[User, Depends(get_current_superuser)]
