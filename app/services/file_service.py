from pathlib import Path

from fastapi import HTTPException

from app.models.files import TreeFileTypes
from db.database import users


async def find_last_file_with_name(file_path: Path, file_name: str) -> int:
    if not file_path.joinpath(file_name).exists():
        return -1
    file_extension = Path(file_name).suffix
    file_name = file_name.replace(file_extension, "")
    max_index = 0
    for file in file_path.iterdir():
        if file.name == file_name:
            continue
        index = file.name.replace(f"{file_name}(", "").replace(f"){file_extension}", "")
        if index.isnumeric() and int(index) > max_index:
            max_index = int(index)
    return max_index


async def increase_last_file_name(file_name: str, index: int) -> str:
    if index == -1:
        return file_name
    file_extension = Path(file_name).suffix
    result = f"{file_name.replace(file_extension, '')}({index + 1}){file_extension}"
    return result


def generate_tree_json(path: Path, file_type: TreeFileTypes) -> dict:
    tree = {"name": path.name, "children": []}
    if path.is_dir():
        contents = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
        for item in contents:
            if file_type == TreeFileTypes.files and not item.is_file():
                continue
            if file_type == TreeFileTypes.folders and not item.is_dir():
                continue
            if item.is_dir():
                tree["children"].append(generate_tree_json(item, file_type))
            else:
                tree["children"].append({"name": item.name})
    return tree


def get_user_group(user_id: int):
    for user in users:
        if user["user_id"] == user_id:
            return user["group"]
    raise HTTPException(status_code=404, detail="User not found")
