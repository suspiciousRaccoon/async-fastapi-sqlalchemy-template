from fastapi import APIRouter

from .routes.auth import router as auth_router
from .routes.superusers import router as superuser_router
from .routes.users import router as user_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(superuser_router)
