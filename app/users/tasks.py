from typing import Callable

from app.config_celery import app
from app.email.main import (
    EmailData,
    generate_new_account_email,
    generate_reset_password_email,
    send_email,
)
from app.email.utils import Email, EmailStatus, generate_email_token
from app.utils import get_logger

logger = get_logger()


def send_email_task(
    email: Email, email_generator: Callable[..., EmailData]
) -> EmailStatus:
    """
    Sends an email using a provided email generation function.

    Args:
        email: A pydantic model with a valid `email` attribute.
        email_generator: A function that takes email, email_to, and token, and returns email data.

    Returns:
        EmailStatus: Status of the email.
    """
    email_sent = False
    error = None

    email_token = generate_email_token(email.email)
    email_data = email_generator(
        email=email.email, email_to=email.email, token=email_token
    )

    try:
        send_email(
            html=email_data.html_content,
            subject=email_data.subject,
            email_to=email.email,
        )
        email_sent = True
    except Exception as e:
        error = str(e)
        logger.exception(e)

    return EmailStatus(email=email.email, sent=email_sent, error=error)


@app.task  # type: ignore[misc]
def hello(number: int) -> int:
    return number * 2


@app.task(pydantic=True)  # type: ignore[misc]
def send_new_user_email(email: Email) -> EmailStatus:
    """Sends an account activation email."""
    return send_email_task(email, generate_new_account_email)


@app.task(pydantic=True)  # type: ignore[misc]
def send_reset_password_email(email: Email) -> EmailStatus:
    """Sends a password reset email."""
    return send_email_task(email, generate_reset_password_email)
