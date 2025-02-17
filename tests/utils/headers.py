from typing import Any

from app.users.utils import create_access_token


def create_authorization_headers_for_email(
    email: str, headers: dict[str, Any] | None = None
) -> dict[str, Any]:
    if not headers:
        headers = {}

    access_token = create_access_token(data={"sub": email})
    bearer = f"Bearer {access_token}"
    headers.update({"Authorization": bearer})

    return headers
