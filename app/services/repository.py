import sqlite3
from typing import Protocol

from app.schemas import ResumeResponse
'''
Note: With a real database server over the network,
Need an async driver or run_in_threadpool.
Implement later
'''

class ResumeRepository(Protocol):
    def save(self, resume: ResumeResponse) -> None: ...

    def get(self, resume_id: str) -> ResumeResponse | None: ...


class SqliteResumeRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS resumes (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    data TEXT NOT NULL
                )
                """
            )

    def save(self, resume: ResumeResponse) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO resumes (id, filename, data) VALUES (?, ?, ?)",
                (resume.id, resume.filename, resume.model_dump_json()),
            )

    def get(self, resume_id: str) -> ResumeResponse | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT data FROM resumes WHERE id = ?", (resume_id,)).fetchone()
        if row is None:
            return None
        return ResumeResponse.model_validate_json(row[0])
