from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

from research_skill.config import SkillConfig
from research_skill.filtering.keyword_filter import filter_papers_by_keywords
from research_skill.ranking.scorer import PaperScorer, RankingWeights
from research_skill.retrieval.arxiv_client import ArxivRetriever
from research_skill.schemas.models import SkillMeta, SkillOutput
from research_skill.summarization.llm_brief import BriefSummarizer


class ResearchSkillPipeline:
    def __init__(self, config: SkillConfig) -> None:
        self.config = config
        self.retriever = ArxivRetriever()
        self.scorer = PaperScorer(
            weights=RankingWeights(
                semantic=config.ranking.semantic,
                keyword=config.ranking.keyword,
                recency=config.ranking.recency,
            )
        )
        self.summarizer = BriefSummarizer(
            enabled=config.summarization.enabled,
            provider=config.summarization.provider,
            model=config.summarization.model,
            temperature=config.summarization.temperature,
            max_output_tokens=config.summarization.max_output_tokens,
        )

    def run_topic(self, topic: str, query: Optional[str], keywords: List[str]) -> SkillOutput:
        merged_query = query or self.config.default_query
        merged_keywords = list(dict.fromkeys([*self.config.default_keywords, *keywords]))

        retrieved = self.retriever.retrieve(
            query=merged_query,
            keywords=merged_keywords,
            max_candidates=self.config.retrieval.max_candidates,
            start_date=self.config.time_range.start,
            end_date=self.config.time_range.end,
            category_allowlist=self.config.retrieval.category_allowlist,
        )

        filtered, matched = filter_papers_by_keywords(
            papers=retrieved,
            keywords=merged_keywords,
            min_hits=self.config.retrieval.min_keyword_hits,
        )

        ranked = self.scorer.rank(
            papers=filtered,
            query_text=f"{merged_query} {' '.join(merged_keywords)}".strip(),
            matched_keywords=matched,
            total_keywords=len(merged_keywords),
            now=date.today(),
        )

        ranked = self.summarizer.summarize(
            query=merged_query,
            ranked_papers=ranked,
            top_k=self.config.summarization.top_k,
        )

        meta = SkillMeta(
            query=merged_query,
            keywords=merged_keywords,
            topic=topic,
            time_range={
                "start": str(self.config.time_range.start) if self.config.time_range.start else None,
                "end": str(self.config.time_range.end) if self.config.time_range.end else None,
            },
            retrieved_count=len(retrieved),
            filtered_count=len(filtered),
            summarized_count=min(self.config.summarization.top_k, len(ranked)),
            generated_at=datetime.utcnow(),
        )

        return SkillOutput(meta=meta, papers=ranked)

    def run_all_topics(self) -> Dict[str, SkillOutput]:
        if not self.config.topics:
            out = self.run_topic(topic="default", query=self.config.default_query, keywords=self.config.default_keywords)
            return {"default": out}

        outputs: Dict[str, SkillOutput] = {}
        for topic, cfg in self.config.topics.items():
            outputs[topic] = self.run_topic(topic=topic, query=cfg.query, keywords=cfg.keywords)
        return outputs
