from pydantic import ValidationError

from app.cli.main import Display
from app.email.utils import Email
from app.users.schema import PasswordModel


def validate_email(email: str) -> bool:
    try:
        Email(email=email)
        return True
    except ValidationError:
        return False


def validate_password(password: str) -> bool:
    try:
        PasswordModel(password=password)
        return True
    except ValidationError:
        return False


def get_valid_email(display: Display) -> str:
    while True:
        email = display.capture_input("Email Address: ")
        if validate_email(email):
            return email
        display.error("Error: Invalid email")


def get_valid_password(display: Display) -> str:
    while True:
        password1 = display.capture_input("Password: ")
        password2 = display.capture_input("Password (again): ")

        if password1 != password2:
            display.error("Error: The passwords didn't match")
            continue

        if validate_password(password1):
            return password1

        display.error(
            "Error: The password doesn't meet strength requirements. Bypass validation? y/N"
        )
        bypass = display.capture_input().lower()
        if bypass == "y":
            return password1
