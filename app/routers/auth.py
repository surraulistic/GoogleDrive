import logging
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import oauth2_scheme, pwd_context
from app.services.auth_service import create_access_token, authenticate_user, register, change_pwd
from app.schemas.users import ChangePasswordRequest, User
from app.schemas import users
from app.services.user_service import get_user_by_email, get_current_user

router = APIRouter()


# logger = logging.getLogger(__name__)
# logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


@router.post("/token", status_code=status.HTTP_200_OK)
def send_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_creds = authenticate_user(form_data.username, form_data.password)
    if not user_creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return create_access_token(user_data=form_data)

@router.post("/register", response_model=users.LiteUser, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: users.UserCreate):
    if get_user_by_email(email=user_data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user = register(user_data=user_data)
    return user


@router.post("/change-pwd", dependencies = [Depends(oauth2_scheme)], status_code=status.HTTP_200_OK)
async def change_password(
        request: ChangePasswordRequest,
        current_user: User = Depends(get_current_user)
):
    if not pwd_context.verify(request.old_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")
    if pwd_context.verify(request.new_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cant be the same")
    change_pwd(
        user_id=current_user.id,
        new_pwd=request.new_password,
    )
    return {"message": "Password changed"}