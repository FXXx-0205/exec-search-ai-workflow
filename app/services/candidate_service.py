from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.adapters.ats import ATSAdapter
from app.config import settings


class CandidateService:
    def __init__(self, demo_data_dir: str | None = None, ats_adapter: ATSAdapter | None = None):
        self.demo_data_dir = demo_data_dir or settings.demo_data_dir
        self.ats_adapter = ats_adapter

    def load_demo_candidates(self) -> list[dict[str, Any]]:
        path = Path(self.demo_data_dir) / "sample_candidates" / "candidates.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def load_candidates(self, role_spec: dict[str, Any], tenant_id: str | None = None) -> list[dict[str, Any]]:
        if self.ats_adapter:
            filters = {
                "keywords": role_spec.get("search_keywords") or [],
                "required_skills": role_spec.get("required_skills") or [],
                "tenant_id": tenant_id,
            }
            adapter_candidates = self.ats_adapter.search_candidates(filters=filters)
            if adapter_candidates:
                return [self._normalize_adapter_candidate(candidate) for candidate in adapter_candidates]
        return self.load_demo_candidates()

    def filter_candidates(self, role_spec: dict[str, Any], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        keywords = [k.lower() for k in (role_spec.get("search_keywords") or []) if isinstance(k, str)]
        required = [k.lower() for k in (role_spec.get("required_skills") or []) if isinstance(k, str)]

        def score(c: dict[str, Any]) -> int:
            blob = json.dumps(c, ensure_ascii=False).lower()
            return sum(1 for k in keywords if k and k in blob) + sum(2 for r in required if r and r in blob)

        scored = [(score(c), c) for c in candidates]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for s, c in scored if s > 0] or candidates[:20]

    def _normalize_adapter_candidate(self, candidate: Any) -> dict[str, Any]:
        return {
            "candidate_id": candidate.candidate_id,
            "full_name": candidate.full_name,
            "current_title": candidate.current_title,
            "current_company": "Unknown",
            "location": "Unknown",
            "sectors": [],
            "functions": [],
            "summary": f"{candidate.current_title} sourced from {candidate.source_system}",
            "evidence": [],
            "source_urls": [],
            "confidence_score": 0.6,
            "source_system": candidate.source_system,
        }
