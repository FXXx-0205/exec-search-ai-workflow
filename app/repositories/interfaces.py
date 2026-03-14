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
    ) -> list[dict[str, Any]]: ...
