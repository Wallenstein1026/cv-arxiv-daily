from __future__ import annotations

import re
from typing import Dict, List, Tuple

from research_skill.schemas.models import Paper


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def keyword_hits(paper: Paper, keywords: List[str]) -> List[str]:
    merged = _normalize(f"{paper.title} {paper.abstract}")
    matched = []
    for kw in keywords:
        kw_norm = _normalize(kw)
        if kw_norm and kw_norm in merged:
            matched.append(kw)
    return matched


def filter_papers_by_keywords(
    papers: List[Paper], keywords: List[str], min_hits: int = 1
) -> Tuple[List[Paper], Dict[str, List[str]]]:
    if not keywords:
        return papers, {p.arxiv_id: [] for p in papers}

    kept: List[Paper] = []
    matched: Dict[str, List[str]] = {}

    for paper in papers:
        hits = keyword_hits(paper, keywords)
        if len(hits) >= min_hits:
            kept.append(paper)
            matched[paper.arxiv_id] = hits

    return kept, matched
