from enum import Enum

from pydantic import BaseModel, Field


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"


class ValidatedUpload(BaseModel):
    filename: str
    file_type: FileType
    size_bytes: int = Field(gt=0)
    content: bytes = Field(repr=False)


class UploadResponse(BaseModel):
    filename: str
    file_type: FileType
    size_bytes: int
