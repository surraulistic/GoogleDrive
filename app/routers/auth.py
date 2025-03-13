import logging
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.auth_service import create_access_token, get_current_active_user, authenticate_user
from app.models.schemas import User

router = APIRouter()


logger = logging.getLogger(__name__)


@router.post("/token", status_code=status.HTTP_201_CREATED)
def send_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    xx = create_access_token(user_data=form_data)
    logger.info(xx)
    return xx


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]