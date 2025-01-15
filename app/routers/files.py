from pathlib import PurePath, Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from starlette import status

from app.models.files import TreeFileTypes
from app.services.file_service import find_last_file_with_name, increase_last_file_name, generate_tree_json, \
    get_user_group
from app.settings import Settings, prem_upload_limit, user_upload_limit

router = APIRouter(prefix="/files", tags=["files"])





@router.post("/upload")
async def upload_file(
        file: UploadFile,
        user_id: int = File(...),
        file_path: str | None = File(default=None)
        ):
    directory_path = Path(PurePath("files", str(user_id)))
    file_name = file.filename
    file_size = file.size
    user_group = get_user_group(user_id)
    if file_size > user_upload_limit and user_group != "premium":
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Upload size is over limit. Max size is 50 MB. Buy Premium.")
    if file_size > prem_upload_limit:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="You reached uploading limit. Max size is 100 MB.")
    if file_path in [str(user_id), "/", None]:
        path_to_save = directory_path
    else:
        path_to_save = Path(PurePath(directory_path, file_path))
    if not path_to_save.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    index = await find_last_file_with_name(path_to_save, file_name)
    file_name = await increase_last_file_name(file_name, index)
    with open(path_to_save.joinpath(file_name), "wb+") as f:
        f.write(await file.read())
    return {
        "author_id": user_id,
        "filename": file_name,
        "path": path_to_save,
        "size": f"{int(file_size / 1024 / 1024)} MB",
    }


@router.post("/create_user_dir/{user_id}")
async def create_user_dir(user_id: int):
    user_folder = Path(PurePath("files", str(user_id)))
    if not user_folder.exists():
        user_folder.mkdir(parents=True)
        return user_folder
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User folder already exists")


@router.post("/create_folder/{user_id}")
async def create_folder(user_id: int, path: str, folder_name: str):
    user_folder = Path(PurePath("files", str(user_id)))
    if not user_folder.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User folder not found")
    path_to = Path(PurePath(user_folder, path)) if path != str(user_id) else user_folder
    if not path_to.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
    index = await find_last_file_with_name(path_to, folder_name)
    folder_name = await increase_last_file_name(folder_name, index)
    path_to.joinpath(folder_name).mkdir(parents=True)


@router.get("/dirs_structure")
def get_all_directories_as_dict(user_id: int):
    base_path = Path(PurePath("files", str(user_id)))
    if base_path.exists():
        tree_json = generate_tree_json(base_path, TreeFileTypes.folders)
        return tree_json
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folders tree not found")