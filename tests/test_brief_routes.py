from __future__ import annotations

from fastapi.testclient import TestClient


def test_brief_list_filters_by_tenant(client: TestClient) -> None:
    client.post(
        "/brief/generate",
        json={"role_spec": {"title": "Role A"}, "candidate_ids": []},
        headers={"x-user-role": "researcher", "x-tenant-id": "tenant_a", "x-user-id": "user_a"},
    )
    client.post(
        "/brief/generate",
        json={"role_spec": {"title": "Role B"}, "candidate_ids": []},
        headers={"x-user-role": "researcher", "x-tenant-id": "tenant_b", "x-user-id": "user_b"},
    )

    response = client.get("/brief", headers={"x-user-role": "researcher", "x-tenant-id": "tenant_a"})

    body = response.json()
    assert response.status_code == 200
    assert body["tenant_id"] == "tenant_a"
    assert all(item["tenant_id"] == "tenant_a" for item in body["briefs"])
