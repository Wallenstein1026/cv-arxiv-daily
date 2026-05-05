from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Paper(BaseModel):
    arxiv_id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: str
    categories: List[str] = Field(default_factory=list)
    primary_category: Optional[str] = None
    published: date
    updated: date
    url: str
    comment: Optional[str] = None


class ScoreBreakdown(BaseModel):
    semantic: float = 0.0
    keyword: float = 0.0
    recency: float = 0.0


class Brief(BaseModel):
    problem: str
    method: str
    key_findings: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    why_relevant_to_query: str
    confidence: float


class RankedPaper(BaseModel):
    paper: Paper
    relevance_score: float
    score_breakdown: ScoreBreakdown
    matched_keywords: List[str] = Field(default_factory=list)
    brief: Optional[Brief] = None


class SkillMeta(BaseModel):
    query: str
    keywords: List[str]
    topic: Optional[str] = None
    time_range: Dict[str, Optional[str]]
    retrieved_count: int
    filtered_count: int
    summarized_count: int
    generated_at: datetime


class SkillOutput(BaseModel):
    meta: SkillMeta
    papers: List[RankedPaper] = Field(default_factory=list)
