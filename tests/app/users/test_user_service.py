from copy import deepcopy
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.users.exceptions import (
    AuthorizationFailed,
    EmailTaken,
    InvalidCredentials,
    UserNotRegistered,
)
from app.users.service import UserService
from app.users.utils import get_password_hash, verify_password
from tests.factory import UserFactory

pytestmark = pytest.mark.anyio


class TestUserService:
    async def test_hash_password(self, session: AsyncSession) -> None:
        user_data = {"email": "test@example.com", "password": "StrongPass123!"}
        user_service = UserService(session)
        user_data_copy = deepcopy(user_data)  # hash_password modified the original dict
        hashed_user_data = user_service.hash_password(user_data=user_data_copy)
        assert not hashed_user_data.get("password", None)
        assert hashed_user_data["hashed_password"]
        assert verify_password(
            user_data["password"], hashed_user_data["hashed_password"]
        )

    async def test_get_user_by_id(self, session: AsyncSession) -> None:
        user = await UserFactory.create_async()
        user_service = UserService(session)
        fetched_user = await user_service.get_user(user_id=user.id)
        assert fetched_user
        assert fetched_user.id == user.id

    async def test_get_user_by_email(self, session: AsyncSession) -> None:
        user = await UserFactory.create_async()
        user_service = UserService(session)
        fetched_user = await user_service.get_user(user_email=user.email)
        assert fetched_user
        assert fetched_user.email == user.email

    async def test_get_users(self, session: AsyncSession) -> None:
        users = await UserFactory.create_batch_async(2)
        user_service = UserService(session)
        fetched_users = await user_service.get_users()
        assert len(fetched_users) == 2
        assert fetched_users[0].email == users[0].email
        assert fetched_users[1].email == users[1].email

    async def test_authenticate_user(self, session: AsyncSession) -> None:
        password = "StrongPass123!"
        hashed_password = get_password_hash(password)
        user = await UserFactory.create_async(hashed_password=hashed_password)
        user_service = UserService(session)
        authenticated_user = await user_service.authenticate(
            user.email, "StrongPass123!"
        )
        assert authenticated_user.id == user.id

    async def test_authenticate_invalid_password(self, session: AsyncSession) -> None:
        user = await UserFactory.create_async()
        user_service = UserService(session)
        with pytest.raises(InvalidCredentials):
            await user_service.authenticate(user.email, "WrongPass")

    async def test_create_user(self, session: AsyncSession) -> None:
        user_data = {"email": "test@example.com", "password": "StrongPass123!"}
        user = await UserService(session).create_user(user_data)
        assert user.email == user_data["email"]
        assert verify_password("StrongPass123!", user.hashed_password)

    async def test_create_user_duplicate_email(
        self,
        session: AsyncSession,
    ) -> None:
        await UserFactory.create_async(email="test@example.com")
        user_service = UserService(session)
        user_data = {"email": "test@example.com", "password": "StrongPass123!"}
        with pytest.raises(EmailTaken):
            await user_service.create_user(user_data)

    async def test_create_super_user(self, session: AsyncSession) -> None:
        user_data = {"email": "test@example.com", "password": "StrongPass123!"}
        user = await UserService(session).create_super_user(user_data)
        assert user.email == user_data["email"]
        assert verify_password("StrongPass123!", user.hashed_password)
        assert user.is_admin

    @patch("app.users.service.send_new_user_email")
    async def test_register_user_sends_activation_email(
        self, mock_send_email: MagicMock, session: AsyncSession
    ) -> None:
        user_service = UserService(session)

        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
        }

        new_user = await user_service.register_user(user_data=user_data)

        assert new_user.is_active is False
        mock_send_email.delay.assert_called_once_with(email={"email": new_user.email})

    async def test_get_user_not_found(self, session: AsyncSession) -> None:
        user_service = UserService(session)
        with pytest.raises(UserNotRegistered):
            await user_service.get_user(user_id=99999)

    async def test_update_user(self, session: AsyncSession) -> None:
        user = await UserFactory.create_async()
        user_service = UserService(session)
        updated_user = await user_service.update_user(
            user.id, {"email": "new@example.com"}
        )
        assert updated_user.email == "new@example.com"

    async def test_update_user_restricted_self(self, session: AsyncSession) -> None:
        user = await UserFactory.create_async()
        user_service = UserService(session)
        updated_user = await user_service.update_user_restricted(
            user.id, {"email": "restricted-self@example.com"}, user
        )
        assert updated_user
        assert updated_user.email == "restricted-self@example.com"

    async def test_update_user_restricted_admin(self, session: AsyncSession) -> None:
        user = await UserFactory.create_async()
        admin = await UserFactory.create_async(is_admin=True)
        user_service = UserService(session)

        updated_user = await user_service.update_user_restricted(
            user.id, {"email": "restricted-admin@example.com"}, admin
        )
        assert updated_user
        assert updated_user.email == "restricted-admin@example.com"

    async def test_update_user_restricted_unauthorized(
        self, session: AsyncSession
    ) -> None:
        user = await UserFactory.create_async(is_admin=False)
        other_user = await UserFactory.create_async(is_admin=False)
        user_service = UserService(session)
        with pytest.raises(AuthorizationFailed):
            await user_service.update_user_restricted(
                user.id, {"email": "restricted-other@example.com"}, other_user
            )

    async def test_activate_user(self, session: AsyncSession) -> None:
        user = await UserFactory.create_async(is_active=False)
        user_service = UserService(session)

        activated_user = await user_service.activate_user(email=user.email)
        assert activated_user
        assert activated_user.is_active is True

    async def test_deactivate_user(self, session: AsyncSession) -> None:
        admin = await UserFactory.create_async(is_admin=True)
        user = await UserFactory.create_async(is_active=True)
        user_service = UserService(session)

        deactivated_user = await user_service.deactivate_user(
            user_id=user.id, current_user=admin
        )
        assert deactivated_user
        assert deactivated_user.is_active is False

    async def test_deactivate_user_unauthorized(self, session: AsyncSession) -> None:
        user = await UserFactory.create_async(is_active=True)
        unauthorized_user = await UserFactory.create_async(is_admin=False)
        user_service = UserService(session)

        with pytest.raises(AuthorizationFailed):
            await user_service.deactivate_user(
                user_id=user.id, current_user=unauthorized_user
            )

    async def test_delete_user(self, session: AsyncSession) -> None:
        admin = await UserFactory.create_async(is_admin=True)
        user = await UserFactory.create_async(is_active=True)
        user_service = UserService(session)

        deleted_user = await user_service.delete_user(
            user_id=user.id, current_user=admin
        )
        assert deleted_user
        assert deleted_user.is_active is False

    @patch("app.users.service.send_reset_password_email")
    async def test_start_password_reset_active_user(
        self, mock_send_email: MagicMock, session: AsyncSession
    ) -> None:
        user = await UserFactory.create_async()
        user_service = UserService(session)

        await user_service.start_password_reset(email=user.email)

        mock_send_email.delay.assert_called_once_with(email={"email": user.email})

    @patch("app.users.service.send_reset_password_email")
    async def test_start_password_reset_inactive_user(
        self, mock_send_email: MagicMock, session: AsyncSession
    ) -> None:
        user = await UserFactory.create_async(is_active=False)
        user_service = UserService(session)

        await user_service.start_password_reset(email=user.email)

        mock_send_email.delay.assert_not_called()

    @patch("app.users.service.send_reset_password_email")
    async def test_start_password_reset_nonexistent_user(
        self, mock_send_email: MagicMock, session: AsyncSession
    ) -> None:
        user_service = UserService(session)

        await user_service.start_password_reset(email="nonexistent@example.com")

        mock_send_email.delay.assert_not_called()

    async def test_finish_password_reset_updates_password(
        self, session: AsyncSession
    ) -> None:
        """Test that finishing a password reset updates the user's password"""
        user = await UserFactory.create_async()
        user_service = UserService(session)

        new_password = "NewSecurePass123!"
        await user_service.finish_password_reset(
            email=user.email, password=new_password
        )

        updated_user = await user_service.get_user(user_email=user.email)
        assert updated_user
        assert verify_password(new_password, updated_user.hashed_password)
