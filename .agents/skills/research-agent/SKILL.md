---
name: research-agent
description: Orchestrate the AI Literature Agent workflow by reading agent_config.yaml, invoking the literature retrieval pipeline, and producing downstream-ready payload artifacts for other group skills. Use this skill when the goal is to run the full agent rather than only the retrieval module.
---

# research-agent

This skill runs the app-level orchestration workflow.

## Run

From the repository root:

```bash
python run_agent.py --config agent_config.yaml
```

Run selected topics only:

```bash
python run_agent.py --config agent_config.yaml --topic "Large Language Models" --topic "Graph Learning"
```

## Outputs

- `outputs/manifest.json`
- `outputs/agent_payload.json`
- `outputs/agent_summary.md`

## Responsibility

- read app-level configuration from `agent_config.yaml`
- invoke the literature retrieval skill
- assemble the downstream payload described in `interfaces/skill_contracts.md`
