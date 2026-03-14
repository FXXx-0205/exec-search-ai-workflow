from __future__ import annotations

from app.adapters.ats import CandidateProfile
from app.services.candidate_service import CandidateService


def test_candidate_service_normalizes_extended_adapter_fields() -> None:
    service = CandidateService()
    normalized = service._normalize_adapter_candidate(
        CandidateProfile(
            tenant_id="tenant_1",
            candidate_id="cand_1",
            full_name="Jamie Ng",
            current_title="Infrastructure Portfolio Manager",
            current_company="Example Asset Management",
            primary_email="jamie@example.com",
            location="Sydney, Australia",
            application_ids=["9001"],
            tag_names=["infrastructure", "super fund"],
            attachment_count=2,
            source_system="greenhouse",
            source_id="cand_1",
            synced_at=__import__("datetime").datetime.now(),
        )
    )

    assert normalized["current_company"] == "Example Asset Management"
    assert normalized["location"] == "Sydney, Australia"
    assert "Application IDs: 9001" in normalized["evidence"]
    assert "Tags: infrastructure, super fund" in normalized["evidence"]
    assert "Attachments available: 2" in normalized["evidence"]
