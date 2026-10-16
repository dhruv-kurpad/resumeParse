from fastapi import FastAPI

from app.middleware import reject_oversized_body, request_context
from app.router import router


app = FastAPI(title="resume-parser")
# The last middleware added runs first, so request_context wraps everything.
app.middleware("http")(reject_oversized_body)
app.middleware("http")(request_context)
app.include_router(router)
