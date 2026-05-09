---
name: literature-retrieval
description: Retrieve recent AI-related papers from arXiv, rank them by topic relevance, and emit structured JSON, Markdown, and downstream-ready payload files. Use this skill when another agent step needs curated literature context before graph analysis, benchmarking, reporting, or model comparison.
---

# literature-retrieval

This skill is the reusable paper retrieval module inside the app.

## Run

From the repository root:

```bash
python run_skill.py --config skill_config.yaml
```

Run a single topic:

```bash
python run_skill.py --config skill_config.yaml --topic "Graph Learning"
```

## Outputs

- `outputs/<topic>.papers.json`
- `outputs/<topic>.brief.md`
- `outputs/<topic>.skill_b.json`
- `outputs/manifest.json`

## Notes

- Topic defaults live in `skill_config.yaml`
- This skill is invoked directly by users or indirectly by `research-agent`
