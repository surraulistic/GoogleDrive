import uuid

from db.connector import db_connector
from db.models import Role, UserRole


def add_role(role_name: str):
    with db_connector.session() as session:
        new_role = Role(name=role_name)
        session.add(new_role)
        session.commit()
        session.flush()
        return new_role


def assign_role(user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
    with db_connector.session() as session:
        role = session.query(Role).filter_by(id=role_id).first()
        if not role:
            return False
        user_role = UserRole(user_id=user_id, role_id=role.id)
        session.add(user_role)
        return True
