from sqlalchemy import Column, String, ForeignKey, UUID
from sqlalchemy.orm import relationship

from db.models.base import BaseModel, Base


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, unique=True, nullable=False)
    users = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")