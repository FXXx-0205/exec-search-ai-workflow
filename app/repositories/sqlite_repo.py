from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.auth import ApprovalStatus
from app.repositories.interfaces import StoredBrief, StoredCandidate


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

    def list(
        self,
        *,
        tenant_id: str,
        project_id: str | None = None,
        approval_status: ApprovalStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[StoredBrief]:
        query = "SELECT * FROM briefs WHERE tenant_id = ?"
        params: list[Any] = [tenant_id]
        if project_id is not None:
            query += " AND project_id = ?"
            params.append(project_id)
        if approval_status is not None:
            query += " AND approval_status = ?"
            params.append(approval_status)
        query += " ORDER BY generated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()
        return [
            StoredBrief(
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
            for row in rows
        ]

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

    def list_events(
        self,
        *,
        tenant_id: str,
        project_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM audit_events WHERE tenant_id = ?"
        params: list[Any] = [tenant_id]
        if project_id is not None:
            query += " AND project_id = ?"
            params.append(project_id)
        if event_type is not None:
            query += " AND event_type = ?"
            params.append(event_type)
        query += " ORDER BY ts DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [
            {
                "event_type": row["event_type"],
                "request_id": row["request_id"],
                "tenant_id": row["tenant_id"],
                "project_id": row["project_id"],
                "actor_id": row["actor_id"],
                "payload": json.loads(row["payload"]),
                "ts": row["ts"],
            }
            for row in rows
        ]


class SqliteCandidateRepository(SQLiteRepository):
    def __init__(self, database_url: str):
        super().__init__(database_url)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS candidates (
                    tenant_id TEXT NOT NULL,
                    candidate_id TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    current_title TEXT NOT NULL,
                    current_company TEXT,
                    location TEXT,
                    primary_email TEXT,
                    summary TEXT NOT NULL,
                    evidence TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    application_ids TEXT NOT NULL,
                    tag_names TEXT NOT NULL,
                    attachment_count INTEGER NOT NULL,
                    synced_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, candidate_id)
                )
                """
            )

    def upsert_many(self, candidates: list[StoredCandidate]) -> None:
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO candidates (
                    tenant_id, candidate_id, full_name, current_title, current_company, location,
                    primary_email, summary, evidence, source_system, source_id, application_ids,
                    tag_names, attachment_count, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        candidate.tenant_id,
                        candidate.candidate_id,
                        candidate.full_name,
                        candidate.current_title,
                        candidate.current_company,
                        candidate.location,
                        candidate.primary_email,
                        candidate.summary,
                        json.dumps(candidate.evidence, ensure_ascii=False),
                        candidate.source_system,
                        candidate.source_id,
                        json.dumps(candidate.application_ids, ensure_ascii=False),
                        json.dumps(candidate.tag_names, ensure_ascii=False),
                        candidate.attachment_count,
                        candidate.synced_at,
                    )
                    for candidate in candidates
                ],
            )

    def list(
        self,
        *,
        tenant_id: str,
        search_text: str | None = None,
        source_system: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredCandidate]:
        query = "SELECT * FROM candidates WHERE tenant_id = ?"
        params: list[Any] = [tenant_id]
        if source_system is not None:
            query += " AND source_system = ?"
            params.append(source_system)
        if search_text:
            query += " AND (lower(full_name) LIKE ? OR lower(current_title) LIKE ? OR lower(summary) LIKE ?)"
            pattern = f"%{search_text.lower()}%"
            params.extend([pattern, pattern, pattern])
        query += " ORDER BY synced_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [
            StoredCandidate(
                tenant_id=row["tenant_id"],
                candidate_id=row["candidate_id"],
                full_name=row["full_name"],
                current_title=row["current_title"],
                current_company=row["current_company"],
                location=row["location"],
                primary_email=row["primary_email"],
                summary=row["summary"],
                evidence=json.loads(row["evidence"]),
                source_system=row["source_system"],
                source_id=row["source_id"],
                application_ids=json.loads(row["application_ids"]),
                tag_names=json.loads(row["tag_names"]),
                attachment_count=int(row["attachment_count"]),
                synced_at=row["synced_at"],
            )
            for row in rows
        ]
