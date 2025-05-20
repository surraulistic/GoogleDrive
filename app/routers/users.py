from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.schemas import users
from app.schemas.users import User
from app.services.users_service import get_all_users, get_current_active_user, get_user_role_id, get_role_by_id

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


@router.get("/me/roles", response_model=list[str], status_code=status.HTTP_200_OK)
async def get_current_user_role(
    current_user = Depends(get_current_active_user),
):
    roles_ids = await get_user_role_id(current_user.id)
    roles = await get_role_by_id(roles_ids)
    return roles
