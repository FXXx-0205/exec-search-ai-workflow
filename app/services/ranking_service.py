from __future__ import annotations

from typing import Any

from app.config import settings


class RankingService:
    def __init__(
        self,
        *,
        weights: dict[str, float] | None = None,
        strategy_version: str | None = None,
    ):
        self.weights = weights or settings.ranking_weights()
        self.strategy_version = strategy_version or settings.ranking_strategy_version

    def score_candidates(self, role_spec: dict[str, Any], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        required = [s.lower() for s in (role_spec.get("required_skills") or []) if isinstance(s, str)]
        preferred = [s.lower() for s in (role_spec.get("preferred_skills") or []) if isinstance(s, str)]
        location = (role_spec.get("location") or "").lower()

        def has_any(blob: str, items: list[str]) -> int:
            return sum(1 for it in items if it and it in blob)

        ranked: list[dict[str, Any]] = []
        for c in candidates:
            blob = (c.get("summary") or "").lower() + " " + " ".join((c.get("sectors") or [])).lower()
            required_hit = has_any(blob, required)
            preferred_hit = has_any(blob, preferred)
            loc_hit = 1 if location and location in (c.get("location") or "").lower() else 0

            skill_match = min(1.0, required_hit / max(1, len(required))) if required else 0.5
            sector_relevance = 0.7 if (c.get("sectors") or []) else 0.4
            location_alignment = 1.0 if loc_hit else 0.4
            seniority_match = 0.6
            functional_similarity = 0.6
            stability_signal = 0.5

            final = (
                self.weights["skill_match"] * skill_match
                + self.weights["seniority_match"] * seniority_match
                + self.weights["sector_relevance"] * sector_relevance
                + self.weights["functional_similarity"] * functional_similarity
                + self.weights["location_alignment"] * location_alignment
                + self.weights["stability_signal"] * stability_signal
            )

            reasoning = []
            if required_hit:
                reasoning.append("Direct evidence of required skill(s) in summary/evidence.")
            if preferred_hit:
                reasoning.append("Some preferred skill signals found.")
            if loc_hit:
                reasoning.append("Location aligns with role requirement.")

            risks = []
            if not required_hit and required:
                risks.append("Limited direct evidence for required skills.")
            if not loc_hit and location:
                risks.append("Location alignment unclear.")

            ranked.append(
                {
                    "candidate_id": c.get("candidate_id"),
                    "fit_score": round(final * 100, 1),
                    "skill_match_score": round(skill_match * 100, 1),
                    "seniority_score": round(seniority_match * 100, 1),
                    "sector_relevance_score": round(sector_relevance * 100, 1),
                    "location_score": round(location_alignment * 100, 1),
                    "ranking_version": self.strategy_version,
                    "ranking_weights": self.weights,
                    "reasoning": reasoning or ["General alignment based on available signals."],
                    "risks": risks,
                }
            )

        ranked.sort(key=lambda x: x["fit_score"], reverse=True)
        return ranked
