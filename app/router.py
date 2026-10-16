from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import validated_upload
from app.schemas import UploadResponse, ValidatedUpload

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/resumes")
async def upload_resume(upload: Annotated[ValidatedUpload, Depends(validated_upload)]) -> UploadResponse:
    # TODO: Microsoft document processing API
    return UploadResponse(
        filename=upload.filename,
        file_type=upload.file_type,
        size_bytes=upload.size_bytes,
    )
