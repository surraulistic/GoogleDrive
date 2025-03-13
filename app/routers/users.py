from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.auth import oauth2_scheme
from app.models import schemas
from app.services.user_service import get_all_users, register, get_user_by_email
from db.connector import get_db


router = APIRouter()

@router.get("/users", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_all_users(db, skip=skip, limit=limit)
    return [schemas.User(
        id = user.id,
        username = user.username,
        is_active = user.is_active,
        email = user.email,
    ) for user in users]


@router.post("/register", response_model=schemas.LiteUser, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate):
    if get_user_by_email(email=user_data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user = register(user_data=user_data)
    return user


@router.post("/login", response_model=schemas.LiteUser)
def get_user_by_id(access_token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    ...