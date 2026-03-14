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
