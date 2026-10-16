import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse

from app.dependencies import MAX_UPLOAD_BYTES

# Multipart adds boundaries and headers around the file itself.
MULTIPART_OVERHEAD_BYTES = 64 * 1024


async def reject_oversized_body(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit():
        if int(content_length) > MAX_UPLOAD_BYTES + MULTIPART_OVERHEAD_BYTES:
            return JSONResponse(status_code=413, content={"detail": f"File exceeds {MAX_UPLOAD_BYTES} bytes"})
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
    print(f"{request_id} {request.method} {request.url.path} {response.status_code} {duration_ms:.2f}ms")
    return response
