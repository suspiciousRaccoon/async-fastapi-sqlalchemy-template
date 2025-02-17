"""
Taken from https://github.com/fastapi/full-stack-fastapi-template/blob/ba1706b48994605580c3e246dfd416afb6124546/backend/app/core/config.py
"""

import os
import secrets
import warnings
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    PostgresDsn,
    UrlConstraints,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

DOTENV = os.path.join(
    os.path.dirname(__file__), Path("../.env")
)  # .env resides in root of the project


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


CeleryBrokerUrl = Annotated[
    MultiHostUrl, UrlConstraints(allowed_schemes=["amqp", "pyamqp"])
]  # assumes rabbitmq
CeleryBackendUrl = Annotated[
    MultiHostUrl, UrlConstraints(allowed_schemes=["db+postgresql"])
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV, env_ignore_empty=True, extra="ignore"
    )

    APP_NAME: str
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    LOG_LEVEL: Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = (
        "DEBUG"
    )
    USER_CREATION_URL: str
    USER_FORGOT_PASSWORD_URL: str

    # LOG_FILE: FilePath

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SERVER_HOST(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    CELERY_BROKER_SERVER: str
    CELERY_BROKER_USER: str = "guest"
    CELERY_BROKER_PASSWORD: str = "guest"
    CELERY_BROKER_PORT: int = 5672
    CELERY_BROKER_VHOST: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def CELERY_BROKER_URL(self) -> CeleryBrokerUrl:
        return MultiHostUrl.build(
            scheme="amqp",
            username=self.CELERY_BROKER_USER,
            password=self.CELERY_BROKER_PASSWORD,
            host=self.CELERY_BROKER_SERVER,
            port=self.CELERY_BROKER_PORT,
            path=self.CELERY_BROKER_VHOST,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def CELERY_RESULT_BACKEND(self) -> CeleryBackendUrl:
        return MultiHostUrl.build(
            scheme="db+postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis" or value == "postgres" or value == "guest":
            message = (
                f'The value of {var_name} is "{value}", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "CELERY_BROKER_PASSWORD", self.CELERY_BROKER_PASSWORD
        )

        return self


settings = Settings()
