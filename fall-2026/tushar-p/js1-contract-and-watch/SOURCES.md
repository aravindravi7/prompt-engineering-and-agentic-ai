# SOURCES — Job-Search Agent 1

## Data and services

- **Greenhouse Job Board API** (public, no login): `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`. It's the only board host on the allow-list. Raw responses are saved in `raw/`.
- **Anthropic API** (`api.anthropic.com`): the Claude judge, model `claude-sonnet-5-5`. The key is read from the environment only and is not in this repository.

## Reference only (no code copied)

- **The Reallocation Engine** (`nikbearbrown/the-reallocation-engine`): the Greenhouse endpoint pattern, and the example personas in `search/examples/`, which I inspected for the format. I didn't use them: Priya Nair, the closest one, targets AI/ML/Data roles and has no years-of-experience field.

## Libraries

- `anthropic` 2.3.0 (Anthropic Python SDK, MIT licence)
- `pytest` 9.2.0 (MIT licence)
- Python standard library (`urllib`, `html`, `json`, `random`, ...)

## What I wrote or decided

- Every rule in CONTRACT.md: the titles, the location scope, the 0–3 years, the 21 days, sponsorship, the skills threshold, and `cannot_tell`.
- Drafted CONTRACT.md and LABELING-RULE.md.
- The approval or rejection of each gap Claude Code raised (A–P).
- The labeling rule's choices, and all 20 hand labels in `experiments/labels.csv`.
- The choice of board, persona, and experiment design.
- The mutation test, the independent checks, and the decision to reject the `&nbsp;` "fix".
- FRICTIONAL.md, written by me.

## What Claude contributed

- **Claude Code** (CLI, in this folder):
  - all code in `agent/` and `experiments/`, and all tests;
  - the plan review that found contract gaps A–P;
  - the build report, which named its own weak tests;
  - the test-first check that showed the `&nbsp;` bug didn't exist.
- **Claude chat** (claude.ai):
  - formatted CONTRACT.md and LABELING-RULE.md from my answers;
  - drafted the fictional persona `persona/cole-palmer.example.json`;
  - built the R3 city list from my pasted location data;
  - proposed the one prompt change;
  - drafted PROMPT-EXPERIMENT.md, SAMPLING-REPORT.md, ACTION-SURFACE.md, README.md and this file from my run outputs, which I reviewed and edited;
- **Claude as the judge** (`claude-sonnet-5-5`, through the API): every Claude verdict in `out/` and `experiments/results/`, all from 2026-10-28 and 2026-10-29. All of them are labeled model judgment.

Claude chat also made mistakes, which I caught and logged in FRICTIONAL.md: a check command that measured the wrong text, and key-setup instructions that overwrote the clipboard.