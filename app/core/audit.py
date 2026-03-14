from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.repositories.factory import get_audit_repository
from app.repositories.interfaces import AuditRepository


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    request_id: str
    payload: dict[str, Any]
    tenant_id: str | None = None
    project_id: str | None = None
    actor_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        event = {
            "event_type": self.event_type,
            "request_id": self.request_id,
            "payload": self.payload,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        if self.tenant_id is not None:
            event["tenant_id"] = self.tenant_id
        if self.project_id is not None:
            event["project_id"] = self.project_id
        if self.actor_id is not None:
            event["actor_id"] = self.actor_id
        return event

class AuditLogger:
    def __init__(self, repository: AuditRepository | None = None):
        self.repository = repository or get_audit_repository()

    def log(self, event: AuditEvent) -> None:
        self.repository.append(json.loads(json.dumps(event.to_dict(), ensure_ascii=False)))
