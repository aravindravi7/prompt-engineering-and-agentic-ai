# FRICTIONAL — Job-Search Agent 1

## Entry 1 — October 29, 2026: Choosing the board
Companies checked:
1. Glean: Glean's board showed `meta.total: 133` when I checked on Oct 29, spanning engineering and non-engineering roles, including recent listings (one Software Engineer posting had `first_published` of Oct 22, 2026).
2. Palantir: uses Lever rather than Greenhouse for its careers board; its listings include software engineering roles in backend, infrastructure, and developer productivity.
3. Capital One: uses Workday for its careers board; its listings include technology roles involving Java, Python, AWS, and full-stack engineering.

Selected: Glean (slug `gleanwork`). Its 133 postings give a broad mix of engineering and non-engineering roles, including recent listings, so the agent should produce both relevant and not-relevant verdicts. Glean's enterprise search platform also connects with my background in Java/Spring Boot microservices, large-volume trade data, and cloud-native infrastructure.

Decision: Palantir and Capital One were considered, but their boards use Lever and Workday rather than Greenhouse, so they don't fit this Greenhouse-based watch.

## Entry 2 — October 29, 2026: Persona and rule fields
Created a fictional persona, Alex Morgan (`@example.com` email, `(617) 555-0147` phone), instead of using my real résumé. First phone format was `555-014-7823`; changed to `(617) 555-0147` after Claude pointed out the conventional fictional format.
First draft of my rule fields included `id` and `departments` and used `"match_type": "semantic"`. Changed after review with Claude:
- Removed `id` from the rule; it is used only for new-since-last-run tracking.
- Removed `departments`, because Alex's résumé has no matching field.
- Replaced semantic matching with mechanical matching, because semantic similarity is a judgment a TA can't recompute by hand. That belongs to the Claude judge, not the rule.
Accepted: the field pairing target_titles↔title, skills↔content, locations↔location.name.

## Entry 3 — October 29, 2026: Contract committed before implementation
Revised CONTRACT.md three times after review with Claude before committing:
- Draft 1 → 2: added raw-response saving, seeded runs, the Claude output schema and validator, HTML decode-before-strip order, and the rule that a Claude failure does not block the state update; removed "optional" from the Claude step.
- Draft 2 → 3: made email/phone required (they were listed as optional but required by the validator); removed two claims the code can't check (truthfulness of Claude's justification; fictional employment history); added "internship" to title exclusions; decided Claude may cite experience/education but not name/email/phone.
Committed alone, before any code: `5c579720e624de0fe41e21301a636814583f0973` (Oct 29, 17:55 EDT).

## Entry 4 — October 29, 2026: Environment setup
Created a venv inside the project folder (instead of conda base) so the TA can reproduce it. Python 3.14.6; installed httpx 0.28.1, anthropic 2.3.0, pytest 9.2.0; saved `requirements.txt` with `pip freeze`.
Noticed: anthropic 2.3.0 pulled in a dependency called `httpx2`, not `httpx`. My contract says the Anthropic call must go through a custom `httpx` client for the host allow-list. Unresolved: whether the SDK accepts a plain `httpx` client, or whether the allow-list for the Claude call must use `httpx2`. To check when building the judge step.

## Entry 5 — October 29, 2026: First test written before implementation
Wrote `test_first_run_baseline_reports_zero_new_postings` in `tests/test_watch.py` before any code in `agent/watch.py` existed.
Noticed: the bare `pytest` command ran conda's pytest 9.0.3 from /opt/anaconda3 instead of the venv's pytest 9.2.0, because conda base was also active. Changed to `python -m pytest` so tests run in the venv; README uses that command.
First failing run: `ModuleNotFoundError: No module named 'agent.watch'` (expected; no implementation yet).

## Entry 6 — October 30, 2026: First test written before implementation
Push was rejected because classmates had pushed to the shared repo; ran `git pull --rebase --autostash`, which changed the commit hash to `47fef3fb16b721ed04fc763a93840f12b6531023`.

## Entry 7 — October 30, 2026: Watch tests 2–5 written before implementation
Wrote the asserts for tests 2–5 before any code in agent/ existed.
Mistake caught in review with Claude: tests 3, 4 and 5 were indented inside test 2, so pytest would never have collected them; the suite would have reported 2 passing tests while host blocking, résumé validation and state preservation were untested. Also missing the write_resume helper. Fixed the indentation and added the helper; asserts unchanged.
Lesson: run `python -m pytest -v` and count the test names, not just "passed".

## Entry 8 — October 30, 2026: Claude Code implemented the watch
Gave Claude Code (desktop app, Code tab) the watch prompt after confirming with `pwd`/`ls` that it was in js1-contract-and-watch. It created agent/net.py, agent/resume.py, agent/watch.py.
Verified myself: `python -m pytest -v` → 5 passed in my venv; `git diff tests/` empty (tests untouched).
Choices Claude Code made that my spec didn't cover, all accepted: usable id = integer; duplicate ids in one response counted once; seen_ids written sorted; evidence filenames in local time with `_1` suffix on same-second collisions (noted in README).
Noticed: Claude Code ran a CLI check writing scratchpad files outside this folder, although my prompt said not to touch anything outside it. Harmless, but the agent acted slightly beyond its instructions; noted for the action-surface comparison.
Not yet checked: Claude Code never ran live mode; the real Greenhouse fetch is untested.
