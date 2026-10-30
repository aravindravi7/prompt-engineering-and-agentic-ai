# SOURCES — Job-Search Agent 1

## What I used

- **Greenhouse Job Board API.** A public, unauthenticated endpoint: `https://boards-api.greenhouse.io/v1/boards/<board>/jobs?content=true`. I used the boards `datadog` (2026-10-29) and `databricks` (2026-10-29 and 2026-10-30).
  - Claude also counted relevant postings on 8 other boards on 2026-10-29 (toast, stripe, robinhood, duolingo, airbnb, scaleai, anthropic, figma) to help choose one. Those responses were not saved.
- **Persona résumé:** Priya Nair, fictional. Copied from the Reallocation Engine (https://github.com/nikbearbrown/the-reallocation-engine), file `search/examples/priya-nair/resume.example.json`, through my local fork, read only.
  - I added `work_authorization` from that persona's `profile.yml`, with a `_source` note.
- **Python 3.11 standard library.** No third-party packages.
- **Claude Code CLI** 2.1.312 (`claude -p`, model `claude-opus-5-5`), through my NEU Claude account. Used for every Claude verdict.
- **Course materials:** the assignment brief, and the repo's `AGENTS.md` (standard-library Python, Claude Code access assumed).

## What I wrote or decided

- **Every rule decision in CONTRACT.md.** I made them by answering multiple-choice questions: good and bad title words, locations, skill count, sponsorship, whole-word matching, and the three wrong versions.
- **The failure sentence,** chosen from four options Claude offered.
- **Approval** of the visa-phrase list.
- **The board choices:** Datadog, then Databricks. And the choice to fix the location rule (v2).
- **The labeling rule,** chosen from two options Claude offered.
- **All 20 hand labels.**
- **The one prompt change** (option B).
- **Running the tests myself** (2026-10-29) and reviewing FRICTIONAL.md.

## What Claude contributed

Claude Code (Opus 5.5) in a desktop session, 2026-10-29 and 2026-10-30.

- **All code:** `agent/`, `experiments/`, `tests/`.
- **The prompt wording:** `prompts/baseline.md`. The revision's added line is option B's text.
- **The proposals** for the visa-phrase list and the US state list. These came after Claude read the real board responses.
- **The 20-posting selection method,** and the one-line requirement summaries I saw on each labeling card.
- **Running** the watch, the judges, the board survey, the 73 recorded Claude calls (10 judged, 20 sampling, 40 experiment, 3 action-surface) and 2 earlier smoke-test calls that were not saved.
- **Drafts** of every document: CONTRACT.md (from my answers), README.md (including the sign-off text), SAMPLING.md, PROMPT-EXPERIMENT.md, ACTION-SURFACE.md, FRICTIONAL.md (written in my voice from the session record) and this file.
- **Findings it surfaced:**
  - "sponsor" on these boards never meant visas;
  - Databricks drops "USA" from locations;
  - empty `resume_fields` made replies INVALID;
  - the agent surface's fetch lost text;
  - the validator's `.0` path quirk.

I accepted most of this. I rejected the paid API-key route in favour of the CLI. I modified the persona, and I fixed the rule as a dated v2 rather than silently.
