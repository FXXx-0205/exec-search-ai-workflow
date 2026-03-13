from __future__ import annotations

from fastapi import APIRouter

from app.llm.anthropic_client import ClaudeClient
from app.models.search_request import CandidatesRequest, IntakeRequest, RankRequest
from app.retrieval.retriever import Retriever
from app.retrieval.vector_store import VectorStore
from app.workflows.candidate_search_graph import run_workflow
from app.services.candidate_service import CandidateService
from app.services.job_parser_service import JobParserService
from app.services.ranking_service import RankingService

router = APIRouter()

_llm = ClaudeClient()
_parser = JobParserService(llm=_llm)
_candidates = CandidateService()
_ranker = RankingService()
_store = VectorStore()
_retriever = Retriever(store=_store)


@router.post("/intake")
def intake(req: IntakeRequest) -> dict:
    role_spec = _parser.parse_role(req.raw_input)
    retrieval_context = _retriever.retrieve_for_role(role_spec, top_k=5)
    return {"role_spec": role_spec, "retrieval_context": retrieval_context, "vector_store_mode": _store.mode}


@router.post("/candidates")
def candidates(req: CandidatesRequest) -> dict:
    pool = _candidates.load_demo_candidates()
    filtered = _candidates.filter_candidates(req.role_spec, pool)
    return {"candidates": filtered, "count": len(filtered)}


@router.post("/rank")
def rank(req: RankRequest) -> dict:
    pool = _candidates.load_demo_candidates()
    by_id = {c.get("candidate_id"): c for c in pool}
    selected = [by_id[cid] for cid in req.candidate_ids if cid in by_id]
    ranked = _ranker.score_candidates(req.role_spec, selected or pool)
    return {"ranked_candidates": ranked, "count": len(ranked)}


@router.post("/run")
def run(req: IntakeRequest) -> dict:
    """
    Agentic demo entrypoint: run end-to-end workflow and return a compact result.
    """
    state = run_workflow(req.raw_input)
    return {
        "request_id": state.get("request_id"),
        "role_spec": state.get("parsed_role"),
        "retrieval_context": state.get("retrieval_context", []),
        "ranked_candidates": (state.get("ranking_results") or [])[:10],
        "brief_markdown": state.get("brief_draft"),
        "critique_feedback": state.get("critique_feedback", []),
    }

