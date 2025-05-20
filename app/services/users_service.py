import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from jwt import InvalidTokenError

from sqlalchemy import select
from starlette import status

from app.auth.auth_config import oauth2_scheme
from app.schemas.auth import TokenData
from config import settings

from db.connector import db_connector
from db.models import users
from db.models.roles import UserRole, Role
from db.models.users import User


async def get_all_users(skip: int = 0, limit: int = 100):
    async with db_connector.async_session() as session:
        stmt = select(users.User).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_user_by_email(email: str):
    async with db_connector.async_session() as session:
        return await session.scalar(select(User).where(User.email == email))


async def get_user_by_id(user_id: uuid.UUID):
    async with db_connector.async_session() as session:
        return await session.scalar(select(User).where(User.id == user_id))


async def get_user_role_id(user_id: uuid.UUID):
    async with db_connector.async_session() as session:
        stmt = select(UserRole.role_id).where(UserRole.user_id == user_id)
        result = await session.execute(stmt)
        roles = result.all()
        if roles:
            return [str(role[0]) for role in roles]
        return []


async def get_role_by_id(roles_id: list[str]):
    uuid_ids = [uuid.UUID(role_id) for role_id in roles_id]
    async with db_connector.async_session() as session:
        stmt = select(Role.name).where(Role.id.in_(uuid_ids))
        result = await session.execute(stmt)
        roles = result.scalars().all()
        if roles:
            return roles
        return []


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.auth_config.secret_key, algorithms=[settings.auth_config.algorithm])
        username = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        raise credentials_exception from e
    user = await get_user_by_email(email=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
