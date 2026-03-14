from __future__ import annotations

from fastapi.testclient import TestClient


def test_audit_list_returns_tenant_scoped_events(client: TestClient) -> None:
    client.post(
        "/brief/generate",
        json={"role_spec": {"title": "Role A"}, "candidate_ids": []},
        headers={"x-user-role": "researcher", "x-tenant-id": "tenant_a", "x-user-id": "user_a"},
    )

    response = client.get("/audit", headers={"x-user-role": "consultant", "x-tenant-id": "tenant_a"})

    body = response.json()
    assert response.status_code == 200
    assert body["count"] >= 1
    assert all(event["tenant_id"] == "tenant_a" for event in body["events"])


def test_audit_list_supports_filters_and_pagination(client: TestClient) -> None:
    client.post(
        "/brief/generate",
        json={"role_spec": {"title": "Role Filter"}, "candidate_ids": []},
        headers={"x-user-role": "researcher", "x-tenant-id": "tenant_filter", "x-user-id": "user_filter"},
    )

    response = client.get(
        "/audit?event_type=brief_generated&limit=1&offset=0",
        headers={"x-user-role": "consultant", "x-tenant-id": "tenant_filter"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["limit"] == 1
    assert body["offset"] == 0
    assert body["count"] == 1
    assert all(event["event_type"] == "brief_generated" for event in body["events"])
