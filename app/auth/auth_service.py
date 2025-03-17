from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError

from app.auth import pwd_context, oauth2_scheme
from app.auth.models.token import TokenData
from app.services.user_service import get_user_by_email
from db.models.users import User


SECRET_KEY = "e0fbcfca8a11848f875efd1e1753cfa586cd4497dd638b960d4551d24cfbc37e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(user_data: OAuth2PasswordRequestForm, expires_delta: timedelta | None = None):
    to_encode = {
        "grant_type": user_data.grant_type,
        "username": user_data.username,
        "password": user_data.password,
        "scopes": user_data.scopes,
        "client_id": user_data.client_id,
        "client_secret": user_data.client_secret,
    }
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str):
    user = get_user_by_email(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        raise credentials_exception from e
    user = get_user_by_email(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
