from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import settings


def test_search_candidates_uses_access_context_and_mock_adapter(client: TestClient) -> None:
    response = client.post(
        "/search/candidates",
        json={"role_spec": {"search_keywords": ["portfolio"]}},
        headers={"x-user-role": "researcher", "x-tenant-id": "tenant_search"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["tenant_id"] == "tenant_search"
    assert body["count"] >= 1
    assert body["candidates"][0]["source_system"] == "mock-ats"


def test_search_run_requires_permission(client: TestClient) -> None:
    response = client.post(
        "/search/run",
        json={"raw_input": "Need a Head of Infrastructure"},
        headers={"x-user-role": "compliance", "x-tenant-id": "tenant_search"},
    )

    assert response.status_code == 200


def test_search_returns_validation_error_for_unsupported_provider(client: TestClient) -> None:
    settings.ats_provider = "unsupported"
    try:
        response = client.post(
            "/search/candidates",
            json={"role_spec": {"search_keywords": ["portfolio"]}},
            headers={"x-user-role": "researcher", "x-tenant-id": "tenant_search"},
        )
    finally:
        settings.ats_provider = "mock"

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
