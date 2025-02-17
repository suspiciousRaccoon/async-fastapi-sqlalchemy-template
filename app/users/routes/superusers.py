from typing import Any

from fastapi import APIRouter

from app.database.dependencies import DbSession
from app.users.dependencies import CurrentSuperUser
from app.users.schema import (
    UserCreate,
    UserSchema,
)
from app.users.service import UserService

router = APIRouter()


@router.get("/users", response_model=list[UserSchema])
async def get_users(session: DbSession, current_superuser: CurrentSuperUser) -> Any:
    users = await UserService(session).get_users()
    return users


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int, session: DbSession, current_superuser: CurrentSuperUser
) -> Any:
    user = await UserService(session).get_user(user_id=user_id)
    return user


@router.post("/users", response_model=UserSchema, status_code=201)
async def create_user(
    session: DbSession, user: UserCreate, current_superuser: CurrentSuperUser
) -> Any:
    new_user = await UserService(session).create_user(user_data=user.model_dump())

    return new_user
