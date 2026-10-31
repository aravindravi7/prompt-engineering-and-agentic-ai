# Job-Search Agent 1 — The Contract and the Watch

Arundhati K · INFO 7375 · Fall 2026 · contract: [CONTRACT.md](CONTRACT.md) (committed first, `e6008c3`, before any code)

One board (Stripe on Greenhouse), one fictional résumé (Rohan Desai), new postings only, every verdict justified,
two judges kept apart: a **record** from the written rule and a **model judgment** from Claude.

## Language and toolchain

- Python 3 standard library only (developed on Python 3.15.0, macOS). No packages to install.
- Claude Code CLI (`claude`, 2.1.283) for the Claude judge — optional; everything else runs offline or with
  one public GET. The judge calls `claude -p` with no tools, no settings, no MCP servers, from an empty temp dir.
- Network: only `boards-api.greenhouse.io` (allow-list in `jsagent/fetch.py`).

## Exact commands (from this folder)

```bash
python3 -m unittest discover -s tests -t .        # 45 tests, offline
python3 seed.py --published-before 2026-10-29     # live fetch + build the SEEDED earlier response
python3 run.py --from-file evidence/seeded/earlier-response-before-2026-10-29.json.gz   # run 1: baseline (seeded)
python3 run.py                                    # run 2: live fetch, reports postings new since run 1
python3 run.py --claude                           # same, plus a labeled Claude judgment per new posting
python3 experiments.py sample                     # sampling report calls (needs claude login)
python3 experiments.py score                      # rebuild experiments/RESULTS.md from logs + labels
```

To re-run the watch from scratch, delete `state/seen_ids.json` first (the state file is what makes run 1 a baseline).

## What ran (2026-10-31)

| run | when (UTC) | source | postings | new | rule RELEVANT |
|---|---|---|---|---|---|
| seed source | 06:16:29 | live fetch → `evidence/raw/20261031T061629Z-live-seed-source.json.gz` | 746 | — | — |
| 1 — baseline, **SEEDED** | 06:16:32 | `evidence/seeded/earlier-response-before-2026-10-29.json.gz` (live response minus the 32 postings first published on/after 2026-10-29) | 714 | 0 (baseline) | — |
| 2 — live | 06:16:36 | live fetch → `evidence/raw/20261031T061636Z-live.json.gz` | 746 | 32 | 0 of 32 |

Reports: [`reports/`](reports/) · state file: [`state/seen_ids.json`](state/seen_ids.json).
**Run 1 is seeded, not a second calendar day.** The 32 "new" postings are new relative to a constructed earlier
board, not relative to a board I observed earlier. Postings that closed before today are missing from the seeded
file too, so it only approximates the board as it was before 2026-10-29.

## How the rule reads a posting (CONTRACT §5 interpretations)

| condition | posting field | reading |
|---|---|---|
| role | `title` | whole words "software engineer", "software developer", "backend/back-end engineer", "full-stack/full stack/fullstack engineer" |
| level | `title` only | whole words "intern", "internship", "co-op", "new grad", "new graduate". "Internal" ≠ intern. **"Early Career" is not on the contract's list, so it fails.** |
| US location | `location.name` | whole-word US markers: US, USA, U.S., United States, San Francisco/SF, Seattle/SEA, New York/NYC, Chicago/CHI, Atlanta, WA/CA/NY/IL. "Remote", "AMER", "N/A" alone fail (cannot be verified). |
| skills | `content` (HTML removed) | ≥ 2 of the 10 contract skills, whole words, anywhere in the text; no required/preferred distinction. Aliases: Golang, Postgres, k8s, Amazon Web Services. "Go" counts only capitalised and not starting a sentence. |

A skill is cited only if Rohan's résumé lists it; each citation names the résumé field (`skills.languages[2]`)
and quotes the posting's `content`.

## Tests (CONTRACT §10 → test file)

| contract requirement | test |
|---|---|
| first-run baseline; new ids; no duplicate reports | `tests/test_watch.py` (`NewSinceLastTests`, `EndToEndTests`) |
| verdict ↔ posting id (wrong version 1) | `tests/test_wrong_versions.py::WrongVersion1MisPairing` — rotated verdicts, relabelled ids, missing/duplicated records |
| evidence-based justification (wrong version 2) | `tests/test_wrong_versions.py::WrongVersion2NoEvidence` — generic, one citation, invented quote, wrong résumé field, repeated skill |
| invalid Claude output rejected | `tests/test_claude_validator.py` — 13 constructed bad replies (constructed strings, not Claude output) |
| host allow-list; redirects | `tests/test_fetch.py` |
| judges kept separate and labeled | `tests/test_watch.py::EndToEndTests` |
| fictional résumé only | `tests/test_resume.py` |

Last run: `Ran 45 tests … OK` (2026-10-31).

## Sampling report · Prompt experiment · Action surfaces

- Sampling (Chapter 1): `experiments.py sample` → [`experiments/RESULTS.md`](experiments/RESULTS.md) — TODO (needs Claude login + my hand labels)
- Prompt experiment (Chapter 2): labeling set in [`labeling/`](labeling/), rule in `labeling/LABELING-RULE.md` — TODO
- Action-surface comparison (Chapter 3): [`ACTION-SURFACES.md`](ACTION-SURFACES.md) — TODO

## Sign-off — Job-Search Agent 1

_To be written by me after the runs. Placeholders only._

- **Checked:**
- **How:**
- **Not checked:**
  1.
  2.
  3.
- **Not claiming:**
- **Signed or withheld:** ____________ (name, date)

### Driver's seat

| part of the task | Claude should | I should | why it stays mine | evidence (commit / transcript line) |
|---|---|---|---|---|
| | | | | |
