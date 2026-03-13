from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from app.config import settings


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str


class ClaudeClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key if api_key is not None else settings.anthropic_api_key
        self._client = None

        if self.api_key:
            from anthropic import Anthropic

            self._client = Anthropic(api_key=self.api_key)

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 1200,
        extra: dict[str, Any] | None = None,
    ) -> str:
        if not self._client:
            return self._mock(system_prompt=system_prompt, user_prompt=user_prompt)

        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        if extra:
            kwargs.update(extra)

        resp = self._client.messages.create(**kwargs)
        parts: list[str] = []
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return "\n".join(parts).strip()

    def _mock(self, system_prompt: str, user_prompt: str) -> str:
        # 无 key 时用于 demo：只做极简规则解析/生成，保证端到端能跑通
        if "structured role specification" in system_prompt:
            lower = user_prompt.lower()
            role = {
                "title": "Infrastructure Portfolio Manager" if "infrastructure" in lower else "Executive Role",
                "seniority": "Senior" if "senior" in lower else "Unspecified",
                "sector": "Funds Management" if "fund" in lower or "asset" in lower else "Unspecified",
                "location": "Australia" if "australia" in lower else "Unspecified",
                "required_skills": ["Institutional portfolio management"],
                "preferred_skills": [],
                "search_keywords": ["infrastructure", "portfolio manager", "institutional"],
                "disqualifiers": [],
            }
            return json.dumps(role, ensure_ascii=False)

        if "briefing note" in system_prompt:
            return (
                "## 1. Role Summary\n"
                f"{user_prompt}\n\n"
                "## 2. Market Overview\n"
                "Evidence is limited in demo mode; treat as draft.\n\n"
                "## 3. Candidate Landscape\n"
                "See ranked shortlist below.\n\n"
                "## 4. Recommended Search Strategy\n"
                "- Use targeted mapping across relevant firms\n"
                "- Prioritize directly evidenced skill match\n\n"
                "## 5. Risks / Open Questions\n"
                "- Evidence gaps: leadership scope, mobility, exact mandate type\n"
            )

        return user_prompt

