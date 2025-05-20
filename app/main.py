import uvicorn
from fastapi import FastAPI

from config import settings
from app.middleware.auth_require import AuthMiddleware
from app.routers.files import router as files_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router


app = FastAPI()


app.include_router(
    router=files_router,
    prefix="/files",
    tags=["files"]
)


app.include_router(
    router=users_router,
    prefix="/users",
    tags=["users"]
)


app.include_router(
    router=auth_router,
    prefix="/auth",
    tags=["auth"]
)


app.add_middleware(
    AuthMiddleware,
    excluded_routes={"/files/download/"}
)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.api_config.HOST, port=settings.api_config.PORT, reload=settings.api_config.RELOAD)