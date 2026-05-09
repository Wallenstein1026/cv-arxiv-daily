---
name: cv-arxiv-daily
description: Retrieve recent AI-related papers from arXiv, filter and rank them by topic relevance, and generate JSON, Markdown, and StudyClaw-compatible research briefs. Use this skill when the task is to monitor artificial intelligence research topics such as large language models, graph learning, computer vision, multimodal systems, or adjacent areas.
---

# cv-arxiv-daily

Use this skill when you need a repeatable pipeline for recent AI paper discovery and brief generation from arXiv.

## What this skill does

- Retrieves recent arXiv papers from configured categories such as `cs.AI`, `cs.LG`, and other configured AI-adjacent areas
- Filters candidates with topic keywords
- Ranks papers with semantic, keyword, and recency signals
- Generates per-topic outputs in JSON, Markdown, and StudyClaw-compatible JSON

## Run

From the skill root:

```bash
python run_skill.py --config skill_config.yaml
```

Run a single topic:

```bash
python run_skill.py --config skill_config.yaml --topic "Graph Learning"
```

Override the output directory:

```bash
python run_skill.py --config skill_config.yaml --output-dir outputs_custom
```

## Inputs

Primary configuration lives in `skill_config.yaml`.

Key fields:

- `default_query`: fallback search query
- `time_range.start` and `time_range.end`: date window for retrieval
- `retrieval.category_allowlist`: arXiv categories to search
- `ranking.semantic`, `ranking.keyword`, `ranking.recency`: ranking weights that must sum to `1.0`
- `summarization.enabled`: enable model-based summarization
- `topics`: named research topics with `query` and `keywords`

## Outputs

Outputs are written under the configured output directory, defaulting to `outputs/`.

- `<topic>.papers.json`: ranked paper list with metadata and summaries
- `<topic>.brief.md`: human-readable topic brief
- `<topic>.skill_b.json`: StudyClaw-compatible payload
- `manifest.json`: index of generated artifacts

Topic file names are normalized to lowercase with spaces replaced by underscores.

## OpenAI usage

If `summarization.enabled` is true and `OPENAI_API_KEY` is available, the skill uses the configured OpenAI model for brief generation.

If no API key is present, the pipeline falls back to extractive summaries from abstracts.

## Reference files

- `run_skill.py`: CLI entry point
- `docs/research_skill.md`: short usage reference
- `skill_config.more.yaml`: larger sample configuration
