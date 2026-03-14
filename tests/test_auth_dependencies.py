from __future__ import annotations

from app.api.dependencies.auth import get_access_context
from app.core.exceptions import ValidationError


def test_invalid_user_role_raises_validation_error() -> None:
    try:
        get_access_context(x_user_role="invalid-role")
    except ValidationError as exc:
        assert exc.code == "validation_error"
    else:
        raise AssertionError("Expected ValidationError for invalid role")
