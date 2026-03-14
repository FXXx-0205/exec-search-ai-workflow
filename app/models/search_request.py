from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.auth import ApprovalStatus


class IntakeRequest(BaseModel):
    raw_input: str = Field(min_length=1, max_length=8000)
    project_id: str | None = None


class CandidatesRequest(BaseModel):
    project_id: str | None = None
    role_spec: dict
    provider_filters: dict | None = None


class RankRequest(BaseModel):
    role_spec: dict
    candidate_ids: list[str]


class BriefGenerateRequest(BaseModel):
    project_id: str | None = None
    role_spec: dict | None = None
    candidate_ids: list[str] | None = None


class BriefApprovalRequest(BaseModel):
    status: ApprovalStatus = ApprovalStatus.APPROVED
    comment: str | None = Field(default=None, max_length=1000)
