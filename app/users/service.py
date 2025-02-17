from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.users.tasks import send_new_user_email, send_reset_password_email

from .exceptions import (
    AuthorizationFailed,
    EmailTaken,
    InvalidCredentials,
    UserNotRegistered,
)
from .models import User
from .repository import UserRepository
from .utils import get_password_hash, verify_password


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def hash_password(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """
        Removes the `password` field and value from `user_data` if available, then
        adds a new `hashed_password` field with a hashed password


        Args:
            user_data (dict): user data with raw `password` field

        Returns:
            dict[str, Any]: user data with `hashed_password` field and a hashed password
        """
        password = user_data.pop("password", None)
        if password:
            user_data["hashed_password"] = get_password_hash(password=password)
        return user_data

    async def get_user(
        self,
        user_id: int | None = None,
        user_email: str | None = None,
        raise_exception: bool = True,
    ) -> User | None:
        """Generic method to fetch a user

        Args:
            user_id (int | None, optional): Primary key of a user. Defaults to None.
            user_email (str | None, optional): Email of a user. Defaults to None.
            raise_exception (bool, optional): If True, will raise an exception if the user is not found. Defaults to True.

        Raises:
            ValueError: Raised if a user identifier is not provided.
            UserNotRegistered: Raised if a user is not found and `raise_exception` is true.

        Returns:
            User | None: a User or None if not found.
        """

        if not any([user_id, user_email]):
            raise ValueError(
                "At least one identifier (user_id, user_email) must be provided."
            )
        filters: dict[str, str | int] = {}
        if user_id:
            filters["id"] = user_id
        if user_email:
            filters["email"] = user_email

        user = await UserRepository(self.session).get_by_attributes(**filters)
        if not user and raise_exception:
            raise UserNotRegistered
        return user

    async def get_users(self) -> Sequence[User]:
        users = await UserRepository(self.session).get_all()

        return users

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.get_user(user_email=email, raise_exception=False)
        if not user:
            raise InvalidCredentials
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentials
        return user

    async def create_user(self, user_data: dict[str, Any]) -> User:
        try:
            await self.get_user(user_email=user_data.get("email"))
            raise EmailTaken
        except UserNotRegistered:
            new_user = await UserRepository(self.session).create(
                data=self.hash_password(user_data=user_data)
            )

        return new_user

    async def create_super_user(self, user_data: dict[str, Any]) -> User:
        user_data["is_admin"] = True
        return await self.create_user(user_data=user_data)

    async def register_user(self, user_data: dict[str, Any]) -> User:
        """Like create user but sends an activation email to activate the user

        Args:
            user_data (dict): data for the user

        Returns:
            User: unactivated user
        """
        user_data["is_active"] = False
        new_user = await self.create_user(user_data=user_data)

        send_new_user_email.delay(email={"email": new_user.email})

        return new_user

    async def update_user(self, user_id: int, user_data: dict[str, Any]) -> User:
        """Updates an existing user.

        Args:
            user (User): The user instance to update.
            user_data (dict[str, Any]): New data for the user.

        Returns:
            User: The updated user.
        """

        return await UserRepository(self.session).update(
            model_id=user_id, data=self.hash_password(user_data=user_data)
        )

    async def update_user_restricted(
        self, user_id: int, user_data: dict[str, Any], current_user: User
    ) -> User | None:
        """Updates a user with authorization checks.

        Args:
            user_id (int): ID of the user to be updated.
            user_data (dict[str, Any]): New data for the user.
            current_user (User): The user making the request.

        Raises:
            AuthorizationFailed: If the current user isn't authorized.

        Returns:
            User: The updated user.
        """
        user = await self.get_user(user_id=user_id)

        if user:
            if not (current_user.is_admin or user.email == current_user.email):
                raise AuthorizationFailed
            user = await self.update_user(user_id=user.id, user_data=user_data)

        return user

    async def activate_user(self, email: str) -> User | None:
        """
        Activates a user

        Args:
            email (str): email of the user to be activated
        """
        inactive_user = await self.get_user(user_email=email)
        if inactive_user:
            active_user = await self.update_user(
                user_id=inactive_user.id, user_data={"is_active": True}
            )

            return active_user
        return None

    async def deactivate_user(self, user_id: int, current_user: User) -> User | None:
        """
        Deactivates a user

        Args:
            user_id (int): id of the user to be deactivated
            current_user (User): current user

        Raises:
            AuthorizationFailed: raised if the current user isn't allowed to deactive the user with user_id

        Returns:
            User: the deactivated user
        """
        inactive_user = await self.update_user_restricted(
            user_id=user_id, user_data={"is_active": False}, current_user=current_user
        )
        return inactive_user

    async def delete_user(self, user_id: int, current_user: User) -> User | None:
        return await self.deactivate_user(user_id=user_id, current_user=current_user)

    async def start_password_reset(self, email: str) -> None:
        user = await self.get_user(user_email=email, raise_exception=False)

        if user and user.is_active:
            send_reset_password_email.delay(email={"email": email})

    async def finish_password_reset(self, email: str, password: str) -> None:
        """

        Args:
            email (str): _description_
            password (str): _description_
        """

        user = await self.get_user(user_email=email, raise_exception=False)

        if user:
            user_data = self.hash_password({"password": password})
            await self.update_user(user_id=user.id, user_data=user_data)
