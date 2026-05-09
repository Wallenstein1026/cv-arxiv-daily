#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

import yaml

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from research_skill import ResearchSkillPipeline, load_skill_config
from research_skill.output.writers import write_json, write_markdown, write_skill_b_payload


logging.basicConfig(
    format="[%(asctime)s %(levelname)s] %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)


@dataclass
class AgentConfig:
    app_id: str
    app_name: str
    version: str
    task_name: str
    description: str
    skill_config: str
    output_dir: str
    default_topics: List[str]
    downstream_skills: List[str]
    base_dir: Path


def load_agent_config(path: str | Path) -> AgentConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Agent config not found: {config_path}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return AgentConfig(
        app_id=str(raw.get("app_id", "ai-literature-agent")),
        app_name=str(raw.get("app_name", "AI Literature Agent")),
        version=str(raw.get("version", "0.1.0")),
        task_name=str(raw.get("task_name", "ai_research_literature_pipeline")),
        description=str(
            raw.get(
                "description",
                "Retrieve AI-related papers from arXiv and emit downstream-ready payloads.",
            )
        ),
        skill_config=str(raw.get("skill_config", "skill_config.yaml")),
        output_dir=str(raw.get("output_dir", "outputs")),
        default_topics=list(raw.get("default_topics", [])),
        downstream_skills=list(raw.get("downstream_skills", [])),
        base_dir=config_path.resolve().parent,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Literature Agent")
    parser.add_argument("--config", type=str, default="agent_config.yaml", help="Path to agent config")
    parser.add_argument("--topic", action="append", dest="topics", default=None, help="Run one or more topics")
    parser.add_argument("--output-dir", type=str, default=None, help="Override output directory")
    return parser.parse_args()


def normalize_topic_slug(topic: str) -> str:
    return topic.lower().replace(" ", "_")


def resolve_topics(requested: Iterable[str] | None, skill_topic_names: List[str], default_topics: List[str]) -> List[str]:
    if requested:
        topics = list(requested)
    elif default_topics:
        topics = default_topics
    else:
        topics = skill_topic_names

    unknown = [topic for topic in topics if topic not in skill_topic_names]
    if unknown:
        raise ValueError(f"Unknown topics: {unknown}. Available: {skill_topic_names}")
    return topics


def write_agent_summary(
    summary_path: Path,
    *,
    app_name: str,
    task_name: str,
    topics: List[str],
    manifest_path: Path,
    payload_path: Path,
    topic_counts: Dict[str, int],
) -> None:
    lines = [
        f"# {app_name}",
        "",
        f"- Task: `{task_name}`",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Topics: {', '.join(topics)}",
        f"- Skill manifest: `{manifest_path}`",
        f"- Agent payload: `{payload_path}`",
        "",
        "## Topic Counts",
        "",
    ]
    for topic, count in topic_counts.items():
        lines.append(f"- `{topic}`: `{count}` papers")

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    agent_config = load_agent_config(args.config)
    skill_config_path = Path(agent_config.skill_config)
    if not skill_config_path.is_absolute():
        skill_config_path = agent_config.base_dir / skill_config_path
    skill_config = load_skill_config(skill_config_path)
    pipeline = ResearchSkillPipeline(skill_config)

    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = Path(agent_config.output_dir)
        if not output_dir.is_absolute():
            output_dir = agent_config.base_dir / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    topics = resolve_topics(args.topics, list(skill_config.topics.keys()), agent_config.default_topics)
    run_id = datetime.now(timezone.utc).strftime("agent-%Y%m%dT%H%M%SZ")

    skill_manifest: Dict[str, Dict[str, object]] = {}
    topic_counts: Dict[str, int] = {}
    generated_topics = []

    for topic in topics:
        topic_cfg = skill_config.topics[topic]
        output = pipeline.run_topic(topic, topic_cfg.query, topic_cfg.keywords)
        safe_topic = normalize_topic_slug(topic)

        json_path = output_dir / f"{safe_topic}.{skill_config.output.json_filename}"
        md_path = output_dir / f"{safe_topic}.{skill_config.output.markdown_filename}"
        skill_b_json_path = output_dir / f"{safe_topic}.skill_b.json"

        write_json(output, str(json_path))
        write_markdown(output, str(md_path))
        write_skill_b_payload(output, str(skill_b_json_path), run_id=run_id)

        count = len(output.papers)
        topic_counts[topic] = count
        generated_topics.append(
            {
                "topic": topic,
                "query": output.meta.query,
                "keywords": output.meta.keywords,
                "paper_count": count,
                "artifacts": {
                    "papers_json": str(json_path),
                    "brief_markdown": str(md_path),
                    "skill_b_json": str(skill_b_json_path),
                },
            }
        )
        skill_manifest[topic] = {
            "json": str(json_path),
            "markdown": str(md_path),
            "skill_b_json": str(skill_b_json_path),
            "count": count,
        }
        logging.info("Agent topic=%s papers=%s", topic, count)

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(skill_manifest, indent=2), encoding="utf-8")

    payload = {
        "agent": {
            "app_id": agent_config.app_id,
            "app_name": agent_config.app_name,
            "version": agent_config.version,
            "task_name": agent_config.task_name,
            "description": agent_config.description,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id,
        },
        "skill": {
            "name": "literature_retrieval",
            "entry_point": "python run_skill.py --config skill_config.yaml",
        },
        "topics": generated_topics,
        "downstream": {
            "skills": agent_config.downstream_skills,
            "input_contract": "interfaces/skill_contracts.md",
            "manifest_path": str(manifest_path),
        },
    }

    payload_path = output_dir / "agent_payload.json"
    payload_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    summary_path = output_dir / "agent_summary.md"
    write_agent_summary(
        summary_path,
        app_name=agent_config.app_name,
        task_name=agent_config.task_name,
        topics=topics,
        manifest_path=manifest_path,
        payload_path=payload_path,
        topic_counts=topic_counts,
    )

    logging.info("Agent manifest written: %s", manifest_path)
    logging.info("Agent payload written: %s", payload_path)
    logging.info("Agent summary written: %s", summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
