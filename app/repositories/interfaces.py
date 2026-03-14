from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from app.models.auth import ApprovalStatus


@dataclass(frozen=True)
class StoredBrief:
    brief_id: str
    markdown: str
    role_spec: dict[str, Any]
    citations: list[str]
    generated_at: str
    tenant_id: str
    project_id: str | None
    created_by: str
    approval_status: ApprovalStatus
    approval_notes: str | None = None
    approved_by: str | None = None
    approved_at: str | None = None


@dataclass(frozen=True)
class StoredCandidate:
    tenant_id: str
    candidate_id: str
    full_name: str
    current_title: str
    current_company: str | None
    location: str | None
    primary_email: str | None
    summary: str
    evidence: list[str]
    source_system: str
    source_id: str
    application_ids: list[str]
    tag_names: list[str]
    attachment_count: int
    synced_at: str


class BriefRepository(Protocol):
    def save(self, brief: StoredBrief) -> None: ...

    def get(self, brief_id: str) -> StoredBrief | None: ...

    def list(
        self,
        *,
        tenant_id: str,
        project_id: str | None = None,
        approval_status: ApprovalStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[StoredBrief]: ...

    def decide(
        self,
        brief_id: str,
        *,
        status: ApprovalStatus,
        decided_by: str,
        comment: str | None = None,
    ) -> StoredBrief | None: ...


class AuditRepository(Protocol):
    def append(self, event: dict[str, Any]) -> None: ...

    def list_events(
        self,
        *,
        tenant_id: str,
        project_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]: ...


class CandidateRepository(Protocol):
    def upsert_many(self, candidates: list[StoredCandidate]) -> None: ...

    def list(
        self,
        *,
        tenant_id: str,
        search_text: str | None = None,
        source_system: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredCandidate]: ...
