from functools import lru_cache
from pathlib import PurePath
from typing import Annotated

from fastapi import Depends, HTTPException, UploadFile

from app.config import Settings, get_settings
from app.services.parser import AzureTextExtractor
from app.services.profile import ClaudeProfileBuilder
from app.services.repository import ResumeRepository, SqliteResumeRepository
from app.schemas import FileType, User, ValidatedUpload
from app.services.resume_service import ResumeService

SettingsDep = Annotated[Settings, Depends(get_settings)]

#Document type validation
EXTENSIONS = {".pdf": FileType.PDF, ".docx": FileType.DOCX}
MAGIC_BYTES = {FileType.PDF: b"%PDF-", FileType.DOCX: b"PK\x03\x04"}

async def validated_upload(file: UploadFile, settings: SettingsDep) -> ValidatedUpload:
    #ex: resume.pdf
    filename = PurePath(file.filename or "").name
    file_type = EXTENSIONS.get(PurePath(filename).suffix.lower())
    #Quick check before reading the file
    if file_type is None:
        raise HTTPException(415, "Only .pdf and .docx files are accepted")
    chunks = []
    size = 0
    while True:
        chunk = await file.read(settings.upload_chunk_bytes)

        if not chunk: #No more chunks
            break
        size += len(chunk)
        if size > settings.max_upload_bytes:
            raise HTTPException(413, f"File exceeds {settings.max_upload_bytes} bytes")
        chunks.append(chunk)

    if size == 0:
        raise HTTPException(400, "File is empty")

    content = b"".join(chunks)
    if not content.startswith(MAGIC_BYTES[file_type]):
        raise HTTPException(415, f"File content is not a valid {file_type.value}")

    return ValidatedUpload(filename=filename, file_type=file_type, size_bytes=size, content=content)


@lru_cache
def get_extractor() -> AzureTextExtractor:
    settings = get_settings()
    return AzureTextExtractor(settings.azure_di_endpoint, settings.azure_di_key)


@lru_cache
def get_profile_builder() -> ClaudeProfileBuilder:
    settings = get_settings()
    return ClaudeProfileBuilder(settings.anthropic_api_key, settings.anthropic_model)


@lru_cache
def get_repository() -> ResumeRepository:
    return SqliteResumeRepository(get_settings().database_path)


def get_resume_service(
    extractor: Annotated[AzureTextExtractor, Depends(get_extractor)],
    profile_builder: Annotated[ClaudeProfileBuilder, Depends(get_profile_builder)],
    repository: Annotated[ResumeRepository, Depends(get_repository)],
) -> ResumeService:
    return ResumeService(extractor, profile_builder, repository)


def get_current_user() -> User:
    # Placeholder until auth exists.
    return User(name="Unknown")
