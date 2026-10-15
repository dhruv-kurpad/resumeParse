from fastapi import FastAPI

from app.middleware import request_context
from app.router import router


app = FastAPI(title="resume-parser")
app.middleware("http")(request_context)
app.include_router(router)
