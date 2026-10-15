import time
import uuid

from fastapi import Request


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
