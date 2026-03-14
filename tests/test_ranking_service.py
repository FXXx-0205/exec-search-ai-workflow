from __future__ import annotations

from app.services.ranking_service import RankingService


def test_ranking_service_exposes_version_and_weights() -> None:
    service = RankingService(
        weights={
            "skill_match": 0.4,
            "seniority_match": 0.2,
            "sector_relevance": 0.15,
            "functional_similarity": 0.15,
            "location_alignment": 0.05,
            "stability_signal": 0.05,
        },
        strategy_version="v-test",
    )

    ranked = service.score_candidates(
        {"required_skills": ["infrastructure"], "location": "sydney"},
        [
            {
                "candidate_id": "cand_1",
                "summary": "Infrastructure investing leader",
                "sectors": ["Infrastructure"],
                "location": "Sydney",
            }
        ],
    )

    assert ranked[0]["ranking_version"] == "v-test"
    assert ranked[0]["ranking_weights"]["skill_match"] == 0.4
