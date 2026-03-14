from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.models.auth import ApprovalStatus
from app.repositories.interfaces import StoredBrief


class BriefRepo:
    """
    MVP: file-backed storage under data/processed/briefs.
    """

    def __init__(self, root_dir: str | None = None):
        self.root = Path(root_dir or settings.brief_storage_dir)
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

    def list(
        self,
        *,
        tenant_id: str,
        project_id: str | None = None,
        approval_status: ApprovalStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[StoredBrief]:
        briefs: list[StoredBrief] = []
        matched = 0
        for path in sorted(self.root.glob("*.json"), reverse=True):
            try:
                brief = StoredBrief(**json.loads(path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            if brief.tenant_id != tenant_id:
                continue
            if project_id is not None and brief.project_id != project_id:
                continue
            if approval_status is not None and brief.approval_status != approval_status:
                continue
            if matched < offset:
                matched += 1
                continue
            briefs.append(brief)
            if len(briefs) >= limit:
                break
        return briefs

    def decide(
        self,
        brief_id: str,
        *,
        status: ApprovalStatus,
        decided_by: str,
        comment: str | None = None,
    ) -> StoredBrief | None:
        b = self.get(brief_id)
        if not b:
            return None
        now = datetime.now(timezone.utc).isoformat()
        updated = StoredBrief(
            brief_id=b.brief_id,
            markdown=b.markdown,
            role_spec=b.role_spec,
            citations=b.citations,
            generated_at=b.generated_at,
            tenant_id=b.tenant_id,
            project_id=b.project_id,
            created_by=b.created_by,
            approval_status=status,
            approval_notes=comment,
            approved_by=decided_by,
            approved_at=now,
        )
        self.save(updated)
        return updated
