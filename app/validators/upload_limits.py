from uuid import UUID

from fastapi import HTTPException, UploadFile, File, status

from app.services.users_service import get_user_role
from config import file_config


premium_role_id = "dcccd2bb-db76-4d77-b1c6-818b1174e51d"
admin_role_id = "ce274ec4-fb55-429a-a436-547f1b28136a"
user_role_id = "10936e9b-2672-41d5-a293-c6efeb09385c"


regular_user = "9fa6b7c2-ef62-4760-b5b4-e9fdf412823a"
prem_user = "32e34e7d-ba36-49b7-a09e-588af9f355dd"


class UploadFileLimiter:
    def __init__(self, max_file_size: int):
        self.max_file_size_bytes = max_file_size * 1024 * 1024

    async def __call__(self, file: UploadFile = File(...)):

        user_role = get_user_role(UUID("32e34e7d-ba36-49b7-a09e-588af9f355dd"))
        file_size = file.size
        if file_size > self.max_file_size_bytes and premium_role_id not in user_role:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Upload size is over limit. Max size is {file_config.user_upload_limit_mb} MB. Buy Premium."
            )
        if file_size > file_config.prem_upload_limit_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"You reached upload limit. Max size is {file_config.prem_upload_limit_mb} MB"
            )
        return file


upload_file_limiter = UploadFileLimiter(file_config.user_upload_limit_mb)