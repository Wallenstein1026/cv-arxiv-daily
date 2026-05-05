from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator


class TimeRange(BaseModel):
    start: Optional[date] = None
    end: Optional[date] = None

    @field_validator("end")
    @classmethod
    def validate_range(cls, value: Optional[date], info):
        start = info.data.get("start")
        if value is not None and start is not None and value < start:
            raise ValueError("time_range.end must be >= time_range.start")
        return value


class RankingWeights(BaseModel):
    semantic: float = 0.45
    keyword: float = 0.35
    recency: float = 0.20

    @field_validator("recency")
    @classmethod
    def validate_sum(cls, value: float, info):
        semantic = info.data.get("semantic", 0.45)
        keyword = info.data.get("keyword", 0.35)
        total = semantic + keyword + value
        if abs(total - 1.0) > 1e-6:
            raise ValueError("ranking.weights must sum to 1.0")
        return value


class SummarizationConfig(BaseModel):
    enabled: bool = True
    top_k: int = 10
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.2
    max_output_tokens: int = 500


class RetrievalConfig(BaseModel):
    max_candidates: int = 200
    min_keyword_hits: int = 1
    category_allowlist: List[str] = Field(default_factory=list)


class OutputConfig(BaseModel):
    output_dir: str = "outputs"
    json_filename: str = "papers.json"
    markdown_filename: str = "brief.md"


class TopicConfig(BaseModel):
    query: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)


class SkillConfig(BaseModel):
    default_query: str = "computer vision"
    default_keywords: List[str] = Field(default_factory=list)
    time_range: TimeRange = Field(default_factory=TimeRange)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    ranking: RankingWeights = Field(default_factory=RankingWeights)
    summarization: SummarizationConfig = Field(default_factory=SummarizationConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    topics: Dict[str, TopicConfig] = Field(default_factory=dict)


class ConfigError(RuntimeError):
    pass


def load_skill_config(path: str | Path) -> SkillConfig:
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    # compatibility with original config.yaml keywords layout
    if "topics" not in raw and "keywords" in raw:
        topics: Dict[str, Dict[str, List[str]]] = {}
        for topic_name, topic_cfg in raw["keywords"].items():
            filters = topic_cfg.get("filters", []) if isinstance(topic_cfg, dict) else []
            topics[topic_name] = {"keywords": list(filters)}
        raw["topics"] = topics

    if "default_keywords" not in raw and "topics" in raw:
        union_keywords = []
        for v in raw["topics"].values():
            union_keywords.extend(v.get("keywords", []))
        raw["default_keywords"] = sorted(set(union_keywords))

    if "retrieval" not in raw:
        raw["retrieval"] = {}
    if "max_results" in raw and "max_candidates" not in raw["retrieval"]:
        raw["retrieval"]["max_candidates"] = int(raw["max_results"]) * 20

    try:
        return SkillConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"Invalid config at {path}: {exc}") from exc
