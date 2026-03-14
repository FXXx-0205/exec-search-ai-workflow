from __future__ import annotations

from app.llm.anthropic_client import ClaudeClient
from app.services.brief_service import BriefService


def test_brief_service_returns_prompt_metadata_and_context() -> None:
    service = BriefService(llm=ClaudeClient(api_key=None))

    result = service.generate_markdown(
        role_spec={"title": "Head of Infrastructure"},
        ranked_candidates=[{"candidate_id": "cand_1", "fit_score": 91, "reasoning": ["Strong fit"]}],
        retrieval_context=[{"doc_id": "doc_1", "text": "Market context", "source": "doc-src"}],
        generation_context={"tenant_id": "tenant_a"},
    )

    assert result["prompt"]["id"] == "brief_generator"
    assert result["generation_context"]["tenant_id"] == "tenant_a"
    assert "Role Summary" in result["markdown"]
