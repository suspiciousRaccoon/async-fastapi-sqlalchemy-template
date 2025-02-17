from celery import Celery  # type: ignore

from app.config import settings

app = Celery(
    "app",
    broker=settings.CELERY_BROKER_URL.unicode_string(),
    backend=settings.CELERY_RESULT_BACKEND.unicode_string(),
)

app.autodiscover_tasks(["app.users"])
