from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.auth import ApprovalStatus
from app.repositories.interfaces import StoredBrief


def _sqlite_path(database_url: str) -> Path:
    if not database_url.startswith("sqlite:///"):
        raise ValueError(f"Unsupported database URL: {database_url}")
    path = Path(database_url.removeprefix("sqlite:///"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


class SQLiteRepository:
    def __init__(self, database_url: str):
        self.path = _sqlite_path(database_url)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection


class SqliteBriefRepository(SQLiteRepository):
    def __init__(self, database_url: str):
        super().__init__(database_url)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS briefs (
                    brief_id TEXT PRIMARY KEY,
                    markdown TEXT NOT NULL,
                    role_spec TEXT NOT NULL,
                    citations TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    project_id TEXT,
                    created_by TEXT NOT NULL,
                    approval_status TEXT NOT NULL,
                    approval_notes TEXT,
                    approved_by TEXT,
                    approved_at TEXT
                )
                """
            )

    def save(self, brief: StoredBrief) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO briefs (
                    brief_id, markdown, role_spec, citations, generated_at, tenant_id,
                    project_id, created_by, approval_status, approval_notes, approved_by, approved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    brief.brief_id,
                    brief.markdown,
                    json.dumps(brief.role_spec, ensure_ascii=False),
                    json.dumps(brief.citations, ensure_ascii=False),
                    brief.generated_at,
                    brief.tenant_id,
                    brief.project_id,
                    brief.created_by,
                    brief.approval_status,
                    brief.approval_notes,
                    brief.approved_by,
                    brief.approved_at,
                ),
            )

    def get(self, brief_id: str) -> StoredBrief | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM briefs WHERE brief_id = ?", (brief_id,)).fetchone()
        if row is None:
            return None
        return StoredBrief(
            brief_id=row["brief_id"],
            markdown=row["markdown"],
            role_spec=json.loads(row["role_spec"]),
            citations=json.loads(row["citations"]),
            generated_at=row["generated_at"],
            tenant_id=row["tenant_id"],
            project_id=row["project_id"],
            created_by=row["created_by"],
            approval_status=ApprovalStatus(row["approval_status"]),
            approval_notes=row["approval_notes"],
            approved_by=row["approved_by"],
            approved_at=row["approved_at"],
        )

    def decide(
        self,
        brief_id: str,
        *,
        status: ApprovalStatus,
        decided_by: str,
        comment: str | None = None,
    ) -> StoredBrief | None:
        brief = self.get(brief_id)
        if brief is None:
            return None
        updated = StoredBrief(
            brief_id=brief.brief_id,
            markdown=brief.markdown,
            role_spec=brief.role_spec,
            citations=brief.citations,
            generated_at=brief.generated_at,
            tenant_id=brief.tenant_id,
            project_id=brief.project_id,
            created_by=brief.created_by,
            approval_status=status,
            approval_notes=comment,
            approved_by=decided_by,
            approved_at=datetime.now(timezone.utc).isoformat(),
        )
        self.save(updated)
        return updated


class SqliteAuditRepository(SQLiteRepository):
    def __init__(self, database_url: str):
        super().__init__(database_url)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    tenant_id TEXT,
                    project_id TEXT,
                    actor_id TEXT,
                    payload TEXT NOT NULL,
                    ts TEXT NOT NULL
                )
                """
            )

    def append(self, event: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    event_type, request_id, tenant_id, project_id, actor_id, payload, ts
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["event_type"],
                    event["request_id"],
                    event.get("tenant_id"),
                    event.get("project_id"),
                    event.get("actor_id"),
                    json.dumps(event.get("payload", {}), ensure_ascii=False),
                    event["ts"],
                ),
            )
