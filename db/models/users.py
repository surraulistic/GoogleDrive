from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from db.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True)
    email = Column(String(50), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, nullable=False, default=False)
    password = Column(String(60), nullable=False)
    token = Column(String(350), nullable=True, unique=True)
    roles = relationship("UserRole", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


