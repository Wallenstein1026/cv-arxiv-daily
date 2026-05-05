#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research Retrieval & Summarization Skill")
    parser.add_argument("--config", type=str, default="skill_config.yaml", help="Path to skill config")
    parser.add_argument("--topic", type=str, default=None, help="Run a single topic by name")
    parser.add_argument("--output-dir", type=str, default=None, help="Override output directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_skill_config(args.config)
    pipeline = ResearchSkillPipeline(config)

    output_dir = Path(args.output_dir or config.output.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.topic:
        topic_cfg = config.topics.get(args.topic)
        if topic_cfg is None:
            raise ValueError(f"Unknown topic: {args.topic}. Available: {list(config.topics.keys())}")
        outputs = {args.topic: pipeline.run_topic(args.topic, topic_cfg.query, topic_cfg.keywords)}
    else:
        outputs = pipeline.run_all_topics()

    run_id = datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")

    manifest = {}
    for topic, output in outputs.items():
        safe_topic = topic.lower().replace(" ", "_")
        json_path = output_dir / f"{safe_topic}.{config.output.json_filename}"
        md_path = output_dir / f"{safe_topic}.{config.output.markdown_filename}"
        skill_b_json_path = output_dir / f"{safe_topic}.skill_b.json"
        write_json(output, str(json_path))
        write_markdown(output, str(md_path))
        write_skill_b_payload(output, str(skill_b_json_path), run_id=run_id)
        manifest[topic] = {
            "json": str(json_path),
            "markdown": str(md_path),
            "skill_b_json": str(skill_b_json_path),
            "count": len(output.papers),
        }
        logging.info(
            "Topic=%s papers=%s json=%s md=%s skill_b_json=%s",
            topic,
            len(output.papers),
            json_path,
            md_path,
            skill_b_json_path,
        )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logging.info("Manifest written: %s", manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
