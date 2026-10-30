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

## Entry 9 — October 30, 2026: Run 1, seeded baseline
Ran the agent on evidence/2026-10-30_manual-capture_gleanwork.json with no state file:
mode seeded, baseline true, new_ids [], invalid_postings []. Evidence saved as evidence/2026-10-30T113323_seeded_gleanwork.json.
Checked myself: state contains 130 ids (matches meta.total 130); `cmp` confirmed the evidence copy is identical to the capture.
Kept a copy as state/seen_ids_after_run1.json so both runs' state can be submitted.

## Entry 10 — October 30, 2026: Rule and judge tests written before implementation
Wrote asserts for tests covering wrong versions #1 (shifted labels: same verdicts when input order is reversed), #2 (evidence on every verdict, including negative), #5 (JavaScript≠Java, repeats count once, decode-then-strip order, case-insensitive), #6 (retry once, then invalid).
My own addition: Case C also asserts exactly 2 calls, so the code must retry rather than give up after one bad reply.
The judge test uses a fake model function, so no real API calls and no cost.

## Entry 11 — October 30, 2026: Claude Code implemented the rule and judge
Verified myself: `python -m pytest -v` → 9 passed; `git diff tests/` empty.
Resolved from Entry 4: anthropic 2.3.0 accepts only an `httpx2.Client`. Claude Code checked offline with a mock transport that the host-check hook runs on SDK requests and blocks a redirect hop to an unapproved host, then added `make_anthropic_http_client()`. It also set `max_retries=0` so the SDK doesn't retry on its own, keeping the judge's single retry the only one.
Updated CONTRACT.md in a separate commit to say httpx2 for the SDK (dated revision note).
Accepted Claude Code's choices: id not citable; retry resends the same prompt without the error; plain-text placeholder filling; optional --model flag; tags replaced with a space so words don't merge.
Not yet checked: `agent.run` end to end, since it would call the real API (no API key yet; asked TA).

## Entry 12 — October 30, 2026: Labeling rule written before labeling
Wrote labels/LABELING_RULE.md at 1:10 PM ET, before reading any posting closely. It is my own judgment of relevance for Alex, deliberately different from the contract rule in three ways: it accepts platform/infrastructure/data engineering roles, excludes Staff/Principal, and accepts any workable US location. These differences are expected to explain some disagreements between the rule's record verdicts and my hand labels.
After review with Claude, added a section listing those differences, a note that my labels are one person's judgment rather than ground truth, and the selection method (14 technical + 6 non-technical, by title only; random split with seed 7375).

## Entry 13 — October 30, 2026: Picking the 20 postings
First pick had duplicate titles (3 × "Software Engineer", 2 × "Customer Advocacy Manager"), which broke my own selection method ("avoiding duplicate titles"). Replaced 4746919005 and 4746918005 (Software Engineer) with 4614706005 (Software Engineer, Developer Productivity) and 4746685005 (Software Engineer, Native Mobile), and 4743028005 (Customer Advocacy Manager) with 4746354005 (Office Manager).
No Staff or Principal engineering posting is in the set, so my labeling rule's Staff/Principal exclusion is not tested by these 20.
Noticed: three postings use "San Francisco Bay Area", which the contract's location check will reject but my labeling rule may accept.

## Entry 14 — October 30, 2026: Hand-labeled 20 postings before any Claude run
Labeled all 20 using only labels/LABELING_RULE.md. Result: 6 relevant, 14 not_relevant (dev 3/10 relevant, held-out 3/10 relevant).
Noticed while labeling: required years of experience became a deciding factor for 5 postings (e.g. APIs & Context Platform: strong fit but 8+ years). My rule only implies this through "reasonably fits his experience"; I did not edit the rule after labeling.
Implication: a prompt that always answers not_relevant would score 70% on each split; pass rates must be compared against that.
Picked 5 for sampling: 2 clear relevant, 1 clear not_relevant, 2 borderline (APIs & Context Platform; AI & Security).

## Entry 15 — October 30, 2026: Baseline prompt and switch to manual Claude chats
TA confirmed we should use the Claude and Claude Code access Northeastern provides, not a paid API key. Plan: the code builds each prompt, I paste it into a fresh claude.ai chat, save the reply to a file, and the same validator checks it.
Wrote prompts/judge_v1.txt myself. Before any run, added (after review with Claude) a line forbidding markdown fences and labels for the résumé/posting blocks, since claude.ai often fences JSON and my validator rejects fences.
Order decided: sampling runs last, because 2 of the 5 sampling postings are in the held-out set.

## Entry 16 — October 30, 2026: Copy-paste helper; fixed stray markers in v1
Claude Code built agent/manual_judge.py (prompt / check / score), reusing build_prompt and validate_reply from agent/judge.py; it renamed two private helpers in judge.py so they could be imported. Verified myself: 9 tests pass, `git diff tests/` empty.
Claude Code added unrequested safeguards, which I accepted: a meta file that fingerprints the prompt inputs, refusing attempt 2 unless attempt 1 was invalid, and refusing to re-check an already-recorded attempt.
Claude Code flagged that my committed prompts/judge_v1.txt still contained "← NEW" markers from review notes, which would have been sent to Claude. Removed them before any Claude run; v1 is now the version in the commit below.
Also added a second dated contract revision: the judgment goes through claude.ai chats instead of the API, per TA.

## Entry 17 — October 30, 2026: v1 on the dev set
Ran prompts/judge_v1.txt on the 10 dev postings, one fresh claude.ai incognito chat each (Opus 5.5). All 10 replies passed the validator on attempt 1 (after fixing my copy-paste mistake on 4746908005, Entry 17). v1 agreed with my hand labels on 10/10 dev postings; a prompt that always answers not_relevant would score 7/10.
Implication: v1 is already at 100% on dev, so a revision cannot show improvement on this set; it can only stay the same or get worse. Ten cases are too few to conclude v1 is generally reliable.

## Entry 18 — October 30, 2026: v2 = v1 plus one line about experience level
v1 scored 10/10 on dev, so a revision cannot show improvement on dev; the held-out set is where the change is actually tested.
Chose one change: added "Treat a posting as not relevant if the years of experience it requires clearly exceed the candidate's experience." Reason: required years decided 5 of my hand labels, and 4 held-out postings require 5+ years, but v1 never mentions experience level.
Honest limit: this line brings one factor from my own labeling rule into the prompt, so better agreement would partly mean Claude is closer to my judgment, not that it is more correct.
`diff prompts/judge_v1.txt prompts/judge_v2.txt` shows exactly one added line.

## Entry 19 — October 30, 2026: v2 on the dev set
Ran prompts/judge_v2.txt on the same 10 dev postings, one fresh claude.ai incognito chat each (Opus 5.5). All 10 valid on attempt 1; 10/10 agreed with my hand labels, the same as v1. As expected, dev cannot separate v1 from v2; the held-out set is the real test.

## Entry 20 — October 30, 2026: Held-out results
Ran v1 and v2 on the 10 held-out postings (20 fresh claude.ai incognito chats, Opus 5.5). All 20 valid on attempt 1 (after redoing one copy-paste mistake on 4696752005 v1, same cause as Entry 17). v1: 10/10 agree; v2: 10/10 agree; always-not_relevant baseline: 7/10.
Conclusion: my one change (experience-level line) produced no measurable difference. Both prompts hit the ceiling on all 20 cases, so this set cannot tell them apart. v1 already weighed required years on its own (e.g. 4696752005, 8+ years, judged not_relevant by both).

## Entry 21 — October 30, 2026: Held-out results
Ran v1 and v2 on the 10 held-out postings (20 fresh claude.ai incognito chats, Opus 5.5). All 20 valid on attempt 1 (after redoing one copy-paste mistake on 4696752005 v1, same cause as Entry 17). v1: 10/10 agree; v2: 10/10 agree; always-not_relevant baseline: 7/10.
Conclusion: my one change (experience-level line) produced no measurable difference. Both prompts hit the ceiling on all 20 cases, so this set cannot tell them apart. v1 already weighed required years on its own (e.g. 4696752005, 8+ years, judged not_relevant by both).

## Entry 22 — October 30, 2026: Sampling report
Ran 15 more fresh incognito chats (r2–r4) on the 5 sampling postings with v1; reused each posting's v1 prompt-experiment chat as r1. All 5 postings gave the same verdict 4/4 times, matching my hand labels. One retry on 4605446005 r3, caused by my copy error (the a1 reply file holds text from my help chat); attempt 2 in a new chat was valid.
Wrote reports/SAMPLING_REPORT.md and reports/PROMPT_EXPERIMENT.md; Claude drafted both from my results, and I checked the numbers (40 reply files in runs/prompt_exp/, scores from `manual_judge score`).

## Entry 23 — October 30, 2026: Run 2, live
Ran the agent live at 4:29 PM ET (first real Greenhouse request through the allow-listed client): mode live, baseline false, new_ids [], invalid_postings []. Evidence: evidence/2026-10-30T162946_live_gleanwork.json.
Compared with Run 1's input: morning 130 postings, now 129; 0 added, 1 removed (4725753005). The board changed between runs, but only by a removal, so 0 new is the correct answer. State still holds 130 ids, because removed ids are kept, as the contract says. Saved state/seen_ids_after_run2.json.
Limitation: no real new posting appeared, so the "both judges on each new posting" path did not run on a real new posting in Run 2.

## Entry 24 — October 30, 2026: CONSTRUCTED demo of both judges
Because Run 2 had 0 new postings, built a clearly labeled CONSTRUCTED demo: copied Run 1's state minus 3 ids and ran seeded on Run 2's real response. The agent reported exactly those 3 as new. Rule and Claude (3 fresh incognito chats, all valid) agreed on 2 and disagreed on 4696752005: the rule said relevant (3 skills matched) but cannot see the 8+ years requirement; Claude and my hand label said not_relevant. Wrote reports/CONSTRUCTED_DEMO.md. Real state files were not modified.