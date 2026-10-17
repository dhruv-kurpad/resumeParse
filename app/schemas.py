from enum import Enum

from pydantic import BaseModel, Field


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"


class User(BaseModel):
    name: str


class ValidatedUpload(BaseModel):
    filename: str
    file_type: FileType
    size_bytes: int = Field(gt=0)
    content: bytes = Field(repr=False)


class ContactInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    links: list[str] = []


class ExperienceEntry(BaseModel):
    title: str | None = None
    company: str | None = None
    dates: str | None = None
    description: list[str] = []

class ProjectEntry(BaseModel):
    name: str | None = None
    description: list[str] = []
    dates: str | None = None
    links: list[str] = []


class ResumeProfile(BaseModel):
    contact: ContactInfo
    skills: list[str] = []
    experience: list[ExperienceEntry] = []
    projects: list[ProjectEntry] = []


class ResumeResponse(BaseModel):
    id: str
    filename: str
    file_type: FileType
    size_bytes: int
    profile: ResumeProfile
