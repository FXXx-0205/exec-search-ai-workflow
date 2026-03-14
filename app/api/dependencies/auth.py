from __future__ import annotations

from fastapi import Depends, Header

from app.core.exceptions import ForbiddenError, ValidationError
from app.models.auth import AccessContext, ROLE_PERMISSIONS, UserIdentity, UserRole


def get_access_context(
    x_user_id: str | None = Header(default=None),
    x_user_email: str | None = Header(default=None),
    x_user_name: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
    x_project_id: str | None = Header(default=None),
) -> AccessContext:
    role_value = (x_user_role or "researcher").lower()
    try:
        role = UserRole(role_value)
    except ValueError as exc:
        raise ValidationError("Unsupported user role.", details={"role": role_value}) from exc

    return AccessContext(
        tenant_id=x_tenant_id or "demo-tenant",
        project_id=x_project_id,
        actor=UserIdentity(
            user_id=x_user_id or "demo-user",
            email=x_user_email or "demo@example.com",
            display_name=x_user_name or "Demo User",
            role=role,
        ),
    )


def require_permission(permission: str):
    def dependency(context: AccessContext = Depends(get_access_context)) -> AccessContext:
        allowed = ROLE_PERMISSIONS.get(context.actor.role, set())
        if permission not in allowed:
            raise ForbiddenError(
                "You do not have permission to perform this action.",
                details={"required_permission": permission, "role": context.actor.role},
            )
        return context

    return dependency
