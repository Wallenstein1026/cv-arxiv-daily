# Research Retrieval & Summarization Skill

## Run

```bash
python run_skill.py --config skill_config.yaml
```

Run one topic only:

```bash
python run_skill.py --config skill_config.yaml --topic "Graph Learning"
```

## Outputs

Generated under `outputs/`:

- `<topic>.papers.json`: machine-readable paper list + relevance scores + structured briefs
- `<topic>.brief.md`: human-readable report
- `manifest.json`: output index

## Optional LLM summarization

Set `OPENAI_API_KEY` to enable OpenAI summarization.
If not set, pipeline falls back to extractive summaries from abstracts.
