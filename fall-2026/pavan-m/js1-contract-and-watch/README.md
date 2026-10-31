# Job-Search Agent 1 — Contract and Watch

INFO7375, Pavan Majji. Folder: `fall-2026/pavan-m/js1-contract-and-watch/`

A small agent that watches one public job board (Glean on Greenhouse), remembers which postings it has seen, reports only new ones, and gives each new posting two labeled verdicts: a **record** from a written rule anyone can recompute, and a **judgment** from Claude under a fixed output format with a validator. Persona: **Alex Morgan, fictional** (`data/persona_alex.json`, `@example.com`, `555` phone). My real résumé is not in this repo.

## Language and toolchain
- Python 3.14.6, run in a project venv (created from Anaconda's Python 3.14.6)
- httpx 0.28.1 (Greenhouse requests), anthropic 2.3.0 (+ httpx2, required by the SDK), pytest 9.2.0; full list in `requirements.txt`
- Claude judgments: claude.ai (Northeastern account), Opus 5.5, fresh **incognito** chats, per TA instruction (no API key)
- Claude Code (desktop app) wrote the implementation against my contract and tests
- Timestamps in file names are local time (EDT, UTC−4)

## Run it from a fresh clone
```bash
cd fall-2026/pavan-m/js1-contract-and-watch
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -v                      # 9 tests, no network
```
Use `python -m pytest` rather than bare `pytest`, so the venv's pytest runs (Entry 5 in FRICTIONAL.md).

**Watch (live):** fetches the board, saves raw evidence, reports new ids
```bash
python -m agent.watch --resume data/persona_alex.json --state state/seen_ids.json --evidence evidence
```

To try it without changing the committed state and evidence, point it at temporary copies: `--state /tmp/js1_state.json --evidence /tmp/js1_evidence` (the first run there is a baseline).

**Watch (seeded):** same, but from a saved response, no network
```bash
python -m agent.watch --resume data/persona_alex.json --state state/seen_ids.json --evidence evidence \
  --seeded evidence/2026-10-30_manual-capture_gleanwork.json
```
**Claude judgment (copy-paste, same prompt builder and validator as agent/judge.py):**
```bash
python -m agent.manual_judge prompt --posting ID --version v1 \
  --evidence EVIDENCE_FILE --resume data/persona_alex.json --experiment NAME --attempt 1
# paste runs/NAME/v1/ID_a1_prompt.txt into a fresh incognito chat; save the reply as ID_a1_reply.txt
python -m agent.manual_judge check --posting ID --version v1 --experiment NAME --attempt 1 --model-label "TEXT"
python -m agent.manual_judge score --experiment NAME --version v1 --split dev
```
`agent/run.py` (watch + both judges via the API) exists but was **not run**: it needs an API key, and the TA said to use claude.ai instead.

## What ran (past tense, all October 30, 2026)
| Run | What | Result | Evidence |
|---|---|---|---|
| Manual capture | `curl` of the live board before the agent existed | 130 postings | `evidence/2026-10-30_manual-capture_gleanwork.json` |
| Run 1 — **seeded** baseline | agent on the manual capture, no state file | baseline, 0 new, 130 ids | `evidence/2026-10-30T113323_seeded_gleanwork.json`, `state/seen_ids_after_run1.json` |
| Run 2 — **live** | first real Greenhouse request, 4:29 PM | 0 new; board changed by 1 removal (4725753005); state kept 130 ids | `evidence/2026-10-30T162946_live_gleanwork.json`, `state/seen_ids_after_run2.json` |
| **CONSTRUCTED** demo | state copy minus 3 ids, seeded on Run 2's real response | 3 "new"; rule and Claude disagreed on 1 | `reports/CONSTRUCTED_DEMO.md` |

Run 2 found no new posting, so the both-judges path on a real new posting was shown only in the labeled CONSTRUCTED demo and in tests with fake data.

## Reports
- `CONTRACT.md`: written and committed before any code (`5c57972`), with two dated revisions at the bottom
- `reports/SAMPLING_REPORT.md`: 5 postings × 4 fresh chats; 20/20 consistent, 5/5 match my labels
- `reports/PROMPT_EXPERIMENT.md`: v1 vs v2 (one added line), 10 dev + 10 held-out; both 10/10 on each, vs a 7/10 always-not_relevant baseline; no measurable difference
- `reports/ACTION_SURFACE.md`: same task three ways, and my least-autonomy choice
- `labels/`: labeling rule, split (seed 7375), 20 hand labels
- `runs/`: every prompt, reply, and validator result
- `SOURCES.md`, `FRICTIONAL.md`

## Sign-off — Job-Search Agent 1

**Checked**
- Baseline reports 0 new and remembers all ids: `test_first_run_baseline_reports_zero_new_postings`; and by hand on real data (Run 1: 130 ids = `meta.total` 130)
- Seeded runs make no network request and save evidence unchanged: `test_seeded_run_uses_saved_response_without_greenhouse_request`; and by hand with `cmp` on Run 1's evidence copy
- Unapproved hosts and redirects are blocked in my code's client: `test_rejects_unapproved_hosts_and_redirects`
- Non-fictional résumé identity is rejected: `test_rejects_nonfictional_resume_identity`
- A failed fetch leaves the state file byte-for-byte unchanged: `test_failed_fetch_or_rule_preserves_previous_state`
- Verdicts stay attached to their own posting ids: `test_verdicts_remain_associated_with_correct_posting_ids`
- Every rule verdict, including negatives, cites résumé and posting fields: `test_every_verdict_has_resume_and_posting_field_evidence`
- Skill matching (JavaScript ≠ Java, repeats once, decode-then-strip, threshold 3): `test_skills_require_three_distinct_whole_word_matches`
- Invalid Claude replies are retried exactly once, then marked invalid: `test_invalid_judgment_retries_once_then_marks_invalid`
- - Every Claude reply passed `validate_reply`: 59 reply files in `runs/`; 58 are Claude replies, all valid; 1 (`runs/sampling_r3/v1/4605446005_a1_reply.txt`) holds text from my own copy error, not a Claude reply, and was correctly rejected
- Removals between runs are not reported as new: by recomputation of id sets (morning 130 vs live 129)

**How**
- Tests written by me before reading Claude's code: watch tests (`47fef3f`, `7620c75`) before `5e30eac`; rule/judge tests (`86b9864`) before `7bbd664`. `git diff tests/` was empty after each implementation.
- By hand: 20 labels, the labeling rule, `cmp`, id counts, reading Claude Code's action lists, `git status`.
- With Claude's help: Claude Code wrote all of `agent/` (including the `score` command I used for pass rates). Claude (chat) helped me break down the assignment, reviewed my contract drafts, suggested the test structure and interface, and drafted the reports and this README from my results, which I checked against `runs/`.

**Not checked** 
1. No real new posting appeared, so "both judges on a real new posting" ran only in the CONSTRUCTED demo.
2. Whether Claude's justifications are true: the validator checks structure and field names only.
3. The real API path (`make_call_model`, the httpx2 allow-listed client) was never called for real; it was only checked offline by Claude Code with a mock.
4. `agent/run.py` end to end.
5. Atomic state writes under a real crash (only a failed fetch was tested).
6. A posting edited but keeping the same id; pagination or very large responses; any board other than Glean.
7. My allow-list does not constrain an agent with shell access (Way 3 used `curl` directly).

**Not claiming**
- That the agent finds good jobs, or that any verdict is correct. My labels are one person's judgment.
- That v2 is better than v1, or that results generalize beyond 20 postings, one company, one persona, one model, one day.
- That Claude's verdicts are stable in general; only 5 postings × 4 samples were measured.

**Signed or withheld:** Signed - Pavan Jayant Majji(name, date)

## Driver's seat
| Part of the task | Claude did | I did | Why it stays mine | Evidence |
|---|---|---|---|---|
| The contract | Reviewed drafts, pointed out gaps | Wrote all drafts and decisions | It defines what "correct" means | `5c57972` before any code; FRICTIONAL Entry 3 |
| Relevance rule | Pointed out "semantic" isn't hand-checkable | Chose thresholds, exclusions, fail-on-missing location | Only I decide what's worth a day of Alex's time | FRICTIONAL Entry 2; CONTRACT.md "The rule" |
| Tests | Suggested structure; caught my indentation bug | Wrote every assert, before the code | Tests must not come from the code they test | `47fef3f`, `7620c75`, `86b9864` before `5e30eac`, `7bbd664` |
| Implementation | Claude Code wrote `agent/` | Ran tests myself; reviewed and accepted its choices | Writing code is where Claude is strong | `5e30eac`, `7bbd664`; FRICTIONAL Entries 8, 11 |
| Hand labels | Nothing | Labeling rule, picks, split, 20 labels | They're the yardstick Claude is scored against | `da045ca`, `6fcc504` before first Claude run `80b533d` |
| Prompts | Suggested format fixes (no fences) | Wrote v1; chose v2's one change | The experiment tests my decisions | `9e4136f`, `a6f1125`; FRICTIONAL Entries 15, 19 |
| Judgments | Claude judged each posting | Ran every chat; kept the validator in charge | A model's opinion must be labeled and checked | `runs/`; FRICTIONAL Entries 17, 21 (my errors, logged) |
| Autonomy choice | Way 3 agent ran with full access | Chose least autonomy; documented what it did beyond the task | Authority is a decision, not a default | `a2d9537`; `reports/ACTION_SURFACE.md` |
| Sign-off | Drafted the wording | Chose what's "Not checked"; signed or withheld | Only I know what I didn't test | This section |