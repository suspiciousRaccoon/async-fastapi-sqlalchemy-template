from fastapi import APIRouter

from app.users.router import router as user_router

api_router = APIRouter(
    responses={404: {"description": "Not found"}},
)

api_router.include_router(
    user_router,
    prefix="/auth",
    tags=["Authentication"],
)


@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
