import logging
import token
from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, UploadFile, File, status, Depends

from app.auth import oauth2_scheme
from app.routers.auth import send_token
from app.routers.users import get_current_user_role
from app.services.users_service import get_user_role_id, get_current_active_user, get_role_by_id
from config import file_config
from db.models import User


# logger = logging.getLogger(__name__)
# logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


class UploadFileLimiter:
    async def __call__(self,  current_user: Annotated[User, Depends(get_current_active_user)], file: UploadFile = File(...)):
        roles_id = await get_user_role_id(current_user.id)
        user_roles = await get_role_by_id(roles_id)
        file_size = file.size

        if file_size > file_config.user_upload_limit and 'premium' not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Upload size is over limit. Max file size is {file_config.user_upload_limit/1024/1024} MB. Try Premium subscription."
            )

        if file_size > file_config.prem_upload_limit and 'admin' not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"You reached upload limit for premiums. Max file size is {file_config.prem_upload_limit/1024/1024} MB."
            )

        if file_size > file_config.admin_upload_limit:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"You reached upload limit for admins. Max file size is {file_config.prem_upload_limit/1024/1024} MB."
            )
        return file


upload_file_limiter = UploadFileLimiter()