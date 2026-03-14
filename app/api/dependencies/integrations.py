from __future__ import annotations

from app.config import settings
from app.core.exceptions import ValidationError
from app.adapters.ats import ATSAdapter
from app.adapters.crm import CRMAdapter
from app.adapters.doc_store import DocumentStoreAdapter
from app.adapters.mock import MockATSAdapter, MockCRMAdapter, MockDocumentStoreAdapter

_crm = MockCRMAdapter()
_ats = MockATSAdapter()
_doc_store = MockDocumentStoreAdapter()


def get_crm_adapter() -> CRMAdapter:
    if settings.crm_provider != "mock":
        raise ValidationError("Unsupported CRM provider.", details={"provider": settings.crm_provider})
    return _crm


def get_ats_adapter() -> ATSAdapter:
    if settings.ats_provider != "mock":
        raise ValidationError("Unsupported ATS provider.", details={"provider": settings.ats_provider})
    return _ats


def get_document_store_adapter() -> DocumentStoreAdapter:
    if settings.doc_store_provider != "mock":
        raise ValidationError("Unsupported document store provider.", details={"provider": settings.doc_store_provider})
    return _doc_store
