from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.dependencies.auth import require_permission
from app.models.auth import AccessContext
from app.repositories.factory import get_audit_repository

router = APIRouter()

_audit_repo = get_audit_repository()


@router.get("")
def list_audit_events(
    access: AccessContext = Depends(require_permission("audit:view")),
    project_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    events = _audit_repo.list_events(
        tenant_id=access.tenant_id,
        project_id=project_id,
        event_type=event_type,
        limit=limit,
    )
    return {"events": events, "count": len(events), "tenant_id": access.tenant_id}
