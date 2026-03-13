from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StoredBrief:
    brief_id: str
    markdown: str
    role_spec: dict[str, Any]
    citations: list[str]
    generated_at: str
    approved: bool
    approved_at: str | None = None


class BriefRepo:
    """
    MVP: file-backed storage under data/processed/briefs.
    """

    def __init__(self, root_dir: str = "./data/processed/briefs"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, brief_id: str) -> Path:
        return self.root / f"{brief_id}.json"

    def save(self, brief: StoredBrief) -> None:
        self._path(brief.brief_id).write_text(
            json.dumps(brief.__dict__, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get(self, brief_id: str) -> StoredBrief | None:
        p = self._path(brief_id)
        if not p.exists():
            return None
        data = json.loads(p.read_text(encoding="utf-8"))
        return StoredBrief(**data)

    def approve(self, brief_id: str) -> StoredBrief | None:
        b = self.get(brief_id)
        if not b:
            return None
        now = datetime.now(timezone.utc).isoformat()
        approved = StoredBrief(
            brief_id=b.brief_id,
            markdown=b.markdown,
            role_spec=b.role_spec,
            citations=b.citations,
            generated_at=b.generated_at,
            approved=True,
            approved_at=now,
        )
        self.save(approved)
        return approved

