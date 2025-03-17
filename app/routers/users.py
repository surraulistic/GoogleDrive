import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session


from app.models import schemas
from app.services.user_service import get_all_users, register, get_user_by_email, assign_role
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
async def register_user(user_data: schemas.UserCreate):
    if get_user_by_email(email=user_data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user = register(user_data=user_data)
    return user


# @router.post("/login", response_model=schemas.LiteUser)
# async def get_user_by_id(access_token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
#     ...


@router.post("/users/groups", response_model=None, status_code=status.HTTP_201_CREATED)
async def set_user_role(user_id: uuid.UUID, role_id: uuid.UUID):
    result = assign_role(user_id, role_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign role")