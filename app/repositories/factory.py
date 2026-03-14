from __future__ import annotations

from app.config import settings
from app.repositories.audit_repo import JsonlAuditRepository
from app.repositories.brief_repo import BriefRepo
from app.repositories.interfaces import AuditRepository, BriefRepository
from app.repositories.sqlite_repo import SqliteAuditRepository, SqliteBriefRepository


def get_brief_repository() -> BriefRepository:
    if settings.storage_backend == "sqlite":
        return SqliteBriefRepository(settings.database_url)
    return BriefRepo()


def get_audit_repository() -> AuditRepository:
    if settings.storage_backend == "sqlite":
        return SqliteAuditRepository(settings.database_url)
    return JsonlAuditRepository()
