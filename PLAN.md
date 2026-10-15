# Resume Parser API — Plan

## Goal

A FastAPI service where a user uploads a PDF or DOCX resume (up to 20 MB). The service validates it, extracts the text, and returns a structured profile (contact info, skills, experience) as JSON. Text extraction will ultimately be done by Azure AI Document Intelligence.

## Status

| Area | Status |
| --- | --- |
| Project layout (router / service / parser / repository) | Done |
| Upload validation (type, size, magic bytes) | Done |
| Local text extraction (pypdf, python-docx) | Done |
| Heuristic profile builder | Done |
| Request ID + timing middleware, JSON logging | Done |
| Consistent JSON error handling | Done |
| Settings from env vars, `/health` | Done |
| pytest suite (18 tests) | Done |
| GitHub Actions workflow | Written, not yet run (no git repo) |
| Azure Document Intelligence extractor | **TODO — the hand-off** |

## Architecture

```
HTTP request
  -> RequestContextMiddleware      (request ID, timing, access log)
  -> Router: POST /resumes         (app/routers/resumes.py)
       -> Depends(validated_upload)    (app/dependencies.py)
       -> Depends(get_resume_service)
  -> ResumeService.process         (app/services/resume_service.py)
       -> run_in_threadpool(extractor.extract)   (app/parsers/local.py | azure.py)
       -> run_in_threadpool(build_profile)       (app/parsers/profile_builder.py)
       -> repository.save                        (app/repositories/resume_repository.py)
  -> ResumeResponse (Pydantic) serialized to JSON
  -> On error: exception handlers   (app/errors.py)
```

Why each layer exists:

- **Router**: HTTP concerns only (paths, status codes, response models). No business logic.
- **Service**: Orchestrates the use case. Knows nothing about HTTP, so it can be reused from a CLI or worker.
- **Parser** (`TextExtractor` protocol): Isolates the extraction backend, which lets you swap local for Azure with one env var.
- **Repository** (`ResumeRepository` protocol): Isolates storage, which lets you swap in-memory for Postgres without touching the service.

Every dependency is provided through `Depends`, so tests replace them with `app.dependency_overrides`.

## Concept map (where to look)

| Concept | Where it lives |
| --- | --- |
| ASGI vs WSGI, Uvicorn | `app/middleware.py` is raw ASGI (`scope`, `receive`, `send`); run with `uvicorn app.main:app` |
| Request lifecycle | Middleware -> routing -> dependencies -> validation -> handler -> `response_model` serialization -> exception handlers |
| Pydantic request/response models | `app/schemas.py` |
| Settings from env | `app/config.py` (`pydantic-settings`, cached with `lru_cache`) |
| Dependency injection | `app/dependencies.py` |
| Sync vs async / event loop blocking | `ResumeService.process` uses `run_in_threadpool` for CPU-bound parsing |
| Structured logging + request IDs | `app/logging_config.py` (JSON formatter, `ContextVar`) |
| Global error handling | `app/errors.py` |

## Remaining work

### 1. Azure Document Intelligence hand-off (required)

File: `app/parsers/azure.py`

1. Create a Document Intelligence resource in Azure and copy the endpoint and key.
2. Add `azure-ai-documentintelligence` to `requirements.txt` and install it.
3. In `__init__`, create `DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))`.
4. In `extract`:
   - Call `self.client.begin_analyze_document("prebuilt-read", body=content).result()`.
   - Return `result.content`.
   - Wrap `azure.core.exceptions.HttpResponseError` in `ParserError` so it becomes a consistent 422 JSON error.
   - Raise `ParserError` if the returned text is empty.
5. Set `EXTRACTOR_BACKEND=azure`, `AZURE_DI_ENDPOINT` and `AZURE_DI_KEY` in `.env`.
6. Add tests:
   - A unit test that mocks the client and checks that the text is returned and errors are mapped.
   - An optional integration test, marked `@pytest.mark.azure` and skipped when credentials are absent.

Notes:

- There is no prebuilt resume model in API version 2024-11-30. Use `prebuilt-read` for plain text, or `prebuilt-layout` if you want paragraphs and section roles (better input for the profile builder).
- The sync client is fine here because `extract` already runs in a worker thread. An alternative to learn from is the async client (`azure.ai.documentintelligence.aio`) with an `async def extract`. That requires changing the protocol and the service so the call is awaited directly instead of wrapped in `run_in_threadpool`.
- Consider a timeout on the poller and mapping timeouts to a 504 or 422.

### 2. Get CI running

1. Run `git init`, commit, and push to GitHub.
2. Confirm `.github/workflows/ci.yml` passes.

### 3. Optional improvements

- **Better profile extraction**: use `prebuilt-layout` paragraph roles (`title`, `sectionHeading`) instead of plain-text heuristics, or send the text to an LLM with a Pydantic schema for structured output.
- **Persistent storage**: implement a `ResumeRepository` backed by SQLite or Postgres (SQLAlchemy async), injected the same way.
- **True streaming upload**: parse multipart yourself from `request.stream()` (e.g. `streaming-form-data`) so oversize bodies are rejected without Starlette spooling them to disk first.
- **Lifespan**: create the Azure client once in a FastAPI `lifespan` handler and close it on shutdown, instead of per request.
- **Observability**: add a `/ready` endpoint that checks Azure reachability; propagate the request ID to Azure calls via headers.
- **Linting/types**: add `ruff` and `mypy` to CI.

## Running

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload       # http://localhost:8000/docs
pytest -q
```

## Error contract

All errors return:

```json
{"error": {"code": "...", "message": "...", "request_id": "..."}}
```

| Code | Status | When |
| --- | --- | --- |
| `unsupported_file_type` | 415 | Wrong extension, content type, or magic bytes |
| `file_too_large` | 413 | Over `MAX_UPLOAD_BYTES` |
| `empty_file` | 400 | Zero-byte upload |
| `parser_failed` | 422 | Extractor could not read the document |
| `validation_error` | 422 | Missing or malformed request fields |
| `not_found` | 404 | Unknown resume ID |
| `internal_error` | 500 | Anything unexpected |
