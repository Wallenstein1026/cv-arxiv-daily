# StudyClawHub Submission Pack

This file prepares the `cv-arxiv-daily` skill for StudyClawHub submission.

## Submit Type

- Submit as: `Skill`
- Skill name: `cv-arxiv-daily`
- Path to skill folder: `.`

## Step 1: Tool Submission

Use one of the supported tools listed by the course or platform:

- `Claude Code`
- `OpenClaw`
- `WorkBuddy`

Recommended submission summary:

```text
Skill: cv-arxiv-daily
Type: Skill
Purpose: Retrieve recent computer vision papers from arXiv, rank them by topic relevance, and generate structured JSON and Markdown briefs.
Entry point: python run_skill.py --config skill_config.yaml
Primary outputs: outputs/<topic>.papers.json, outputs/<topic>.brief.md, outputs/manifest.json
```

## Step 2: Website Registration

Register this skill on StudyClawHub with the following metadata.

### Form Values

- Name: `cv-arxiv-daily`
- Description: `Retrieves recent computer vision papers from arXiv, filters and ranks them by topic relevance, and generates JSON and Markdown research briefs.`
- Version: `0.1.0`
- Tags: `arxiv, computer-vision, research-mining, paper-ranking, summarization`
- GitHub Repo URL: `https://github.com/LeyiSheng/cv-arxiv-daily`
- Path to Skill Folder: `.`
- Agent name: leave blank if submitting only the skill; otherwise fill in your group agent name
- GitHub Username: `LeyiSheng`

### Short Description Variant

Use this if the form prefers a shorter summary:

```text
Daily CV arXiv mining skill with topic filtering, ranking, and brief generation.
```

## What This Skill Does

- Queries recent arXiv papers in computer vision related categories such as `cs.CV`, `cs.AI`, and `cs.LG`
- Supports topic-specific retrieval for `SLAM`, `Visual Localization`, and `NeRF`
- Ranks papers with semantic, keyword, and recency signals
- Generates machine-readable JSON outputs and human-readable Markdown briefs
- Optionally uses OpenAI for higher quality brief summarization

## Local Evidence for the Submission

- Main config: [skill_config.yaml](/Users/leyisheng/Desktop/py/socialproj/cv-arxiv-daily/skill_config.yaml:1)
- Usage doc: [docs/research_skill.md](/Users/leyisheng/Desktop/py/socialproj/cv-arxiv-daily/docs/research_skill.md:1)
- Runner: [run_skill.py](/Users/leyisheng/Desktop/py/socialproj/cv-arxiv-daily/run_skill.py:1)
- Package source: [src/research_skill](/Users/leyisheng/Desktop/py/socialproj/cv-arxiv-daily/src/research_skill)

## Final Checklist

- Confirm whether the website wants `Path to Skill Folder` as `.` for a repo-root skill
- Make sure the GitHub repository is public or accessible to reviewers
- Submit the skill first, then register the integrating agent separately if your group has one
