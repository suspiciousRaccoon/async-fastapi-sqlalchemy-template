from typing import Any

from fastapi import APIRouter

from app.database.dependencies import DbSession
from app.users.dependencies import CurrentActiveUser
from app.users.schema import (
    UserSchema,
    UserUpdate,
)
from app.users.service import UserService

router = APIRouter()


@router.get("/users/me/", response_model=UserSchema)
async def users_me(
    current_user: CurrentActiveUser,
) -> Any:
    return current_user


@router.patch("/users/{user_id}", response_model=UserSchema)
async def update_user(
    session: DbSession, user_id: int, user: UserUpdate, current_user: CurrentActiveUser
) -> Any:
    updated_user = await UserService(session).update_user_restricted(
        user_id=user_id, user_data=user.model_dump(), current_user=current_user
    )
    return updated_user


@router.delete("/users/{user_id}", response_model=UserSchema)
async def delete_user(
    user_id: int, session: DbSession, current_user: CurrentActiveUser
) -> Any:
    deleted_user = await UserService(session).delete_user(
        user_id=user_id, current_user=current_user
    )
    return deleted_user
