from fastapi import FastAPI

from app.config import settings

from .router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url="/docs/openapi.json",
    root_path=settings.API_V1_STR,
    debug=True,
)

app.include_router(api_router)
