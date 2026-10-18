import json
import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import get_settings

logger = logging.getLogger("app")

# Multipart adds boundaries and headers around the file itself.
MULTIPART_OVERHEAD_BYTES = 64 * 1024


async def reject_oversized_body(request: Request, call_next):
    max_upload_bytes = get_settings().max_upload_bytes
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit():
        if int(content_length) > max_upload_bytes + MULTIPART_OVERHEAD_BYTES:
            return JSONResponse(status_code=413, content={"detail": f"File exceeds {max_upload_bytes} bytes"})
    return await call_next(request)


#Method called at request before sending to endpoint
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    response.headers["x-request-id"] = request_id
    response.headers["x-process-time-ms"] = f"{duration_ms:.2f}"
    logger.info(json.dumps({
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration_ms, 2),
    }))
    return response
