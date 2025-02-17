from typing import AsyncGenerator, Generator, Literal, Never

import alembic
import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, AsyncTransaction

from app.config import settings
from app.database.dependencies import get_session
from app.main import app
from tests.database import async_engine
from tests.factory import UserFactory

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


# Apply migrations at the beginning of the testing session and downgrade at the end
@pytest.fixture(scope="session")
def apply_migrations() -> Generator[None, None, None]:
    config = Config("alembic.ini")
    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture
async def connection(
    anyio_backend: Literal["asyncio"], apply_migrations: Never
) -> AsyncGenerator[AsyncConnection, None]:
    async with async_engine.connect() as connection:
        yield connection


@pytest.fixture()
async def transaction(
    connection: AsyncConnection,
) -> AsyncGenerator[AsyncTransaction, None]:
    async with connection.begin() as transaction:
        yield transaction


# Use this fixture to get SQLAlchemy's AsyncSession.
# All changes that occur in a test function are rolled back
# after function exits, even if session.commit() is called
# in inner functions
@pytest.fixture()
async def session(
    connection: AsyncConnection, transaction: AsyncTransaction
) -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    yield async_session

    await async_session.close()
    await transaction.rollback()


@pytest.fixture(autouse=True)
async def set_factory_session(session: AsyncSession) -> None:
    UserFactory.__async_session__ = session


@pytest.fixture()
async def client(
    session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=f"{settings.SERVER_HOST}/"
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()
