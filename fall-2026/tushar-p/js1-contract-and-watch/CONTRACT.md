# CONTRACT — Job-Search Agent 1

Version 0.4 · 2026-10-29 · Tushar Patel

Scope: one Greenhouse board, one fictional persona résumé, new postings only, every verdict justified.

## Changelog

- **v0.1 (2026-10-27):** first version, committed before any code.
- **v0.2 (2026-10-27):** revised after Claude Code's plan review (items A–P) and before any code was written. Changes:
  - whole-word matching everywhere (B)
  - R3 rebuilt from the real Stripe location list (C)
  - missing date → unknown (D)
  - R4 uses the largest minimum (E)
  - closed R5 phrase list (F)
  - persona values outside this contract → stop (G)
  - "missing field" defined (H)
  - stronger wrong-version test 2 (I)
  - Claude output format defined (J)
  - state file and raw file rules (K, L)
  - Claude API host added to the allow-list (M)
  - what Claude receives (N)
  - no API key → stop (O)
  - model fallback off (P)
  - a raw file without content can't be a run input (A)
- **v0.3 (2026-10-27):** three gaps found while Claude Code built against v0.2. The code already does this; the contract is updated to match, and the change is documented here rather than written as if known in advance.
  - R2 has no résumé field, so its justification entry uses `resume_field: "none"` (R2 only).
  - Claude also receives the run date and the posting id.
  - The no-content stop applies to live fetches too (after the raw file is saved).
- **v0.4 (2026-10-29):** two changes after run 2 (2026-10-28), where a bad API key made all 16 Claude calls fail with HTTP 401 and the run still updated the state file.
  - An auth failure (HTTP 401) stops the run at the first call, with no output and no state update. Other API errors still mark that posting's Claude verdict invalid.
  - The Claude judge prompt is read from a file (default `prompts/baseline.txt`). Its SHA-256 is recorded in the experiment results.

## In

- **Board:** host `boards-api.greenhouse.io`, board token `stripe`.
  Endpoint: `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`
- **Résumé:** fictional persona Cole Palmer, `persona/cole-palmer.example.json` (invented for this assignment; 555 phone, `@example.com` email).
- **Résumé fields the rule reads** (no others):

  | Rule input | Persona JSON key | Type |
  |---|---|---|
  | target titles | `job_search.target_titles` | non-empty list of strings |
  | skills | `skills` | non-empty list of strings |
  | years of experience | `job_search.years_experience` | integer |
  | work location | `job_search.work_country` | string |
  | needs sponsorship | `job_search.needs_sponsorship` | boolean |

- `personal`, `education` and `experience` are never read by the rule. Contact fields are never printed and never sent to Claude.
- **Missing field:** a required key that is absent, has the wrong type, or is an empty list. The agent stops with an error before any fetch and produces no output.
- **Rule undefined:** this contract is written for `years_experience` = 0, `work_country` = "US", and a boolean `needs_sponsorship`. For any other `years_experience` or `work_country`, the agent stops with "rule undefined for this value". If `needs_sponsorship` is false, R5 passes as not applicable.
- **No API key:** if `ANTHROPIC_API_KEY` is not set and `--no-claude` is not given, the agent stops with an error before fetching.
- **Bad API key:** if the Claude API answers HTTP 401, the run stops at once. It writes no output and does not update the state file.

## Out

For each **new** posting, one record:

- `posting_id`, `title`, `url`, `location`, `date_used` (which date field, and its value)
- `rule_verdict`: `relevant` | `not_relevant` | `cannot_tell` — labeled **record**
- `rule_justification`: one entry per check R1–R6, each with `resume_field`, `posting_field`, `value_found`, and `result` (pass / fail / unknown)
- `claude_verdict`, `claude_justification`, `claude_valid`, `claude_model` (the model named in the response) — labeled **model judgment**

**Claude output format.** The JSON must have exactly these keys:

```
{"posting_id": "<must equal the posting's id>",
 "verdict": "relevant" | "not_relevant" | "cannot_tell",
 "justification": [{"resume_field": "...", "posting_field": "...", "evidence": "..."}]}
```

- `resume_field` must be one of the five persona keys above.
- `posting_field` must be one of `title`, `location.name`, `content`, `first_published`, `updated_at`.
- `justification` must not be empty, and no extra keys are allowed anywhere.
- Anything else is **invalid**. The raw reply is saved, `claude_valid` is false, and `claude_verdict` is null. Invalid output is never repaired.
- A refusal counts as invalid.
- Model fallback is off.

**What Claude receives:**
- the persona's rule fields only;
- the posting id and the run date;
- the posting's title, location, dates, and HTML-stripped content;
- R1–R6 and the verdict logic, in plain language.

Per run: run date, whether the run is live or **seeded**, postings fetched, number new, and the path of the raw response used. Output goes to `out/` as one JSON file and one short Markdown summary.

## State and raw files

- **State file:** `state/seen_ids.json` by default, or a path given with `--state`. It is tracked in git, because it is submission evidence.
  - A **missing** state file means a **baseline run**: every id is recorded and 0 are reported as new.
  - An existing empty list `[]` means every posting is new.
  - Ids are only ever added, never removed. The file is written only after the outputs are written.
- **Raw files:** each live fetch saves the exact response bytes, before parsing, to `raw/greenhouse-stripe-<fetch timestamp>.json`, even if the status is not 200. Raw files are tracked in git.
- **Seeded runs:** `--from-raw <file>` reads a saved response with no network call and labels the run seeded. It saves no new raw file, but it does update the state file it was given.
- **No content:** if any posting in a raw response (live or seeded) has no content, the run stops with an error. For a live fetch, the raw file is saved first.

## Refuses

- Fetching any host not on the allow-list. Allow-list: `boards-api.greenhouse.io` and `api.anthropic.com`. Only `https` is allowed, and every redirect hop is checked again.
- Showing a real résumé on screen or on GitHub. Only the fictional persona is used.
- Presenting Claude's judgment as a fact. Claude verdicts are always labeled model judgment.
- Applying, emailing, messaging, or logging in anywhere.

## The rule

Each check returns **pass**, **fail**, or **unknown**.

- All matching is **whole-word** and case-insensitive, unless a rule says otherwise.
- Matching runs on HTML-stripped posting content, with spaces trimmed from text.

- **R1 Title.**
  - Pass if the title contains one of `job_search.target_titles` ("Software Engineer", "AI Engineer", "Backend Engineer").
  - Fail if it contains none.
  - Fail if it contains any of Senior, Staff, Principal, Lead, Manager, or Intern. Excluded words win over target titles.
  - "Internal" and "Internship" do not match "Intern", and "Software Engineering" does not match "Software Engineer".

- **R2 Freshness.**
  - The posting date is `first_published`, or `updated_at` if that is missing.
  - Dates are compared as calendar dates in America/New_York.
  - 21 days or fewer before the run date → pass. 22 or more → fail. A future date → pass.
  - Both dates missing or unparseable → unknown.

- **R3 Location.** Compared with `job_search.work_country` (US). The list below was built from the real Stripe location values on 2026-10-27.
  - **Pass** if `location.name` contains any one of these, as a whole word. If several locations are listed, one US match is enough.
    - US markers: "United States", "USA", "U.S.", or "US" (uppercase only), including prefixed forms like "US-Remote" and "US-SF-HQ".
    - US cities: San Francisco, South San Francisco, New York, New York City, New-York, Seattle, Chicago, Atlanta.
    - City short forms: SF, NYC, NY, SEA, CHI, ATL, DC.
    - US state names: any of the 50, e.g. Illinois.
    - US state abbreviations, uppercase only and only directly after a comma or semicolon (e.g. ", WA", "; IL"). **"CA" is excluded**, because on this board "Toronto, CA" and "CA-Toronto" mean Canada. San Francisco postings still pass through the city name.
  - **Unknown** if the whole value is only "Remote", or a placeholder: "N/A", "na", "LOCATION", or empty.
  - **Fail** for everything else, for example "Dublin", "London OR Dublin", "Sydney, Australia", "AMER", "CDMX".
  - Note: "OR" and "IN" (as in "IN-Bengaluru") are not read as Oregon or Indiana, because abbreviations count only after a comma or semicolon.

- **R4 Experience.** New grad means 0–3 years (`job_search.years_experience` is 0).
  - Find every "N+ years" and every "N–M years" in the posting text. "N-M" and "N to M" count too. Each match's minimum is N.
  - Take the **largest** of those minimums. 3 or less → pass. More than 3 → fail.
  - No matches → unknown.
  - Plain "N years" without "+" or a range doesn't count, and spelled-out numbers aren't parsed. These are known gaps.

- **R5 Sponsorship.** Applies because `job_search.needs_sponsorship` is true.
  - Fail if the posting text contains any of these phrases: "unable to sponsor", "will not sponsor", "does not sponsor", "no sponsorship", "without sponsorship", "without the need for sponsorship".
  - Otherwise pass. This list is closed, and will be reviewed against real Stripe wording after the first content fetch.

- **R6 Skills.**
  - Pass if at least **1** item in `skills` appears as a whole word in the posting text. "Java" does not match "JavaScript".
  - Fail if none do.

**Verdict:**
1. Any check fails → `not_relevant`.
2. Otherwise, any check unknown → `cannot_tell` (a person decides).
3. Otherwise → `relevant`.

## Wrong versions (tests must catch these)

1. **A justification that cites no fields.** This applies to both judges.
   - A rule justification entry missing any of its four parts is rejected. The one exception: R2's `resume_field` is "none", because R2 compares the posting date with the run date.
   - A Claude justification entry with a missing, empty, or unlisted `resume_field` or `posting_field` is rejected.
2. **An already-seen posting reported as new again.** Test:
   1. Seed the state with a subset of a fixture's ids.
   2. Run once, and expect exactly the remaining ids as new.
   3. Run again on the same input, and expect 0 new.

   The original v0.1 test (two runs, second reports 0) is kept too. It can't catch this bug alone, because run 1 is a baseline that always reports 0.

## What a failure looks like

2026-10-27: The agent fails if it marks as relevant a posting dated more than 21 days before the run, a posting requiring more than 3 years of experience, a posting outside the US, or a posting that says it will not sponsor visas.
