import asyncio

import click
from rich.console import Console

from app.database.core import AsyncSessionLocal
from app.users.models import User
from app.users.service import UserService

from .validate import (
    get_valid_email,
    get_valid_password,
)


class Display:
    def __init__(self) -> None:
        self._console = Console()

    def log(self, msg: str) -> None:
        self._console.print(msg)

    def success(self, msg: str) -> None:
        self._console.print(msg, style="bold green")

    def warning(self, msg: str) -> None:
        self._console.print(msg, style="bold yellow")

    def error(self, msg: str) -> None:
        self._console.print(msg, style="bold red")

    def line(self, msg: str) -> None:
        self._console.rule(msg)

    def capture_input(self, msg: str = "") -> str:
        return self._console.input(msg)


@click.group()
def cli() -> None:
    pass


@cli.command()
def createsuperuser() -> None:
    display = Display()
    display.line("Create Super User")

    email = get_valid_email(display)
    password = get_valid_password(display)

    user_data = {"email": email, "password": password}

    async def create_super_user() -> User:
        async with AsyncSessionLocal() as session:
            user = await UserService(session).create_super_user(user_data=user_data)
            return user

    try:
        user = asyncio.run(create_super_user())
        display.success(f"User created succesfully {user.email}")
    except Exception as e:
        display.error(f"Error: could not create user {e}")


@cli.command()
def createuser() -> None:
    display = Display()
    display.line("Create User")

    email = get_valid_email(display)
    password = get_valid_password(display)

    user_data = {"email": email, "password": password}

    async def create_user() -> User:
        async with AsyncSessionLocal() as session:
            user = await UserService(session).create_user(user_data=user_data)
            return user

    try:
        user = asyncio.run(create_user())
        display.success(f"User created successfully: {user.email}")
    except Exception as e:
        display.error(f"Error: could not create user {e}")
