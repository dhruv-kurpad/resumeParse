from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user, get_resume_service, validated_upload
from app.schemas import ResumeResponse, User, ValidatedUpload
from app.services.resume_service import ResumeService

router = APIRouter()

ServiceDep = Annotated[ResumeService, Depends(get_resume_service)]


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/resumes", status_code=201)
async def upload_resume(
    upload: Annotated[ValidatedUpload, Depends(validated_upload)],
    service: ServiceDep,
    user: User = Depends(get_current_user),) -> ResumeResponse:
    return await service.process(upload)


@router.get("/resumes/{resume_id}")
async def get_resume(resume_id: str, service: ServiceDep) -> ResumeResponse:
    resume = service.get(resume_id)
    if resume is None:
        raise HTTPException(404, f"Resume {resume_id} not found")
    return resume
