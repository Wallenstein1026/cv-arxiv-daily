from __future__ import annotations

from datetime import date
from typing import Iterable, List, Optional

import arxiv
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from research_skill.schemas.models import Paper


class ArxivRetriever:
    def __init__(self, page_size: int = 100, delay_seconds: float = 1.0) -> None:
        self.client = arxiv.Client(page_size=page_size, delay_seconds=delay_seconds, num_retries=3)

    @staticmethod
    def build_query(query: Optional[str], keywords: List[str]) -> str:
        clauses = []
        if query:
            clauses.append(f"all:{query}")

        for kw in keywords:
            kw = kw.strip()
            if not kw:
                continue
            if " " in kw:
                clauses.append(f'all:"{kw}"')
            else:
                clauses.append(f"all:{kw}")

        if not clauses:
            return "all:computer vision"

        return " OR ".join(clauses)

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    def retrieve(
        self,
        query: Optional[str],
        keywords: List[str],
        max_candidates: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_allowlist: Optional[List[str]] = None,
    ) -> List[Paper]:
        full_query = self.build_query(query=query, keywords=keywords)
        search = arxiv.Search(
            query=full_query,
            max_results=max_candidates,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

        papers: List[Paper] = []
        seen = set()
        categories = set(category_allowlist or [])

        for result in self.client.results(search):
            paper_id = result.get_short_id().split("v")[0]
            if paper_id in seen:
                continue

            published = result.published.date()
            updated = result.updated.date()

            if start_date and published < start_date and updated < start_date:
                continue
            if end_date and published > end_date and updated > end_date:
                continue

            all_categories = list(result.categories or [])
            if categories and not categories.intersection(all_categories):
                continue

            paper = Paper(
                arxiv_id=paper_id,
                title=result.title.strip(),
                authors=[str(a) for a in result.authors],
                abstract=(result.summary or "").replace("\n", " ").strip(),
                categories=all_categories,
                primary_category=result.primary_category,
                published=published,
                updated=updated,
                url=f"https://arxiv.org/abs/{paper_id}",
                comment=result.comment,
            )
            papers.append(paper)
            seen.add(paper_id)

        return papers
