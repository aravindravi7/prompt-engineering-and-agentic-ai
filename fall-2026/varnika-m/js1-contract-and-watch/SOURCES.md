# SOURCES — Job-Search Agent 1

What I used, what I wrote, and what Claude contributed. Updated as the work goes.

## What I used

| Source | What I took from it |
|---|---|
| The Reallocation Engine, `nikbearbrown/the-reallocation-engine` (my local fork, read only), `search/examples/aarav-patel/resume.example.json` at commit `d08afdd` | The fictional persona résumé, copied unchanged to `persona/aarav-patel.resume.example.json` (SHA-256 `f6ee24e4174370794da5a8c43167020e012821a9dcbfc04a99874ec379495c6e`) |
| Anthropic's public Greenhouse job board, `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` | The postings the agent watches |

## What Claude contributed

| Date | Part | What Claude Code (Opus 5.5) did | What I did |
|---|---|---|---|
| 2026-10-31 | Board check | Made one read-only request to the board at 06:00:09 UTC, to confirm it is public and to see the posting fields. That copy was kept outside this folder. It was not a run of the agent and is not part of the evidence. | Chose the board (Anthropic) and the persona (Aarav Patel) |
| 2026-10-31 | Discarded contract draft | At my request, wrote a full contract draft and chose its thresholds after trying them on the titles and descriptions from the board check. The draft was never committed. | Discarded it and wrote my own `CONTRACT.md` (below). |
| 2026-10-31 | Reviews of my `CONTRACT.md` | Reviewed my drafts three times against the assignment and the board data. **First review:** flagged no named fields in Out, an unclear Rule 3, an unclear Rule 4 (which phrases count, required vs preferred), a failure sentence that described error handling, wrong versions without named tests, and missing raw-response, seeded-run, Claude-judge and fictional-résumé-check lines. It suggested recognising US locations by "United States" or a state code after a comma, gave the three location strings now used as Rule 3's examples, quoted the years phrases now used as Rule 4's examples, gave the 25 + 4 = 29 months calculation, and gave an example test sentence for wrong version 1. **Second review:** flagged that Rule 4 said two different things and offered two mechanical options. It also suggested "Python 3.9 or later", a state-file path, and a fetch-failure line. **Third review:** a final check. It checked Rule 3 against all 26 locations on the board, and Rule 4 and the whole rule against the board snapshot (1 match of 675). | Rewrote each flagged part myself, in my own words. Chose option (a) for Rule 4. |
| 2026-10-31 | `tests/` (69 tests) | Wrote all the tests from `CONTRACT.md`, after it was committed (`93afbb8`) and before any implementation existed. My two wrong-version test sentences became `test_wrong_version_1_…` and `test_wrong_version_2_…` in `tests/test_rule.py`. The tests failed at first because there was no `agent` package yet. | *[Varnika: what you checked in the tests against your contract]* |
| 2026-10-31 | Wording edits in `CONTRACT.md` | At my request: added to Rule 4 that a range may use a hyphen or a dash. Then, at the final check, labeled the worked example as constructed, and spelled out the validator (`label` must be exactly `CLAUDE_JUDGMENT`, `reason` must not be empty, no text outside the JSON). | Asked for the edits |
| 2026-10-31 | `CONTRACT.md` "Changes" section | At my request, after the first commit: wrote the dated addition naming the résumé fields Rules 1–3 cite. Writing the tests had found that gap. | Agreed with the fields and asked for the addition |

## What I wrote

| Date | Part | Notes |
|---|---|---|
| 2026-10-31 | `CONTRACT.md` | Written in my own words after discarding Claude's draft. **Kept from Claude's draft:** the Rule 1 title list, the Rule 2 seniority list, the 15 skills and the two-skill threshold in Rule 5, the three-year limit in Rule 4, and excluding `familiar_with_not_shipped`. **From Claude's reviews** (see above): Rule 3's method and its example strings, Rule 4's option (a) and its example phrases, the 29-month figure, and the wording of wrong version 1's test. **My own:** all the wording of In, Out and Refuses, Rule 4's choices (counting preferred qualifications, using the higher number of a range, not counting spelled-out numbers), the reason for the three-year limit, the Claude JSON format, the two wrong versions, and the failure sentence. |
