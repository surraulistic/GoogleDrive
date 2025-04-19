import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from jwt import InvalidTokenError

from sqlalchemy.orm import Session
from sqlalchemy import select
from starlette import status

from app.auth import oauth2_scheme, SECRET_KEY, ALGORITHM
from app.schemas.auth import TokenData

from db.connector import db_connector
from db.models import users
from db.models.roles import UserRole
from db.models.users import User


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(users.User).offset(skip).limit(limit).all()


def get_user_by_email(email: str):
    with db_connector.session() as session:
        a = session.scalar(select(User).where(User.email == email))
        return a

def get_user_by_id(user_id: uuid.UUID):
    with db_connector.session() as session:
        return session.scalar(select(User).where(User.id == user_id))


def get_user_role(user_id: uuid.UUID):
    with db_connector.session() as session:
        if result := session.query(UserRole.role_id).filter(UserRole.user_id == user_id).all():
            if result:
                return [str(result[0]) for result in result]
            return []


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        raise credentials_exception from e
    user = get_user_by_email(email=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
