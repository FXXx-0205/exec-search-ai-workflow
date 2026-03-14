from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.adapters.ats import ATSAdapter
from app.config import settings
from app.repositories.interfaces import CandidateRepository


class CandidateService:
    def __init__(
        self,
        demo_data_dir: str | None = None,
        ats_adapter: ATSAdapter | None = None,
        candidate_repository: CandidateRepository | None = None,
    ):
        self.demo_data_dir = demo_data_dir or settings.demo_data_dir
        self.ats_adapter = ats_adapter
        self.candidate_repository = candidate_repository

    def load_demo_candidates(self) -> list[dict[str, Any]]:
        path = Path(self.demo_data_dir) / "sample_candidates" / "candidates.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def load_candidates(
        self,
        role_spec: dict[str, Any],
        tenant_id: str | None = None,
        provider_filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if self.candidate_repository and tenant_id:
            stored = self.candidate_repository.list(
                tenant_id=tenant_id,
                search_text=" ".join(role_spec.get("search_keywords") or []) or None,
                source_system=(provider_filters or {}).get("source_system"),
                limit=int((provider_filters or {}).get("limit") or 100),
            )
            if stored:
                return [self._normalize_stored_candidate(candidate) for candidate in stored]
        if self.ats_adapter:
            filters = {
                "keywords": role_spec.get("search_keywords") or [],
                "required_skills": role_spec.get("required_skills") or [],
                "tenant_id": tenant_id,
            }
            if provider_filters:
                filters.update(provider_filters)
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
            "current_company": candidate.current_company or "Unknown",
            "location": candidate.location or "Unknown",
            "sectors": [],
            "functions": [],
            "summary": self._build_summary(candidate),
            "evidence": self._build_evidence(candidate),
            "source_urls": [],
            "confidence_score": 0.6,
            "source_system": candidate.source_system,
        }

    def _normalize_stored_candidate(self, candidate: Any) -> dict[str, Any]:
        return {
            "candidate_id": candidate.candidate_id,
            "full_name": candidate.full_name,
            "current_title": candidate.current_title,
            "current_company": candidate.current_company or "Unknown",
            "location": candidate.location or "Unknown",
            "sectors": [],
            "functions": [],
            "summary": candidate.summary,
            "evidence": candidate.evidence,
            "source_urls": [],
            "confidence_score": 0.75,
            "source_system": candidate.source_system,
        }

    def _build_summary(self, candidate: Any) -> str:
        parts = [candidate.current_title]
        if getattr(candidate, "current_company", None):
            parts.append(f"at {candidate.current_company}")
        if getattr(candidate, "location", None):
            parts.append(f"based in {candidate.location}")
        parts.append(f"sourced from {candidate.source_system}")
        return " ".join(parts)

    def _build_evidence(self, candidate: Any) -> list[str]:
        evidence: list[str] = []
        if getattr(candidate, "primary_email", None):
            evidence.append(f"Primary email on record: {candidate.primary_email}")
        if getattr(candidate, "application_ids", None):
            evidence.append(f"Application IDs: {', '.join(candidate.application_ids)}")
        if getattr(candidate, "tag_names", None):
            evidence.append(f"Tags: {', '.join(candidate.tag_names)}")
        if getattr(candidate, "attachment_count", 0):
            evidence.append(f"Attachments available: {candidate.attachment_count}")
        return evidence
