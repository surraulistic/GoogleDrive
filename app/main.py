import uvicorn
from fastapi import FastAPI

from app.middleware.auth_require import AuthMiddleware
from app.routers.files import router as files_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router


app = FastAPI()


app.include_router(files_router)

app.include_router(
    router=users_router,
    prefix="/users",
)

app.include_router(
    router=auth_router,
    prefix="/auth",
)


app.add_middleware(AuthMiddleware, excluded_routes={""})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)