from pathlib import PurePath, Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from starlette import status

from app.models.files import TreeFileTypes
from app.services.file_service import find_last_file_with_name, increase_last_file_name, generate_tree_json

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file(file: UploadFile, user_id: int = File(...)):
    directory_path = Path(PurePath("files", str(user_id)))
    file_name = file.filename
    if not directory_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User folder not found")
    index = await find_last_file_with_name(directory_path, file_name)
    file_name = await increase_last_file_name(file_name, index)
    with open(directory_path.joinpath(file_name), "wb+") as f:
        f.write(await file.read())
    return {"author_id": user_id, "filename": file_name}


@router.post("/create_user_dir/{user_id}")
async def create_user_dir(user_id: int):
    user_folder = Path(PurePath("files", str(user_id)))
    if not user_folder.exists():
        user_folder.mkdir(parents=True)
        return user_folder
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User folder already exists")


@router.post("/create_folder/{user_id}")
async def create_folder(user_id: int, path: str, folder_name: str):
    user_folder = Path(PurePath(r"files", str(user_id)))
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


# def get_all_directories_as_dict(user_id: int) -> dict:
#     directories = {}
#     directories_path = Path(PurePath("files", str(user_id)))
#     for subdir in directories_path.iterdir():
#         if subdir.is_dir():
#             directories[subdir.name] = subdir.resolve()
#     return directories
# Должен вернуться JSON в виде структуры всех папок
