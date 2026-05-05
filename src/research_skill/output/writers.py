from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from research_skill.schemas.models import SkillOutput


def write_json(output: SkillOutput, path: str) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        output.model_dump_json(indent=2, exclude_none=True),
        encoding="utf-8",
    )
    return out_path


def write_markdown(output: SkillOutput, path: str, top_n: int = 20) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    meta = output.meta
    lines = [
        f"# Research Brief: {meta.topic or meta.query}",
        "",
        f"- Generated at: `{meta.generated_at.isoformat()}`",
        f"- Query: `{meta.query}`",
        f"- Keywords: {', '.join(meta.keywords) if meta.keywords else '(none)' }",
        f"- Time range: `{meta.time_range.get('start')}` to `{meta.time_range.get('end')}`",
        f"- Retrieved / Filtered / Summarized: `{meta.retrieved_count}` / `{meta.filtered_count}` / `{meta.summarized_count}`",
        "",
        "## Ranked Papers",
        "",
    ]

    papers = output.papers[:top_n]
    if not papers:
        lines.append("No papers found for this query/time range.")
    else:
        for i, item in enumerate(papers, start=1):
            p = item.paper
            lines.extend(
                [
                    f"### {i}. {p.title}",
                    f"- arXiv: [{p.arxiv_id}]({p.url})",
                    f"- Published: `{p.published}` | Updated: `{p.updated}`",
                    f"- Authors: {', '.join(p.authors[:8])}" + (" ..." if len(p.authors) > 8 else ""),
                    f"- Categories: {', '.join(p.categories) if p.categories else '(none)'}",
                    f"- Relevance Score: `{item.relevance_score:.4f}`",
                    "- Score Breakdown: "
                    f"semantic=`{item.score_breakdown.semantic:.4f}`, "
                    f"keyword=`{item.score_breakdown.keyword:.4f}`, "
                    f"recency=`{item.score_breakdown.recency:.4f}`",
                    f"- Matched Keywords: {', '.join(item.matched_keywords) if item.matched_keywords else '(none)'}",
                ]
            )

            if item.brief:
                b = item.brief
                lines.extend(
                    [
                        "- Structured Brief:",
                        f"  - Problem: {b.problem}",
                        f"  - Method: {b.method}",
                        f"  - Key Findings: {'; '.join(b.key_findings) if b.key_findings else '(none)'}",
                        f"  - Limitations: {'; '.join(b.limitations) if b.limitations else '(none)'}",
                        f"  - Why Relevant: {b.why_relevant_to_query}",
                        f"  - Confidence: `{b.confidence:.2f}`",
                    ]
                )
            lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def write_skill_b_payload(output: SkillOutput, path: str, run_id: str, embeddings: Dict[str, list] | None = None) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    papers_metadata = []
    for item in output.papers:
        paper = item.paper
        paper_id = paper.arxiv_id
        papers_metadata.append(
            {
                "paper_id": paper_id,
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": list(paper.authors or []),
                "categories": list(paper.categories or []),
                "published_at": paper.published.isoformat(),
            }
        )

    payload = {
        "run_id": run_id,
        "papers_metadata": papers_metadata,
        "embeddings": embeddings or {},
    }

    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path
