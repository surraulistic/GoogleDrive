import uuid

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.auth import pwd_context
from db.connector import db_connector
from db.models import users
from app.models.schemas import UserCreate
from db.models.roles import UserRole, Role
from db.models.users import User


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(users.User).offset(skip).limit(limit).all()


def get_user_by_email(email: str):
    with db_connector.session() as session:
        return session.scalar(select(User).where(User.email == email))


def register(user_data: UserCreate):
    with db_connector.session() as session:
        user = User(email=user_data.email)
        user.password = pwd_context.hash(user_data.password)
        session.add(user)
        session.flush()
        return user


def get_user_role(user_id: uuid.UUID):
    with db_connector.session() as session:
        if result := session.query(UserRole.role_id).filter(UserRole.user_id == user_id).all():
            if result:
                return [str(result[0]) for result in result]
            return []


def assign_role(user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
    with db_connector.session() as session:
        role = session.query(Role).filter_by(id=role_id).first()
        if not role:
            return False
        user_role = UserRole(user_id=user_id, role_id=role.id)
        session.add(user_role)
        return True

def add_role(role_name: str):
    with db_connector.session() as session:
        new_role = Role(name=role_name)
        session.add(new_role)
        session.commit()
        session.flush()
        return new_role