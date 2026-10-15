from fastapi import APIRouter, UploadFile

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/resumes")
async def upload_resume(file: UploadFile) -> dict:
    content = await file.read()
    # TODO: Microsoft document processing API
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
    }
