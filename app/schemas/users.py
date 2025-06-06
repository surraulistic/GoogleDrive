import uuid
from enum import StrEnum
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class LiteUser(UserBase):
    id: uuid.UUID


class User(UserBase):
    id: uuid.UUID
    username: str | None = None
    is_active: bool | None = None


class UserAuth(UserBase):
    username: EmailStr
    password: str


class UserInDB(User):
    hashed_password: str


class UserRole(StrEnum):
    PREMIUM = "premium"
    REGULAR = "regular"
    ADMIN = "admin"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class RoleRequest(UserBase):
    role: UserRole


