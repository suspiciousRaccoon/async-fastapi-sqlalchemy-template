# Async FastAPI + SQLAlchemy template
I didn't like any of the templates I found, so I made my own.  ฅ/ᐠ. ̫ .ᐟ\ฅ

## Features
- FastAPI as backend.
- PostgresSQL 17 as database.
- SQLAlchemy 2.0 
- Alembic for migrations.
- Docker for development.
- JWT for auth.
- Pytest for testing.
- Celery + RabbitMQ + SQLAlchemy for asynchronous tasks.
- CLI with rich + click.
- Fully Asynchronous.

### Installing

<details>
<summary>Details</summary>
<br/>
Clone the repo:
  
```bash
git clone git@github.com:suspiciousRaccoon/async-fastapi-sqlalchemy-template.git
cd async-fastapi-sqlalchemy-template
```

The project needs some enviroment variables to be set before running, see [Configuration](https://github.com/suspiciousRaccoon/async-fastapi-sqlalchemy-template/edit/main/README.md#configuration)

Simply copying `.env.example` is enough for it to work with docker.
```bash
cp .env.example .env
```
  
### Option 1: Docker (recommended)
Simply run:
```bash
docker compose up
```
### Option 2: uv
#### Installing
This project uses uv for dependency management
```bash
uv sync
source .venv/bin/activate 
```
Keep in mind you'll need an instance of RabbitMQ and PostgresSQL running with their enviroment variables set. See [Configuration](https://github.com/suspiciousRaccoon/async-fastapi-sqlalchemy-template/edit/main/README.md#configuration)

#### Running celery
```bash
uv run celery -A app.config_celery worker --loglevel=INFO
```
#### Running migrations
```bash
uv run alembic upgrade head
```
#### Running the backend
```bash
uv run fastapi dev --host 0.0.0.0 app/main.py
```
#### Running tests
```bash
uv run pytest
```
</details>

### Configuration
<details>
  <summary>Environment Variables</summary>
<br/>
You can find an example configuration in `.env.example`
  

| Variable                  | Example Value  | Description |
|---------------------------|---------------|-------------|
| `DOMAIN`                  | `localhost`   | The domain for deployment. |
| `ENVIRONMENT`             | `local`       | Environment type: `local`, `staging`, or `production`. |
| `BACKEND_CORS_ORIGINS`    | `"http://localhost,http://localhost:5173"` | Allowed CORS origins. |
| `SECRET_KEY`              | `changethis`  | Secret key, go to [here](https://github.com/suspiciousRaccoon/async-fastapi-sqlalchemy-template/edit/main/README.md#how-to-generate-a-secret-key) for generating one . |
| `APP_NAME`                | `Async FastAPI SQLAlchemy Template` | Application name. |
| `LOG_LEVEL`               | `DEBUG`       | Log level (`DEBUG`, `INFO`, `WARNING`, etc.). |
| `LOG_FILE`                | `/var/log/app/logfile` | Path to log file. |
| `USER_CREATION_URL`       | `http://localhost/api/v1/auth/users/verify` | URL sent in user creation emails along a token query parameter |
| `USER_FORGOT_PASSWORD_URL`| `http://localhost/api/v1/auth/users/reset-password` | URL sent in password reset emails along a token query parameter |
| `SMTP_HOST`               | *(empty)*     | SMTP server host. |
| `SMTP_USER`               | *(empty)*     | SMTP username. |
| `SMTP_PASSWORD`           | *(empty)*     | SMTP password. |
| `EMAILS_FROM_EMAIL`       | `info@example.com` | Sender email address. |
| `EMAILS_FROM_NAME`        | `info`        | Sender name. |
| `SMTP_TLS`                | `True`        | Enable TLS for SMTP. |
| `SMTP_SSL`                | `False`       | Enable SSL for SMTP. |
| `SMTP_PORT`               | `587`         | SMTP port. |
| `POSTGRES_SERVER`         | `localhost`   | PostgreSQL server address. |
| `POSTGRES_PORT`           | `5432`        | PostgreSQL server port. |
| `POSTGRES_DB`             | `postgres`    | PostgreSQL database name. |
| `POSTGRES_USER`           | `postgres`    | PostgreSQL username. |
| `POSTGRES_PASSWORD`       | `postgres`    | PostgreSQL password. |
| `PGADMIN_DEFAULT_EMAIL`   | `admin@admin.com` | Default email for pgAdmin. |
| `PGADMIN_DEFAULT_PASSWORD`| `admin`       | Default password for pgAdmin. |
| `PGADMIN_CONFIG_SERVER_MODE` | `False`    | Enable or disable server mode in pgAdmin. |
| `CELERY_BROKER_SERVER`    | `rabbitmq`    | Celery message broker server. |
| `CELERY_BROKER_USER`      | `guest`       | Celery broker username. |
| `CELERY_BROKER_PASSWORD`  | `guest`       | Celery broker password. |
| `CELERY_BROKER_PORT`      | `5672`        | Celery broker port. |
| `CELERY_BROKER_VHOST`     | *(empty)*     | Celery virtual host. RabbitMQ defaults to "/" |

#### How to generate a secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

</details>

### Using the app CLI
<details>
  <summary>Details</summary>
<br/>
#### Creating users from CLi
  
```bash
uv run appcli createsuperuser
# or for normal users
uv run appcli createuser
```

You can change `appcli` by editing: 
```
[project.scripts]
appcli = "app.cli.main:cli"
```
inside the `pyproject.toml`
  
</details>


## License
MIT
