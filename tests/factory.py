from typing import TypeVar

from polyfactory import Ignore, Use
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.factories.pydantic_factory import ModelFactory

from app.users.models import User
from app.users.utils import generate_random_password, get_password_hash
from app.users.schema import AuthUser
from app.users.schema import UserCreate
from app.users.schema import UserUpdate


class UserFactory(SQLAlchemyFactory[User]):
    id = Ignore()
    email = Use(lambda: UserFactory.__faker__.email())
    hashed_password = Use(get_password_hash, generate_random_password())
    is_active = Use(lambda: True)


class AuthUserSchemaFactory(ModelFactory[AuthUser]): ...


class UserCreateSchemaFactory(ModelFactory[UserCreate]): ...


class UserUpdateSchemaFactory(ModelFactory[UserUpdate]): ...
