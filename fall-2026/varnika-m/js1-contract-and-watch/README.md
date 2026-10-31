# Job-Search Agent 1 — The Contract and the Watch

Varnika M · INFO 7375, Fall 2026

The agent watches one public job board: Anthropic's Greenhouse board. Each time it runs, it reports only the postings that are new since the last run. Each new posting gets two verdicts against a fictional résumé (Aarav Patel):

- a **record** from my written rule, which anyone can recompute;
- a **judgment** from Claude, which is labeled as an opinion.

The specification is [CONTRACT.md](CONTRACT.md). Who did what is in [SOURCES.md](SOURCES.md), and the process log is in [FRICTIONAL.md](FRICTIONAL.md).

## Language and toolchain

| What | Version | Needed for |
|---|---|---|
| Python, standard library only | 3.9 or later (tested on 3.9.6, macOS) | everything |
| Claude Code CLI (`claude`), logged in | tested with 2.1.283 | only the `--claude` judgment step |
| Network access to `boards-api.greenhouse.io` | n/a | only live runs |

Nothing needs to be installed. There is no `requirements.txt`, because nothing outside the standard library is used.

## Commands

Run everything from this folder:

```bash
cd fall-2026/varnika-m/js1-contract-and-watch
```

**Tests.** These run offline, without Claude, on constructed postings only:

```bash
python3 -m unittest discover -s tests -t . -v
```

**A live run.** This fetches the board once and writes into `evidence/raw/`, `runs/` and `state/`:

```bash
python3 -m agent.watch                 # rule verdicts only
python3 -m agent.watch --claude        # also ask Claude about each new posting
```

**A seeded run** from a saved response. The run record and the report label it `seeded`:

```bash
python3 -m agent.watch --fixture path/to/saved-response.json
```

The first run is the baseline: it records every posting id and reports none as new. Each later run reports only the ids that are not in `state/anthropic.state.json`.

## What is in this folder

| Path | What it is |
|---|---|
| `CONTRACT.md` | In, Out, Refuses, the rule, wrong versions, failure; written before any code |
| `persona/aarav-patel.resume.example.json` | The fictional résumé (`@example.com`, 555 phone) |
| `agent/` | The code: `watch.py` (the run), `rule.py` (Rules 1–5), `claude_judge.py` (prompt, call, validator), `fetch.py` (allow-list), `resume.py` (fictional check) |
| `prompts/baseline-v1.txt` | The prompt for Claude's judgment |
| `tests/` | 72 offline tests |
| `evidence/raw/` | Every raw board response, byte for byte, gzip-compressed (`gunzip -c FILE` restores it) |
| `runs/` | One JSON record and one Markdown report per run |
| `state/anthropic.state.json` | Every posting id seen so far, and the list of runs |

## What ran

*No runs yet. Run 1 (the live baseline) and run 2 (a second calendar day) will be logged here, with their dates and files.*
