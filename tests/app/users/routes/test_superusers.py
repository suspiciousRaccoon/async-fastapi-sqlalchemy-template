from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio.session import AsyncSession

from tests.factory import UserCreateSchemaFactory, UserFactory
from tests.utils.headers import create_authorization_headers_for_email


class TestSuperUserRoutes:
    @pytest.mark.parametrize("is_admin, expected_status", [(True, 200), (False, 403)])
    async def test_get_users(
        self,
        client: AsyncClient,
        session: AsyncGenerator[AsyncSession, None],
        is_admin: bool,
        expected_status: int,
    ) -> None:
        users = await UserFactory.create_batch_async(3)
        superuser = await UserFactory.create_async(is_admin=is_admin)

        headers = create_authorization_headers_for_email(email=superuser.email)

        response = await client.get("auth/users", headers=headers)
        assert response.status_code == expected_status
        if is_admin:
            assert len(response.json()) == len(users) + 1

    @pytest.mark.parametrize("is_admin, expected_status", [(True, 200), (False, 403)])
    async def test_get_user(
        self,
        client: AsyncClient,
        session: AsyncGenerator[AsyncSession, None],
        is_admin: bool,
        expected_status: int,
    ) -> None:
        user = await UserFactory.create_async()
        superuser = await UserFactory.create_async(is_admin=is_admin)

        headers = create_authorization_headers_for_email(email=superuser.email)

        response = await client.get(f"/auth/users/{user.id}", headers=headers)

        assert response.status_code == expected_status
        if is_admin:
            assert response.json() == {"id": user.id, "email": user.email}

    @pytest.mark.parametrize("is_admin, expected_status", [(True, 201), (False, 403)])
    async def test_create_user(
        self,
        client: AsyncClient,
        session: AsyncGenerator[AsyncSession, None],
        is_admin: bool,
        expected_status: int,
    ) -> None:
        superuser = await UserFactory.create_async(is_admin=is_admin)

        new_user_data = UserCreateSchemaFactory.build().model_dump()

        headers = create_authorization_headers_for_email(email=superuser.email)

        response = await client.post("/auth/users", json=new_user_data, headers=headers)

        assert response.status_code == expected_status

        if is_admin:
            created_user = response.json()

            assert created_user["email"] == new_user_data["email"]
            assert "id" in created_user
