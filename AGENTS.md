# AI Literature Agent

Codex-powered research app that contains one top-level agent and one standalone skill for AI-related arXiv literature retrieval.

## Single Invariant

The repository exposes two concrete entry points:

- `python run_skill.py --config skill_config.yaml`
- `python run_agent.py --config agent_config.yaml`

The skill performs paper retrieval and summarization. The agent orchestrates that skill and writes an `agent_payload.json` artifact.

## Components

This repository contains exactly one agent-facing skill and one app-level agent wrapper.

### `/literature-retrieval`

Reusable paper retrieval module.

- purpose: retrieve AI-related papers from arXiv and emit ranked outputs
- entry: `python run_skill.py --config skill_config.yaml`
- outputs:
  - `outputs/<topic>.papers.json`
  - `outputs/<topic>.brief.md`
  - `outputs/<topic>.skill_b.json`
  - `outputs/manifest.json`

### `/research-agent`

Top-level app orchestrator.

- purpose: run the agent workflow and package the skill outputs as app-level artifacts
- entry: `python run_agent.py --config agent_config.yaml`
- outputs:
  - `outputs/manifest.json`
  - `outputs/agent_payload.json`
  - `outputs/agent_summary.md`

## App Structure

- App manifest: `stuclaw.app.json`
- App landing page: `index.html`
- Start script: `start.sh`
- Stop script: `stop.sh`
- Skill config: `skill_config.yaml`
- Agent config: `agent_config.yaml`

## Call Hierarchy

`/research-agent` is the entry for normal app execution and internally uses `/literature-retrieval`.

```text
research-agent
  -> literature-retrieval
  -> outputs/manifest.json
  -> outputs/agent_payload.json
  -> submission-ready artifacts
```

## Runtime Notes

- The app is a one-shot workflow, not a long-running daemon
- `start.sh` runs the agent once and writes artifacts
- `stop.sh` is informational because no background process remains after completion

## Quick Commands

Run the full agent:

```bash
bash start.sh
```

Run only the skill:

```bash
python run_skill.py --config skill_config.yaml --topic "Graph Learning"
```

Run selected agent topics:

```bash
python run_agent.py --config agent_config.yaml --topic "Large Language Models" --topic "Graph Learning"
```
