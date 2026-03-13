from __future__ import annotations

from pydantic import BaseModel, Field


class IntakeRequest(BaseModel):
    raw_input: str = Field(min_length=1, max_length=8000)


class CandidatesRequest(BaseModel):
    project_id: str | None = None
    role_spec: dict


class RankRequest(BaseModel):
    role_spec: dict
    candidate_ids: list[str]


class BriefGenerateRequest(BaseModel):
    project_id: str | None = None
    role_spec: dict | None = None
    candidate_ids: list[str] | None = None

