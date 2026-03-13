from __future__ import annotations

from typing import Any

from app.retrieval.vector_store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore):
        self.store = store

    def retrieve_for_role(self, role_spec: dict[str, Any], top_k: int = 5) -> list[dict[str, Any]]:
        query_text = " ".join(role_spec.get("search_keywords") or []) or (role_spec.get("title") or "")
        where = None
        sector = role_spec.get("sector")
        if sector:
            where = {"sector": sector}

        # 先尝试带 sector 过滤的检索，如果没有结果则回退到不加过滤的查询
        results = self.store.query(query_text=query_text, top_k=top_k, where=where)
        if not results and where is not None:
            results = self.store.query(query_text=query_text, top_k=top_k, where=None)
        return results

