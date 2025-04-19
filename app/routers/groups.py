import uuid

from fastapi import HTTPException
from starlette import status

from app.routers.users import router
from app.services.group_service import assign_role


@router.post("/groups", response_model=None, status_code=status.HTTP_201_CREATED)
async def set_user_role(user_id: uuid.UUID, role_id: uuid.UUID):
    result = assign_role(user_id, role_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign role")
