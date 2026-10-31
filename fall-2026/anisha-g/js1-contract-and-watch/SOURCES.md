# Sources
- Greenhouse public Job Board API: `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` (public, no login). Raw responses saved in `runs/` as evidence.
- My own earlier code: `fetch-board.py` from my Reallocation Engine mode (anishagaikar0420/the-reallocation-engine, branch mode/anisha-bi-analyst-triage) — the HTML-to-text and slug check were reused.
- Claude (Anthropic), 2026-10-31: drafted CONTRACT.md wording from my decisions, wrote `agent.py`, `tests/test_agent.py`, both prompts, ACTION-SURFACES.md and the README/sign-off templates. I chose the board, the rule and the persona defaults, ran everything, and wrote the hand labels and conclusions.
- Claude Code (`claude -p`): the JUDGMENT calls. My own Claude Code hit its spend limit on 2026-10-31, so the 63 judge calls behind `reports/` and run 2 were run by Claude in its workspace on my raw response and my labels (see FRICTIONAL.md).
- `label.py`: helper written by Claude; the 20 labels it recorded are mine.
- Persona "Nadia Okafor": fictional, written for this assignment.
