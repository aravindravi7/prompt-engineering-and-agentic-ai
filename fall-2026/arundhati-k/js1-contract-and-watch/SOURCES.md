# SOURCES — what I used, what I wrote, what AI contributed

## Used
- Assignment brief: `assignments/assignment-js1-the-contract-and-the-watch.md` (this repo).
- Stripe's public Greenhouse board: `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`
  (raw responses saved in `evidence/raw/`, fetched 2026-10-31).
- Persona: Rohan Desai, fictional, from The Reallocation Engine `search/examples/rohan-desai/resume.example.json`
  (copied unchanged to `persona/`).
- Claude Code CLI 2.1.283 (`claude -p`), model reported `claude-opus-5-5` (plus `claude-haiku-5-5` inside WebFetch, surface 3).

## What I wrote / decided
_My words — fill in. Be specific (file + what):_
- CONTRACT.md — 
- Persona switch (Maya → Rohan), the 10 skills, the 2-skill threshold — 
- labeling/LABELING-RULE.md — 
- All 20 hand labels in labeling/labels.csv — 
- The revision prompt's one change — 
- Action-surface choice and defense; sampling and experiment conclusions; sign-off; FRICTIONAL.md — 

## My own look at Stripe postings (date, what I saw)
_My words — 2 lines from postings I opened myself._

## ChatGPT contributed
_My words — be exact. Things I know came from ChatGPT in this assignment:_
- _CONTRACT.md structure/text? (say how much)_
- _The persona/skills correction text (it contained a `utm_source=chatgpt.com` link)_
- _"Stripe research notes" — ChatGPT's own findings, not my observation; not used as evidence_
- _Row 3 label: I read ChatGPT's analysis of the posting before deciding (noted in labels.csv)_
- _Any other labels?_

## Claude (Claude Code, this session) contributed
- All code in `jsagent/`, `run.py`, `seed.py`, `make_labeling_set.py`, `experiments.py`, and all tests, written
  against my committed contract (`e6008c3` → `0c55047`).
- Ran the seeded baseline, both live runs, sampling, both prompts on dev and held-out, and surfaces 2 and 3.
- Pointed out: Maya is a PM persona with no Java/Spring; the "Go" verb false match; label-vs-rule inconsistencies (rows 13–16).
- Drafted the factual parts of README, SAMPLING-REPORT, PROMPT-EXPERIMENT, ACTION-SURFACES (tables, what ran, quotes).
  The conclusions in those files are mine.
- Constructed the test fixtures (`tests/fixtures.py`) — not real postings.
