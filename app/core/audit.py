from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    request_id: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "request_id": self.request_id,
            "payload": self.payload,
            "ts": datetime.now(timezone.utc).isoformat(),
        }


class AuditLogger:
    def __init__(self, path: str | None = None):
        self.path = Path(path or getattr(settings, "audit_log_path", "./data/audit.jsonl"))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: AuditEvent) -> None:
        line = json.dumps(event.to_dict(), ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

