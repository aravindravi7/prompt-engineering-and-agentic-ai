# Job-Search Agent 1: the contract and the watch

## Summary

A small agent that watches one public job board (Stripe's Greenhouse board), remembers which postings it has seen, and reports only new ones. Each new posting gets two verdicts on whether it suits a fictional job seeker (Maya Sehgal): one from a written rule anyone can recompute (a **RECORD**), and one from Claude under a fixed prompt (a **JUDGMENT**). The contract it is built against (`CONTRACT.md`) was written and committed before any code. The agent never applies, emails, messages, or logs in anywhere, and fetches from one allow-listed host only.

## Toolchain

- **Language:** JavaScript (ES modules), Node.js **v20.20.2**. No npm packages: built-in `fetch`, `node:test`, `node:child_process`.
- **Claude:** the Claude Code CLI, **2.1.310 (Claude Code)**, called as `claude -p` (one fresh session per call, no tools, run in an empty temp directory so it reads nothing but the prompt). Model requested and reported by the CLI on every call: **`claude-sonnet-5-5`**. Signed in to a claude.ai account; no API key is used or stored.
- **OS:** macOS (Darwin 25.5.0).
- **Network:** `boards-api.greenhouse.io` only (`src/fetch.mjs`).

## Commands

From this folder (`fall-2026/aravind-r/js1-contract-and-watch/`):

```bash
node --test test/
```

```bash
node src/watch.mjs --board stripe --state state/seen-ids.json --label live
```

The first run against an empty state file is the baseline and reports nothing as new. Each later run reports only ids not in the state file. Add `--judge none` to skip the Claude step. A run read from a saved file instead of the network must carry `seeded` in its label:

```bash
node src/watch.mjs --board stripe --state state/seeded-v2-seen-ids.json --label seeded-second-v2 --from-file runs/20261101T015849Z-live-baseline/raw-response.json
```

Seeded run construction, the label draw, the Claude batches and scoring:

```bash
node tools/make-seeded.mjs --raw runs/20261101T015849Z-live-baseline/raw-response.json --seed 20261031 --fixed 8195440,8165137,8223723 --pm 3 --nonpm 2 --exclude labels/draw.json --name seeded-earlier-v2 --runs runs
```

```bash
node tools/check-new-set.mjs --seeded runs/20261101T020452Z-seeded-earlier-v2 --run runs/20261101T020459Z-seeded-second-v2
```

```bash
node tools/draw-labels.mjs --raw runs/20261101T015849Z-live-baseline/raw-response.json --seed 20261031 --out labels
```

```bash
node tools/judge-batch.mjs --set dev --n 1-10 --prompt prompts/judge.v2.md --schema v2 --out experiment/v2-dev.jsonl
```

```bash
node tools/score.mjs experiment/v1-dev.jsonl experiment/v2-dev.jsonl
```

Exit codes from `watch.mjs`: 2 bad arguments, 3 persona or prefs validation failed, 4 refused fetch (host off the allow-list or a redirect), 5 malformed response, 6 a rule justification failed its own citation check.

## What ran (all on 2026-10-31 ET; UTC timestamps in folder names)

| Run | What | Result |
|---|---|---|
| `runs/20261101T015849Z-live-baseline` | live fetch, one request to `boards-api.greenhouse.io` (HTTP 200) | 745 postings; baseline, 0 reported as new; raw response saved; `state/seen-ids.json` written |
| `runs/20261101T020324Z-seeded-earlier` + `-seeded-baseline` | **SEEDED / CONSTRUCTED**, superseded | its draw removed a held-out labeling posting; kept for the record (`SUPERSEDED.md`) |
| `runs/20261101T020452Z-seeded-earlier-v2` | **SEEDED / CONSTRUCTED**: the live response with 8 postings removed (3 rule-relevant ids I chose, 3 PM-family not-relevant and 2 non-PM drawn with seed 20261031, labeling postings excluded) | 737 postings |
| `runs/20261101T020452Z-seeded-baseline-v2` | seeded baseline on the constructed response, own state file | 0 reported as new |
| `runs/20261101T020459Z-seeded-second-v2` | seeded second run against the real saved response, Claude judge on | exactly the 8 removed ids reported as new (`check-new-set`: PASS); rule and Claude verdicts in `report.md` |
| `sampling/v1-dev1-5-x4.jsonl` | prompt v1, dev postings 1–5, 4 fresh calls each | 20 calls, 0 invalid |
| `experiment/v1-dev.jsonl`, `experiment/v2-dev.jsonl` | prompt v1 and v2 on dev 1–10 | 10 + 10 calls, 0 invalid; v2 quote fidelity exact 10/10 |

No second calendar day was available before the deadline, so the change between runs is seeded and labeled as such. Tests: `node --test test/` ran 13 tests, 13 passing.

## Layout

| Path | What |
|---|---|
| `CONTRACT.md` | the contract, committed first (`5656bfb`) |
| `src/` | `watch.mjs` (runner), `fetch.mjs` (allow-list), `persona.mjs` (fictional-persona check), `state.mjs`, `rule.mjs` (six gates), `claude-judge.mjs` (prompt, validator) |
| `persona/` | the shipped fictional résumé (byte-for-byte copy) and `persona-prefs.json` (added preferences) |
| `prompts/` | `judge.v1.md` (baseline), `judge.v2.md` (one change: evidence quotes) |
| `test/` | tests, including one per wrong version in the contract; `fixtures/constructed-board.json` is constructed, not real |
| `runs/`, `state/` | saved raw responses, reports and state files |
| `labels/` | labeling rule, the seeded draw of 20 postings, their full texts, my hand labels |
| `sampling/`, `experiment/` | every Claude reply, raw, with date, model and session id |

## Sampling report

See `SAMPLING.md`.

## Prompt experiment

See `EXPERIMENT.md`.

## Action-surface comparison

See `ACTION-SURFACE.md`.

## Sign-off — Job-Search Agent 1

[Aravind to write: Checked / How / Not checked (at least three) / Not claiming / Signed or withheld]

## Driver's seat

[Aravind to write: what Claude did, what I did, why that part stays mine, with the commit or edit that shows the split]
