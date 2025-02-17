from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from app.config import settings

async_engine = create_async_engine(
    url=settings.SQLALCHEMY_DATABASE_URI.unicode_string()
)
