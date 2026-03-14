from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import settings


class JsonlAuditRepository:
    def __init__(self, path: str | None = None):
        self.path = Path(path or settings.audit_log_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: dict[str, Any]) -> None:
        line = json.dumps(event, ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as file_handle:
            file_handle.write(line + "\n")
