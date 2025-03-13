import uuid

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.auth import pwd_context
from db.connector import db_connector
from db.models import users
from app.models.schemas import UserCreate
from db.models.users import User


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(users.User).offset(skip).limit(limit).all()


def get_user_by_email(email: str):
    with db_connector.session() as session:
        return session.scalar(select(User).where(User.email == email))


def get_user_group(table, column, user_id: uuid.UUID):
    with db_connector.session() as session:
        if result := session.query(getattr(table, column)).filter(table.id == user_id).one_or_none():
            return result[0] if result else None


def register(user_data: UserCreate):
    with db_connector.session() as session:
        user = User(email=user_data.email)
        user.hashed_password = pwd_context.hash(user_data.password)
        session.add(user)
        session.flush()
        return user
