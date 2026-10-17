# Module 1: Web Frameworks (FastAPI) — Weeks 1–2

Goal: explain everything that happens between a request arriving and a response leaving.

**Outcome:** A resume upload API. User uploads a PDF or DOCX (≤ 20 MB); the service validates it, extracts the text, and returns a structured profile (contact info, skills, experience) as JSON.

**Done when:** I can whiteboard the full request path through my own service, and every route has a passing test in CI.

**Difficulty:** `[n/10]` after each task. 1 = seconds, 10 = several hours.

---

## Concepts

Tick each one when I can explain it out loud without notes.

- [ ] **ASGI vs WSGI**: what each is, why FastAPI is ASGI, what `scope` / `receive` / `send` are `[6/10]`
- [ ] **How Uvicorn runs an async app**: event loop, how it calls `app` for each request `[6/10]`
- [ ] **Request lifecycle**, in order: `[7/10]`
  - [ ] Routing `[2/10]`
  - [x] Middleware `[4/10]`
  - [ ] Dependency injection (`Depends`) `[6/10]`
  - [ ] Validation `[3/10]`
  - [ ] Handler `[2/10]`
  - [ ] Serialization (`response_model`) `[3/10]`
  - [ ] Exception handlers `[4/10]`
- [ ] **Pydantic models** for request and response validation `[4/10]`
- [ ] **Settings from environment variables** (`pydantic-settings`, `.env`) `[3/10]`
- [ ] **Project layout**: router, service, data-access layer, and *why* each layer exists `[5/10]`
- [ ] **Sync vs async handlers**: when to use `def` vs `async def` `[6/10]`
- [ ] **What blocks the event loop**: CPU-bound work, sync I/O, and how thread pools fix it `[7/10]`
- [ ] **Structured logging**: JSON logs, why they beat `print` `[3/10]`
- [x] **Request IDs**: why they exist, client-provided vs generated `[3/10]`
- [ ] **Global error handling**: one consistent JSON error shape `[4/10]`

---

## Implement

### 1. Skeleton
- [x] `app/main.py` creates the app `[1/10]`
- [x] `app/router.py` with `GET /health` `[1/10]`
- [x] `POST /resumes` accepts an `UploadFile` `[2/10]`
- [x] `.gitignore`, `requirements.txt` `[1/10]`
- [x] Repo pushed to GitHub `[2/10]`

### 2. Middleware
- [x] Request ID middleware (header in, header out, stored on `request.state`) `[3/10]`
- [x] Timing middleware (`x-process-time-ms` header + log line) `[2/10]`
- [ ] Decide: always generate the ID, or validate and reuse the client's `[2/10]`
- [ ] Replace `print` with structured JSON logging that includes the request ID `[5/10]`

### 3. Upload validation (Pydantic + dependencies)
- [x] Pydantic response model in place of `dict` `[2/10]`
- [x] `validated_upload` dependency: `[6/10]`
  - [x] Allow only `.pdf` / `.docx` extensions `[2/10]`
  - [x] Check the declared content type `[2/10]`
  - [x] Check magic bytes (`%PDF-`, `PK\x03\x04`) `[3/10]`
  - [x] Read in chunks and reject over 20 MB *while* streaming `[5/10]`
  - [x] Early reject using the `Content-Length` header `[4/10]`
  - [x] Reject empty files `[1/10]`
- [x] Return a `ValidatedUpload` Pydantic model to the handler `[3/10]`

### 4. Layered structure
- [x] `service.py`: `ResumeService` orchestrates extract → build profile → save `[4/10]`
- [x] `parser.py`: `TextExtractor` protocol + Azure implementation `[5/10]`
- [x] `profile.py`: text → `ResumeProfile` via Claude (contact, skills, experience, projects) `[4/10]`
- [x] `repository.py`: `ResumeRepository` protocol + in-memory implementation `[3/10]`
- [x] Wire everything with `Depends` so each piece can be swapped in tests `[6/10]`
- [x] `GET /resumes/{id}` returns a saved profile `[3/10]`

### 5. Don't block the event loop
- [x] Run text extraction with `run_in_threadpool` `[3/10]`
- [ ] Explain why: what would happen if parsing ran directly in `async def` `[6/10]`

### 6. Errors
- [ ] `AppError` base class with `code` and `status_code` `[3/10]`
- [ ] Specific errors: unsupported type (415), too large (413), empty (400), parser failed (422), not found (404) `[2/10]`
- [ ] Global exception handlers return `{"error": {"code", "message", "request_id"}}` `[4/10]`
- [ ] Handle `RequestValidationError` and unexpected `Exception` with the same shape `[4/10]`

### 7. Config
- [ ] `config.py` with `pydantic-settings` (`MAX_UPLOAD_BYTES`, `LOG_LEVEL`, extractor backend) `[3/10]`
- [ ] `.env.example` committed, `.env` gitignored `[1/10]`
- [ ] Inject settings with `Depends(get_settings)` `[3/10]`

### 8. Azure Document Intelligence (hand-off)
- [x] `AzureTextExtractor` implementing `TextExtractor` `[5/10]`
- [x] Use `prebuilt-read` via `azure-ai-documentintelligence` `[6/10]`
- [x] Map Azure errors to `ExtractionError` `[3/10]`
- [x] Add endpoint + key to `.env` and test with a real resume `[2/10]`

### 9. Tests
- [ ] `pytest` + FastAPI `TestClient` `[3/10]`
- [ ] Sample resumes (PDF + DOCX) as fixtures `[4/10]`
- [ ] Happy path: PDF and DOCX return a profile `[3/10]`
- [ ] Bad file type, spoofed magic bytes, empty file, oversize file `[4/10]`
- [ ] Parser failure returns the JSON error `[3/10]`
- [ ] Fake extractor injected via `dependency_overrides` `[5/10]`
- [ ] Middleware headers present `[2/10]`
- [ ] **Every route has at least one test** `[2/10]`

### 10. CI
- [ ] `.github/workflows/ci.yml` runs `pytest` on push and PR `[4/10]`
- [ ] CI is green `[3/10]`

---

## Deliverable

- [ ] `Dockerfile` `[4/10]`
- [ ] `docker-compose.yml`: `docker compose up` starts the API `[3/10]`
- [ ] `README.md` with a sample `curl` request and JSON response `[2/10]`
- [ ] Green CI badge in the README `[1/10]`

---

## Stretch

- [ ] Rebuild one router in Go (`net/http` + `chi`) `[8/10]`
- [ ] Write a short comparison: FastAPI vs Go (DI, validation, concurrency model, performance) `[5/10]`
- [ ] Custom timing middleware that exports per-route latency (e.g. Prometheus histogram on `/metrics`) `[6/10]`
- [ ] Read the FastAPI/Starlette source for dependency injection (`fastapi/dependencies/utils.py`, `solve_dependencies`) and write up how it resolves dependencies `[9/10]`

---

## Final check

- [ ] Whiteboard the full request path through my service, from Uvicorn to the response, naming every file it touches `[7/10]`
- [ ] Every route has a passing test in CI `[3/10]`
