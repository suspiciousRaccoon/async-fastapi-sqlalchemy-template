from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.email.utils import generate_email_token
from app.users.service import UserService
from app.users.utils import get_password_hash, verify_password
from tests.factory import UserCreateSchemaFactory, UserFactory

pytestmark = pytest.mark.anyio


class TestAuthRoutes:
    async def test_login_success(self, client: AsyncClient) -> None:
        password = "StrongPass123!"
        hashed_password = get_password_hash(password)
        user = await UserFactory.create_async(hashed_password=hashed_password)
        data = {"username": user.email, "password": password}
        response = await client.post("auth/token", data=data)

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()

    async def test_login_failure(self, client: AsyncClient) -> None:
        data = {"username": "invalid@example.com", "password": "WrongPass"}

        response = await client.post("auth/token", data=data)

        assert response.status_code == 403

    async def test_generate_password(self, client: AsyncClient) -> None:
        response = await client.get("auth/generate-password")

        assert response.status_code == 200
        assert "password" in response.json()

    @patch("app.users.service.send_new_user_email")
    async def test_register_user(
        self,
        mock_send_email: MagicMock,
        client: AsyncClient,
    ) -> None:
        """Test user registration sends activation email"""

        user_data = UserCreateSchemaFactory.build().model_dump()

        response = await client.post("auth/users/register", json=user_data)

        assert response.status_code == 200
        mock_send_email.delay.assert_called_once()

    @patch("app.users.service.send_reset_password_email")
    async def test_recover_password(
        self,
        mock_send_email: MagicMock,
        client: AsyncClient,
    ) -> None:
        user = await UserFactory.create_async()
        response = await client.post(f"auth/users/{user.email}/password-recovery")

        assert response.status_code == 200
        mock_send_email.delay.assert_called_once_with(email={"email": user.email})

    async def test_recover_password_nonexistent_user(self, client: AsyncClient) -> None:
        response = await client.post(
            "auth/users/nonexistent@example.com/password-recovery"
        )

        assert response.status_code == 200

    async def test_reset_password_success(
        self, client: AsyncClient, session: AsyncSession
    ) -> None:
        user = await UserFactory.create_async()
        new_password = "NewSecurePass123!"
        token = generate_email_token(user.email)

        response = await client.post(
            "auth/users/reset_password",
            json={"token": token, "password": new_password},
        )

        assert response.status_code == 200
        updated_user = await UserService(session).get_user(user_email=user.email)
        assert updated_user
        assert verify_password(new_password, updated_user.hashed_password)

    async def test_reset_password_invalid_token(self, client: AsyncClient) -> None:
        """Test reset password fails with invalid token"""
        response = await client.post(
            "auth/users/reset_password",
            json={"token": "invalid_token", "password": "NewSecurePass123!"},
        )

        assert response.status_code == 401  # Invalid token response
