import logging

from fastapi import FastAPI

from app.api.middleware import reject_oversized_body, request_context
from app.api.router import router
from app.config import get_settings

# format="%(message)s" prints only the JSON, nothing in front of it.
logging.basicConfig(format="%(message)s")
# Apply LOG_LEVEL to our "app" logger only, so library logs (Azure, httpx) stay quiet.
logging.getLogger("app").setLevel(get_settings().log_level)

app = FastAPI(title="resume-parser")
# The last middleware added runs first, so request_context wraps everything.
app.middleware("http")(reject_oversized_body)
app.middleware("http")(request_context)
app.include_router(router)
