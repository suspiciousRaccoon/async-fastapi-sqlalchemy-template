from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column

from app.database.core import Base
from app.repository import BaseRepository

# Define an in-memory SQLite test database
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

pytestmark = pytest.mark.anyio


class Post(Base):
    __tablename__ = "post"

    name: Mapped[str] = mapped_column(nullable=False)


class PostRepository(BaseRepository[Post]):
    model = Post


@pytest.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(
    setup_database: AsyncGenerator[None, None],
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def repository(session: AsyncSession) -> PostRepository:
    return PostRepository(session)


async def test_create(repository: PostRepository) -> None:
    data = {"name": "Test Name"}
    instance = await repository.create(data)
    assert instance.id is not None
    assert instance.name == data["name"]


async def test_get(repository: PostRepository) -> None:
    instance = await repository.create({"name": "Retrieve Test"})
    fetched = await repository.get(int(instance.id))
    assert fetched is not None
    assert fetched.id == instance.id
    assert fetched.name == instance.name


async def test_get_all(repository: PostRepository) -> None:
    post1 = await repository.create({"name": "Post 1"})
    post2 = await repository.create({"name": "Post 2"})
    results = await repository.get_all()
    assert len(results) >= 2
    assert results[0].name == post1.name
    assert results[0].id == post1.id
    assert results[1].name == post2.name
    assert results[1].id == post2.id


async def test_get_by_attributes(repository: PostRepository) -> None:
    """Test filtering by attribute."""
    instance = await repository.create({"name": "Unique Name"})
    fetched = await repository.get_by_attributes(name="Unique Name")
    assert fetched is not None
    assert fetched.id == instance.id
    assert fetched.name == instance.name


async def test_update(repository: PostRepository) -> None:
    """Test updating an instance."""
    instance = await repository.create({"name": "Old Name"})
    updated = await repository.update(instance.id, {"name": "New Name"})
    assert updated.name == "New Name"


async def test_update_instance(repository: PostRepository) -> None:
    """Test updating an instance without re-fetching."""
    instance = await repository.create({"name": "Before Update"})
    updated = await repository.update_instance(instance, {"name": "After Update"})
    assert updated.name == "After Update"


async def test_delete(repository: PostRepository) -> None:
    """Test deleting an instance."""
    instance = await repository.create({"name": "To Be Deleted"})
    await repository.delete(instance.id)
    deleted = await repository.get(instance.id)
    assert deleted is None
