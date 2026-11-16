"""SQLite project history with no secret persistence."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from src.models.schemas import ProjectRecord


class HistoryService:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS projects (project_id TEXT PRIMARY KEY, topic TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, output_path TEXT, thumbnail_path TEXT)")

    def upsert(self, project_id: str, topic: str, status: str, output_path: str | None = None, thumbnail_path: str | None = None) -> ProjectRecord:
        created_at = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute("INSERT INTO projects(project_id, topic, status, created_at, output_path, thumbnail_path) VALUES(?, ?, ?, ?, ?, ?) ON CONFLICT(project_id) DO UPDATE SET status=excluded.status, output_path=excluded.output_path, thumbnail_path=excluded.thumbnail_path", (project_id, topic, status, created_at, output_path, thumbnail_path))
        return ProjectRecord(project_id=project_id, topic=topic, status=status, created_at=created_at, output_path=output_path, thumbnail_path=thumbnail_path)

    def list_projects(self, limit: int = 50) -> list[ProjectRecord]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM projects ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [ProjectRecord(**dict(row)) for row in rows]

