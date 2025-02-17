"""
List of all the application models, mainly for alembic migrations but could be used for row level permissions or a more complex permission system
"""

from celery.backends.database.session import ResultModelBase  # type: ignore

from app.users.models import Base as UserBase

# used for multiple models
# https://alembic.sqlalchemy.org/en/latest/autogenerate.html#autogenerating-multiple-metadata-collections
metadata = [UserBase.metadata, ResultModelBase.metadata]  # add rest of models here
