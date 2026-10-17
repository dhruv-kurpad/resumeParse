import uuid

from starlette.concurrency import run_in_threadpool

from app.services.parser import AzureTextExtractor
from app.services.profile import ClaudeProfileBuilder
from app.services.repository import ResumeRepository
from app.schemas import ResumeResponse, ValidatedUpload


class ResumeService:
    def __init__(
        self,
        extractor: AzureTextExtractor,
        profile_builder: ClaudeProfileBuilder,
        repository: ResumeRepository,
    ):
        self.extractor = extractor
        self.profile_builder = profile_builder
        self.repository = repository

    async def process(self, upload: ValidatedUpload) -> ResumeResponse:
        # Both clients block while they wait on the network, so keep them off the event loop.
        text = await run_in_threadpool(self.extractor.extract, upload.content)
        profile = await run_in_threadpool(self.profile_builder.build, text)

        resume = ResumeResponse(
            id=uuid.uuid4().hex,
            filename=upload.filename,
            file_type=upload.file_type,
            size_bytes=upload.size_bytes,
            profile=profile,
        )
        self.repository.save(resume)
        return resume

    def get(self, resume_id: str) -> ResumeResponse | None:
        return self.repository.get(resume_id)
