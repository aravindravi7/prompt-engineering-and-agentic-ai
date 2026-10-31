# FRICTIONAL: JS1

Entries are dated by when the work happened. I wrote this log on 2026-10-31 from my notes, the commits and
a factual session log Claude Code kept, so the earlier entries are **retrospective**. The "What happened"
and "Evidence" lines are facts organized by Claude Code; the rest is mine.

## 2026-10-29: choosing a board

- **I tried / expected:** [Ashwin]
- **What happened:** Claude Code probed six public Greenhouse boards (Datadog, Cloudflare, Stripe, Airbnb,
  Databricks, Robinhood) for job counts and SWE/backend titles. I picked Cloudflare, and we saved a raw
  snapshot before writing the contract so its date would be in git first.
- **Evidence:** `083428b` (snapshot only).

## 2026-10-30: the contract, and switching boards twice

- **What happened:**
  - My first contract draft named Datadog. Applied by hand to a live Datadog fetch, my rule gave **0 relevant**:
    6 titles passed the title check, and all 6 failed seniority. Cloudflare also gave 0, because no office was in Boston or a "Remote - US" format.
  - Claude Code checked four Boston-area boards with the same rule. Klaviyo gave 4 of 156, so I rewrote the
    contract for Klaviyo. The Cloudflare snapshot stayed in the repo, unused.
  - In draft 2, Claude Code flagged that I wrote "nine fields" (the JSON has 8), "Claude API request" (we use
    `claude -p`), and that validation rule 8 allowed an empty quote. I renamed the persona to Supriya Sharma.
- **What I did:** [Ashwin: what you accepted, changed or rejected]
- **Evidence:** `470fae3` (contract, before any code); edits listed in SOURCES.md.

## 2026-10-30: implementation, my test run, run 1

- **What happened:**
  - Claude Code implemented against the contract (`15d6b3f`). I ran the tests myself: 48/48 OK.
  - I ran the live baseline at 23:25:13 UTC, before the UTC date changed, so run 2 the next day would be a second calendar day. 156 postings, 0 reported new (`d093ecf`).
  - Checking the worked example against the real posting showed it says "Postgres", not "PostgreSQL", so my
    rule correctly does not count it (`93687a1`).
  - A development smoke call had Claude answer NOT_RELEVANT on my worked example ("2+ years"), while my rule says RELEVANT.
- **I understand now / still do not:** [Ashwin]

## 2026-10-31: run 2

- **What happened:** live run at 16:09:43 UTC: the same 156 ids, **0 new**. 8 postings had a changed
  `updated_at` and none was reported as new, which is the by-id behavior I specified.
- **Evidence:** `26bf8fe`.

## 2026-10-31: the seed, and running steps out of order

- **What happened:**
  - I typed `--seed YOUR_NUMBER` literally from the instructions, then tried `label`, `sample` and
    `experiment` before a selection existed. Each one stopped with "selection.json does not exist yet".
  - After asking what a seed is, I chose 2608 (`9ed2e88`).
- **What I did / learned:** [Ashwin]

## 2026-10-31: writing the labeling rule

- **What happened:** my point 3 said "up to 2 years". Claude Code asked how that treats a posting that says "2+ years".
  I added: "2+ years" counts as 2 and is acceptable; "3+ years" is Not Relevant (`20b01fb`).
- **Note:** this question came from my worked-example posting, which later landed in the held-out set (see the next entry).

## 2026-10-31: all 20 labels came out Not Relevant

- **What happened:**
  - My 20 labels were all NOT_RELEVANT (`6773f06`). The seed had picked mostly Senior, Staff and Lead roles.
    Only 7 of the 52 engineering postings are non-senior.
  - An always-no prompt would have scored 10/10, so the experiment could not show anything.
  - I chose to add every unused non-senior posting (4) as a disclosed supplement, under the same seed and protocol. My original files were left unchanged (`dbf0ef4`, `04bcea5`, `f9bd958`).
  - I labeled 2 Relevant and 2 Not Relevant.
- **Side issue:** Claude Code first said a `&amp;` I saw was a display bug in its tool. It checked, found the
  tool was fine (it was how the chat showed the output), and said so.
- **Why I decided this way / what I am unsure about:** [Ashwin]

## 2026-10-31: sampling and the prompt experiment

- **What happened:**
  - Sampling: 20 calls, all valid and unanimous. On SE II Test Frameworks, Claude said NOT_RELEVANT 4/4 against my RELEVANT,
    each time because "2+ years" is "above New Grad".
  - I chose the one change: a sentence stating my experience threshold. Dev 11/12 → 12/12; held-out 11/12 → 12/12.
  - The held-out gain is one posting, and it was my worked example.
- **Evidence:** `76bd1ce`, `d932e3b`, `d10abd6`, `914d40d`; `sampling/REPORT.md`, `experiment/REPORT.md`.
- **What I learned:** [Ashwin]

## 2026-10-31: action surfaces

- **What happened:** I pasted the filled prompt into claude.ai and pasted back its reply. Claude Code ran the
  file-read version. Both said RELEVANT and both passed the validator. I chose the watch (`7cde01c`, `a13d3ca`).

## Unresolved / next

- [Ashwin: e.g. no live new posting appeared, so the live judge path on a new posting is untested on real data; one labeler; …]
