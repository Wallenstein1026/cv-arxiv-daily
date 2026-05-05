from __future__ import annotations

import json
import os
import re
from typing import List

from research_skill.schemas.models import Brief, RankedPaper

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


SYSTEM_PROMPT = (
    "You are a research analyst. "
    "Return strict JSON with keys: problem, method, key_findings, limitations, why_relevant_to_query, confidence. "
    "confidence must be a number between 0 and 1. key_findings and limitations are arrays of short strings."
)


def _first_sentences(text: str, n: int = 3) -> List[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    return [c.strip() for c in chunks if c.strip()][:n]


class BriefSummarizer:
    def __init__(
        self,
        enabled: bool,
        provider: str,
        model: str,
        temperature: float = 0.2,
        max_output_tokens: int = 500,
    ) -> None:
        self.enabled = enabled
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.client = self._build_client()

    def _build_client(self):
        if not self.enabled:
            return None
        if self.provider != "openai":
            return None
        if OpenAI is None:
            return None
        if not os.getenv("OPENAI_API_KEY"):
            return None
        return OpenAI()

    def summarize(self, query: str, ranked_papers: List[RankedPaper], top_k: int) -> List[RankedPaper]:
        if not ranked_papers:
            return ranked_papers

        limit = min(top_k, len(ranked_papers))
        for idx in range(limit):
            ranked_papers[idx].brief = self._summarize_one(query=query, item=ranked_papers[idx])
        return ranked_papers

    def _summarize_one(self, query: str, item: RankedPaper) -> Brief:
        if self.client is None:
            return self._extractive_brief(query, item)

        prompt = (
            f"Query: {query}\n"
            f"Title: {item.paper.title}\n"
            f"Abstract: {item.paper.abstract}\n"
            f"Matched Keywords: {', '.join(item.matched_keywords)}\n"
            "Output JSON only."
        )

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_output_tokens,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            text = completion.choices[0].message.content
            data = json.loads(text)
            return self._coerce_brief(data)
        except Exception:
            return self._extractive_brief(query, item)

    def _coerce_brief(self, data: dict) -> Brief:
        def _as_list(v):
            if isinstance(v, list):
                return [str(x) for x in v if str(x).strip()]
            if isinstance(v, str) and v.strip():
                return [v.strip()]
            return []

        confidence_raw = data.get("confidence", 0.65)
        try:
            confidence = float(confidence_raw)
        except (TypeError, ValueError):
            confidence = 0.65
        confidence = min(max(confidence, 0.0), 1.0)

        return Brief(
            problem=str(data.get("problem", "Not provided")).strip() or "Not provided",
            method=str(data.get("method", "Not provided")).strip() or "Not provided",
            key_findings=_as_list(data.get("key_findings")),
            limitations=_as_list(data.get("limitations")),
            why_relevant_to_query=str(data.get("why_relevant_to_query", "Not provided")).strip() or "Not provided",
            confidence=round(confidence, 3),
        )

    def _extractive_brief(self, query: str, item: RankedPaper) -> Brief:
        sents = _first_sentences(item.paper.abstract, n=3)
        problem = sents[0] if len(sents) >= 1 else item.paper.abstract[:220]
        method = sents[1] if len(sents) >= 2 else "Method details are limited in abstract."
        findings = sents[2:] if len(sents) >= 3 else ["Key findings are condensed from abstract."]
        limitations = ["Abstract-only summary; full paper may include additional caveats."]

        if item.matched_keywords:
            relevance = f"Matches keywords: {', '.join(item.matched_keywords)}. Related to query '{query}'."
        else:
            relevance = f"Lexically and semantically related to query '{query}'."

        return Brief(
            problem=problem,
            method=method,
            key_findings=findings,
            limitations=limitations,
            why_relevant_to_query=relevance,
            confidence=0.62,
        )
