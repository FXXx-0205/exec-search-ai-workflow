from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.llm.anthropic_client import ClaudeClient
from app.models.search_request import BriefGenerateRequest
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import VectorStore
from app.repositories.brief_repo import BriefRepo, StoredBrief
from app.services.brief_service import BriefService
from app.services.candidate_service import CandidateService
from app.services.ranking_service import RankingService

router = APIRouter()

_llm = ClaudeClient()
_brief = BriefService(llm=_llm)
_candidates = CandidateService()
_ranker = RankingService()
_store = VectorStore()
_retriever = Retriever(store=_store)
_repo = BriefRepo()


@router.post("/generate")
def generate(req: BriefGenerateRequest) -> dict:
    role_spec = req.role_spec or {"title": "Unspecified", "search_keywords": []}
    pool = _candidates.load_demo_candidates()
    by_id = {c.get("candidate_id"): c for c in pool}
    selected = [by_id[cid] for cid in (req.candidate_ids or []) if cid in by_id] or pool
    ranked = _ranker.score_candidates(role_spec, selected)
    retrieval_context = _retriever.retrieve_for_role(role_spec, top_k=5)
    out = _brief.generate_markdown(role_spec=role_spec, ranked_candidates=ranked, retrieval_context=retrieval_context)
    _repo.save(
        StoredBrief(
            brief_id=out["brief_id"],
            markdown=out["markdown"],
            role_spec=role_spec,
            citations=out.get("citations", []),
            generated_at=out["generated_at"],
            approved=False,
        )
    )
    return out


@router.post("/approve/{brief_id}")
def approve(brief_id: str) -> dict:
    b = _repo.approve(brief_id)
    if not b:
        raise HTTPException(status_code=404, detail="brief not found")
    return {"brief_id": b.brief_id, "approved": b.approved, "approved_at": b.approved_at}


@router.get("/{brief_id}")
def get_brief(brief_id: str) -> dict:
    b = _repo.get(brief_id)
    if not b:
        raise HTTPException(status_code=404, detail="brief not found")
    return {
        "brief_id": b.brief_id,
        "markdown": b.markdown,
        "approved": b.approved,
        "approved_at": b.approved_at,
        "generated_at": b.generated_at,
        "citations": b.citations,
    }


@router.get("/{brief_id}/export")
def export_brief(brief_id: str) -> dict:
    """
    Client-facing export gate: must be approved.
    """
    b = _repo.get(brief_id)
    if not b:
        raise HTTPException(status_code=404, detail="brief not found")
    if not b.approved:
        raise HTTPException(status_code=403, detail="brief not approved")
    return {"brief_id": b.brief_id, "markdown": b.markdown, "exported": True}

