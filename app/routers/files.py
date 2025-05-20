import os
import uuid
from pathlib import PurePath, Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import FileResponse
from app.auth.auth_config import oauth2_scheme
from app.schemas.users import User
from app.services.users_service import get_current_user
from app.validators.upload_limits import upload_file_limiter
from app.schemas.files import TreeFileTypes
from app.services.files_service import (
    find_last_file_with_name,
    increase_last_file_name,
    generate_tree_json,
)


router = APIRouter()


file_storage: dict[str, str] = {}


@router.post("/upload", dependencies=[Depends(oauth2_scheme)])
async def upload_file(
        file: UploadFile = Depends(upload_file_limiter),
        current_user: User = Depends(get_current_user),
        file_path: str | None = File(default=None),
        ):
    file_id = str(uuid.uuid4())
    user_id = current_user.id
    file_size = file.size
    directory_path = Path(PurePath("files", str(user_id)))
    file_name = file.filename
    if file_path in [str(user_id), "/", None]:
        path_to_save = directory_path
    else:
        path_to_save = Path(PurePath(directory_path, file_path))
    if not path_to_save.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    index = await find_last_file_with_name(path_to_save, file_name)
    file_name = await increase_last_file_name(file_name, index)
    full_file_path = path_to_save.joinpath(file_name)
    with open(path_to_save.joinpath(file_name), "wb+") as f:
        f.write(await file.read())
    file_storage[file_id] = str(full_file_path)
    return {
        "author_id": user_id,
        "file_id": file_id,
        "filename": file_name,
        "path": path_to_save,
        "size": f"{float(file_size / 1024 / 1024)} MB",
    }


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    file_path = file_storage.get(file_id)
    if not file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(path=file_path, filename=Path(file_path).name, media_type='application/octet-stream')


@router.post("/create_user_dir/{user_id}", dependencies=[Depends(oauth2_scheme)])
async def create_user_dir(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    user_folder = Path(PurePath("files", str(user_id)))
    if not user_folder.exists():
        user_folder.mkdir(parents=True)
        return user_folder
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User directory already exists")


@router.post("/create_folder/{user_id}", dependencies=[Depends(oauth2_scheme)])
async def create_folder(
        path: str,
        folder_name: str,
        current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    user_folder = Path(PurePath("files", str(user_id)))
    if not user_folder.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User directory not found")
    path_to = Path(PurePath(user_folder, path)) if path != str(user_id) else user_folder
    if not path_to.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    index = await find_last_file_with_name(path_to, folder_name)
    folder_name = await increase_last_file_name(folder_name, index)
    path_to.joinpath(folder_name).mkdir(parents=True)


@router.get("/dirs_structure", dependencies=[Depends(oauth2_scheme)])
def get_all_directories_as_dict(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    base_path = Path(PurePath("files", str(user_id)))
    if base_path.exists():
        tree_json = generate_tree_json(base_path, TreeFileTypes.folders)
        return tree_json
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folders tree not found")