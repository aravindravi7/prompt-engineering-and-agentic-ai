# Job-Search Agent 1: the contract and the watch

**Hemanth Rayudu, INFO 7375, Fall 2026.** One board, one résumé, new postings only, and every verdict justified.

- **The board:** Anthropic's public Greenhouse board.
- **The résumé:** **Priya Nair**, a fictional persona from The Reallocation Engine (`@example.com`, 555 number). My real résumé isn't in this folder or anywhere in git.

The agent fetches the board from one allow-listed host and saves the raw response as evidence. It remembers posting ids and reports only postings new since the last run. Each new posting gets two verdicts, side by side:

- a **record** from my written rule (anyone can recompute it);
- a **judgment** from Claude under a prompt contract, with a validator that rejects any other format. The agent uses prompt **v2** (`prompts/judge_v2.md`, which includes the written rule), my choice after the prompt experiment. The seeded runs above used v1, the default at the time.

It never applies, emails, messages or logs in.

| File | What it is |
|---|---|
| [`CONTRACT.md`](CONTRACT.md) | In / Out / Refuses / the rule / two wrong versions / the failure sentence. Committed alone, before any code, as `b88cdbb` |
| `jsagent/` | the agent: `watch.py` (allow-list, fetch, raw evidence, new-by-id), `rule.py` (the record), `claude_judge.py` (the judgment and validator), `resume.py` (persona validation; contact fields never leave), `cli.py` |
| `tests/` | 27 tests, including the two wrong versions from the contract (`test_wrong_versions.py`) |
| `runs/`, `state/`, `evidence/seeded/` | raw responses (gzipped, with SHA-256 of the original bytes), reports and state files from the real runs |
| [`SAMPLING-REPORT.md`](SAMPLING-REPORT.md) | Chapter 1: 5 postings × 4 fresh conversations |
| [`PROMPT-EXPERIMENT.md`](PROMPT-EXPERIMENT.md) | Chapter 2: 20 hand-labeled postings, baseline vs. one change, dev vs. held-out |
| [`ACTION-SURFACE.md`](ACTION-SURFACE.md) | Chapter 3: the same task done three ways, and the least autonomy that suffices |
| `experiment/`, `action-surface/`, `prompts/`, `scripts/` | labels, every Claude answer, the two prompts, the helper scripts |
| [`SOURCES.md`](SOURCES.md), [`FRICTIONAL.md`](FRICTIONAL.md) | what I used and what Claude contributed; my log |

## Language, toolchain, exact commands

- **Language and libraries:** Python 3.9.10. Standard library only, plus `pytest` 8.3.3 for the tests.
- **Claude Code:** 2.1.316, which runs the Claude judge through `claude -p` (no API key).
  - The rule judge, the watch and every test run **without** Claude Code.
  - Model used for every recorded call: `claude-sonnet-5-5`.
- **Tested on:** macOS.

```bash
cd fall-2026/rayudu-h/js1-contract-and-watch
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q                      # 27 tests, no network, no Claude

# one watch run (live fetch; the Claude judge needs Claude Code logged in; add --no-claude to skip it)
.venv/bin/python -m jsagent run --board anthropic --resume persona/priya-nair.resume.json

# to try it without touching the committed state, give it a fresh state file:
.venv/bin/python -m jsagent run --board anthropic --resume persona/priya-nair.resume.json \
    --state /tmp/js1-seen.json --runs-dir /tmp/js1-runs --no-claude
```

- **The first run against a state file is a baseline:** it reports nothing as new.
- **Each run writes `runs/<timestamp>/`:**
  - `raw.json.gz` and `raw.meta.json`, the raw response and its SHA-256;
  - `report.md`;
  - `run.json`;
  - `judgments.jsonl`, when there are new postings.
- **It also updates the state file.**
- **Reproducing the reports:**
  - `scripts/analyze.py sampling` and `scripts/analyze.py experiment dev|heldout` recompute every number from the saved files.
  - `scripts/claude_batch.py` re-runs the Claude calls. Expect different answers on some postings; see the sampling report.

## What ran (Oct 31, 2026, ET)

| Run | What | Result |
|---|---|---|
| `runs/2026-10-31T144337/` | **live baseline**, real fetch | 675 postings, none reported as new. Raw sha256 `1e5b62fe…7e88`, byte-identical to a fetch made at 03:36 while writing the contract: the board didn't change all day Saturday |
| `runs/2026-10-31T144406-seeded/` | **SEEDED baseline** on an earlier response made by `scripts/make_seeded_earlier.py` (the real response minus the 9 postings first published Oct 30) | 666 postings, none new |
| `runs/2026-10-31T144406-seeded-2/` | **SEEDED second run** on the real response | **9 new**. Rule and Claude (v1) agreed on all 9: "Data Engineer" relevant, 8 not relevant |
| [second live run: filled in after it runs] | live fetch against the live baseline's state | [result] |

The second calendar day falls after the deadline. That's why the pair of runs with a change between them is the **seeded** pair, labeled as such in each report.

## Sign-off — Job-Search Agent 1

```text
Sign-off — Job-Search Agent 1
Checked:      [Hemanth: which properties, by which of your own tests — e.g. the hand-worked
              example in CONTRACT.md; your 10 dev hand labels vs the rule code (10/10);
              the two wrong-version tests; reading the seeded-2 report]
How:          [by hand / by a test I wrote before reading Claude's code / by recomputation /
              with Claude's help (say which parts): note the tests were written by Claude
              from your contract, and the held-out labels used Claude's skill-evidence script]
Not checked:  [at least three real items, e.g.: a real (unseeded) second-day change on the
              board; whether "relevant" by my rule means a job is actually worth Priya's
              time; Claude's verdicts beyond one call per posting in the experiment;
              any board other than Anthropic; redirects to an off-list host (code exists,
              no test against a live redirect)]
Not claiming: [e.g. that Claude's judgment is correct; that the rule finds good jobs;
              that 10 held-out postings estimate an error rate]
Signed or withheld: ____________ (name, date)
```

## Driver's seat

| Part of the task | Claude did | I did | Why it stays mine | Where it shows |
|---|---|---|---|---|
| The contract | wrote the boilerplate; asked one question at a time; checked facts (fields, counts) before each choice | chose the board, persona, rule, edge cases, refusals, wrong versions and failure sentence | the rule decides what counts as "worth my time"; Claude can't know that | `CONTRACT.md` authorship note; commit `b88cdbb` before any code |
| The worked example | kept its own script's answer hidden until I'd answered | checked the posting by hand; then **changed my rule** when my reason ("it's a manager role") wasn't in it | a TA must be able to predict my verdicts from my rule | `CONTRACT.md`, worked example and the seniority line |
| Hand labels | built the skill-evidence sheet (no verdicts) and caught that "AWS" was only inside "Laws" | labeled all 20; relabeled #1 and #2 when my instinct didn't follow my rule | the labels are the ground truth the experiment is scored against | `experiment/labels.csv`, `first_instinct_label` and `note` columns |
| Scope | showed that multi-board is JS2 and that Databricks would break the rule | decided to keep one board (Anthropic) | what the agent watches is my call | `FRICTIONAL.md`, Oct 31 ~2:50 PM entry |
| Code, tests, reports | wrote them against the contract and ran them | [Hemanth: what you reviewed or ran yourself] | I'm responsible for what's submitted | git history |
