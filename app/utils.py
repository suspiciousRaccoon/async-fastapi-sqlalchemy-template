import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def get_logger() -> logging.Logger:
    return logging.getLogger(__name__)


def get_current_time() -> datetime:
    """
    Get current time in UTC
    """
    return datetime.now(tz=timezone.utc).astimezone(ZoneInfo("UTC"))
