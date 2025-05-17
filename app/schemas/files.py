from enum import StrEnum

from pydantic import BaseModel


class FileUploadRequest(BaseModel):
    author_id: int


class TreeFileTypes(StrEnum):
    all = "all"
    files = "files"
    folders = "folders"