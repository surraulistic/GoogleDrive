from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas import users
from app.schemas.users import User
from app.services.users_service import get_all_users, get_current_active_user
# from db.connector import get_db


router = APIRouter()


@router.get("/", response_model=list[users.User])
async def read_users(skip: int = 0, limit: int = 100):
    db_users = await get_all_users(skip=skip, limit=limit)
    return [users.User(
        id = user.id,
        username = user.username,
        is_active = user.is_active,
        email = user.email,
    ) for user in db_users]


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


# @router.get("/users/me/items/")
# async def read_own_items(
#     current_user: Annotated[User, Depends(get_current_active_user)],
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]


# @router.post("/login", response_model=schemas.LiteUser)
# async def get_user_by_id(access_token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
#     ...

