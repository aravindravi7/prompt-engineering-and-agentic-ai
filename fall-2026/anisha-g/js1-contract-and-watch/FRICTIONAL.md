# FRICTIONAL — Anisha Gaikar, JS1

**2026-10-31, ~5:07 pm** — Started on the due date. Asked Claude to build the assignment and ask me for what it needed. Claude couldn't reach any job-board API from its workspace (all three hosts refused by its proxy), so every real run happens on my Mac.

**2026-10-31, ~5:10 pm** — Picked defaults when asked: Klaviyo's Greenhouse board (same company as my Reallocation recipe), a new fictional persona, and the rule title + ≥2 skills + ≤3 years. Claude reused the HTML cleaning from my own `fetch-board.py`.

**2026-10-31, ~5:12 pm** — Claude's tests passed in its workspace (9 tests) and a fake-board / fake-Claude smoke test ran every command. Not yet run on real data.

**2026-10-31, ~5:37 pm** — Asked Claude to write the failure sentence; it drafted one, I read it and committed the contract as `9af05ef` before running anything.

**2026-10-31, ~5:38 pm** — Tests: 9 passed on my Mac. Run 1 (live, baseline): 156 postings, 0 new — correct for a baseline.

**2026-10-31, ~5:39 pm** — The label sheet came out with only **6** postings: Klaviyo had only 6 analyst/analytics titles, not 20. Claude patched `labels` to take all 6 analyst postings plus 14 random others (seed 7375). Accepted: it also gives the set clear negatives.

**2026-10-31, ~5:41 pm** — My first labelling attempt broke: pasting a script into Terminal left it stuck (`heredoc>`, `dquote>`), and the script couldn't read my typing through a heredoc. Claude rewrote it as `label.py`; I opened a fresh Terminal window. I hand-labelled all 20; I stopped once at #13 and found #12 (Manager, IT SOX) had the wrong reason pasted, so I fixed it and made `label.py` resume where it stopped. My labels: 19 `not_relevant`, 1 `relevant` (Senior CS Compensation Analyst).

**2026-10-31, ~5:55 pm** — Ran the experiment and sampling on my Mac: **all 60 Claude calls came back empty** and were rejected as `INVALID` by my validator — the validator did its job. Cause: `claude -p "Reply with only the word OK"` → "You've hit your individual spend limit" (exit 1). My Claude Code could not make any more calls tonight.

**2026-10-31, ~5:58 pm** — Decision: I sent Claude my run-1 raw response; Claude rebuilt the same 20-posting sheet with the same seed (it checked the ids and order matched mine exactly) and entered my labels as I had typed them, then ran dev, held-out and sampling with `claude -p` in its own workspace (each call a fresh conversation). Same code, same prompts, same raw data; only the machine differs. Unresolved: these Claude calls did not run on my machine.

**2026-10-31, ~6:00 pm** — Results: revised prompt 10/10 dev, 9/10 held-out; baseline 8/10 and 5/10, mostly from INVALID format (unknown `resume_fields`, and quoting the location line, which my validator rejects because it only checks title + body — a validator strictness I found, not a Claude invention). Sampling: 20/20 valid, 4/4 the same verdict on every posting — and 4/4 `not_relevant` on the one posting I labelled `relevant`.

**2026-10-31, ~6:05 pm** — Looked into that disagreement: the posting says "3–5 years"; my rule takes the top of the range (5 > 3). I read it as reachable at 3. Not changed tonight — logged as "not checked" in the sign-off.

**2026-10-31, ~6:05 pm** — Run 2: the board wasn't going to change within the evening, so I did the seeded run the assignment allows (run 1's real response minus its 3 newest ids, then the real response): 0 new, then exactly those 3 new, judged by both rule and Claude (all `not_relevant`, all valid).

**What I accepted / changed / rejected from Claude:** accepted the code, tests, prompts and doc drafts; changed the label sampling (6 → 20 postings) and the labeller after it failed; rejected letting Claude write the hand labels — those are mine.
