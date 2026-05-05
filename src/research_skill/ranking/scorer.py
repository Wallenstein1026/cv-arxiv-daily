from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from research_skill.schemas.models import Paper, RankedPaper, ScoreBreakdown


@dataclass
class RankingWeights:
    semantic: float
    keyword: float
    recency: float


class PaperScorer:
    def __init__(self, weights: RankingWeights, recency_half_life_days: int = 180) -> None:
        self.weights = weights
        self.recency_half_life_days = recency_half_life_days

    def _semantic_scores(self, papers: List[Paper], query_text: str) -> np.ndarray:
        if not papers:
            return np.array([])

        documents = [f"{p.title}. {p.abstract}" for p in papers]
        corpus = [query_text] + documents
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
        tfidf = vectorizer.fit_transform(corpus)
        query_vector = tfidf[0:1]
        doc_vectors = tfidf[1:]
        scores = cosine_similarity(query_vector, doc_vectors).flatten()

        if float(scores.max(initial=0.0)) > 0:
            scores = scores / scores.max()

        return scores

    def _keyword_scores(self, papers: List[Paper], matched_keywords: Dict[str, List[str]], total_keywords: int) -> np.ndarray:
        if not papers:
            return np.array([])
        denominator = max(total_keywords, 1)
        return np.array([len(matched_keywords.get(p.arxiv_id, [])) / denominator for p in papers], dtype=float)

    def _recency_scores(self, papers: List[Paper], now: date) -> np.ndarray:
        if not papers:
            return np.array([])
        scores = []
        for p in papers:
            newest_date = max(p.published, p.updated)
            age_days = max((now - newest_date).days, 0)
            decay = math.exp(-math.log(2) * age_days / self.recency_half_life_days)
            scores.append(decay)
        return np.array(scores, dtype=float)

    def rank(
        self,
        papers: List[Paper],
        query_text: str,
        matched_keywords: Dict[str, List[str]],
        total_keywords: int,
        now: date,
    ) -> List[RankedPaper]:
        if not papers:
            return []

        semantic_scores = self._semantic_scores(papers, query_text)
        keyword_scores = self._keyword_scores(papers, matched_keywords, total_keywords)
        recency_scores = self._recency_scores(papers, now)

        ranked: List[RankedPaper] = []
        for idx, paper in enumerate(papers):
            semantic = float(semantic_scores[idx])
            keyword = float(keyword_scores[idx])
            recency = float(recency_scores[idx])

            total = (
                self.weights.semantic * semantic
                + self.weights.keyword * keyword
                + self.weights.recency * recency
            )

            ranked.append(
                RankedPaper(
                    paper=paper,
                    relevance_score=round(total, 6),
                    score_breakdown=ScoreBreakdown(
                        semantic=round(semantic, 6),
                        keyword=round(keyword, 6),
                        recency=round(recency, 6),
                    ),
                    matched_keywords=matched_keywords.get(paper.arxiv_id, []),
                )
            )

        ranked.sort(key=lambda x: (x.relevance_score, x.paper.updated, x.paper.published), reverse=True)
        return ranked
