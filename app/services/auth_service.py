import uuid
from datetime import timedelta, datetime, timezone
import jwt
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.auth_config import pwd_context
from app.schemas.auth import Token
from app.schemas.users import UserCreate
from app.services.users_service import get_user_by_email, get_user_by_id
from config import settings
from db.connector import db_connector
from db.models.users import User


async def create_access_token(user_data: OAuth2PasswordRequestForm, expires_delta: timedelta | None = None):
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
    encoded_jwt = jwt.encode(to_encode, settings.auth_config.secret_key, algorithm=settings.auth_config.algorithm)
    return Token(access_token=encoded_jwt)


async def authenticate_user(username: str, password: str):
    user = await get_user_by_email(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


async def change_pwd(user_id: uuid.UUID, new_pwd: str):
    async with db_connector.async_session() as session:
        user = await get_user_by_id(user_id)
        user.password = pwd_context.hash(new_pwd)
        session.add(user)
        session.flush()
        return None


async def register(user_data: UserCreate):
    async with db_connector.async_session() as session:
        user = User(email=user_data.email)
        user.password = pwd_context.hash(user_data.password)
        session.add(user)
        session.flush()
        return user



