from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factory import UserFactory
from tests.utils.headers import create_authorization_headers_for_email


class TestUserRoutes:
    async def test_users_me(self, client: AsyncClient, session: AsyncSession) -> None:
        user = await UserFactory.create_async()
        headers = create_authorization_headers_for_email(email=user.email)

        response = await client.get("/auth/users/me/", headers=headers)

        assert response.status_code == 200
        assert response.json() == {"id": user.id, "email": user.email}

    @pytest.mark.parametrize(
        "is_admin, target, expected_status",
        [
            (False, "self", 200),  # Regular users can update their own profile
            (False, "other", 403),  # Regular users cannot update others
            (True, "other", 200),  # Superusers can update anyone
        ],
    )
    async def test_update_user(
        self,
        client: AsyncClient,
        session: AsyncSession,
        is_admin: bool,
        target: str,
        expected_status: int,
    ) -> None:
        request_user = await UserFactory.create_async(is_admin=is_admin)
        target_user = (
            request_user if target == "self" else await UserFactory.create_async()
        )

        update_data = {"email": "updated@example.com"}
        headers = create_authorization_headers_for_email(email=request_user.email)

        response = await client.patch(
            f"/auth/users/{target_user.id}", json=update_data, headers=headers
        )

        assert response.status_code == expected_status

        if expected_status == 200:
            data = response.json()
            assert data["email"] == update_data["email"]
            assert data["id"] == target_user.id

    @pytest.mark.parametrize(
        "is_admin, target, expected_status",
        [
            (False, "self", 200),  # Regular users can delete their own account
            (False, "other", 403),  # Regular users cannot delete others
            (True, "other", 200),  # Superusers can delete anyone
        ],
    )
    async def test_delete_user(
        self,
        client: AsyncClient,
        session: AsyncSession,
        is_admin: bool,
        target: str,
        expected_status: int,
    ) -> None:
        """Test that users can only delete their own account unless they are superusers."""
        request_user = await UserFactory.create_async(is_admin=is_admin)
        target_user_obj = (
            request_user if target == "self" else await UserFactory.create_async()
        )

        headers = create_authorization_headers_for_email(email=request_user.email)

        response = await client.delete(
            f"/auth/users/{target_user_obj.id}", headers=headers
        )

        assert response.status_code == expected_status
