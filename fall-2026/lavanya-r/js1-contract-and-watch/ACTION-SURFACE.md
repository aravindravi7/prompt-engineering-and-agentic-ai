# Action-surface comparison (Chapter 3)

**Ran:** 2026-10-30, between 21:27 UTC (the last experiment reply) and 21:30 UTC (17:30 ET, commit `e24ec82`). Those files have no per-reply timestamp, so this is the narrowest window the evidence supports.

**Code:** `experiments/action_surface.py`.

**Models:** surfaces 1 and 2 reported only `claude-opus-5-5`. Surface 3 reported **`claude-haiku-5-5` as well as `claude-opus-5-5`** (`models_used` in `3-agent.json`). The extra model is most likely the web-fetch tool summarizing the page before Opus saw it. I could not see the tool calls to confirm that.

**Evidence:** `evidence/action-surface/<surface>.json`. Each file holds the exact command (minus the prompt), the files in the folder before and after, the turn count, permission denials and the verbatim reply.

**Same task three ways:** judge posting 6865698002, "Software Engineer - New Grad (2027 Start)", for Priya under `prompts/revision.md`.

**Hand label:** not fit. Priya graduated in Dec 2025, and the posting wants fall 2026 or spring 2027.

**Note on surface 1:** I ran the "paste into a chat" surface as a tool-free `claude -p` call with the posting pasted into the prompt. That is a stand-in for a chat window, not the claude.ai web app.

## What each surface could do, and what happened

| | 1. Paste the posting into the prompt | 2. Give Claude files to read | 3. Agent fetches and writes its own state |
|---|---|---|---|
| **Can read** | only the text I pasted | any file the `Read` tool can open. `--allowedTools Read` sets no path limit, and I did not test whether it can read outside its folder. It was given `posting.json` and `resume.json` | the web, limited to `boards-api.greenhouse.io` by a permission rule, plus files in its folder |
| **Can write** | nothing | nothing | files in its folder (`Write`) |
| **Can send** | nothing beyond the model call | nothing beyond the model call | HTTP requests to the allowed host |
| **Authority it needed** | none: `--tools ""` | `--tools Read --allowedTools Read` | `--tools WebFetch,Read,Write --allowedTools "WebFetch(domain:boards-api.greenhouse.io)" Read Write` |
| **Turns** | 1 | 3 | 4 |
| **Files after** | none | `posting.json`, `resume.json` (unchanged) | `resume.json`, plus **`state.json` written by Claude**: `{"seen_ids": [6865698002]}` |
| **Verdict inside the reply** | not_relevant (matches hand label) | not_relevant (matches) | not_relevant (matches) |
| **Validator** | INVALID: cited `education.0.end_date` (the same `.0` quirk as in PROMPT-EXPERIMENT.md) | INVALID: same quirk | valid |
| **What went wrong / could go wrong** | Nothing it can touch. The only risk is what I paste: a real résumé pasted here would leave my machine. | It could read any file I put in or near its folder, so a real résumé there would be in reach. It still can't write or fetch. | **Happened:** its reason says the posting "names only one of her listed skills (Python)", but the raw posting names three (Python, Databricks, Unity Catalog), per `rule.judge` on the saved run 2 response. It reached the right verdict partly for a wrong reason, probably because a smaller model (`claude-haiku-5-5`) summarized the page first. It **saved no raw response**, so its claim can't be checked against what it actually saw. **Could:** write a wrong or partial state file, which would silently change what counts as "new" next run. It could also fetch more than asked from the allowed host. |

## The choice: the least autonomy that suffices

**Surface 1, pasted text with no tools, for the Claude step. Everything else stays in my own code.**

- **The judging task doesn't need more.** Claude only needs the posting text and the résumé facts to judge. My code already fetches the board, and it does that safely:
  - the allow-list is checked before any request, and redirects that leave it are refused;
  - the exact response bytes are saved with a sha256 hash.
- **The agent surface failed at something code did correctly.** Its fetch lost part of the posting, and it kept no evidence. That is exactly what the watch must not do, because "new since last run" and every justification depend on the saved raw response.
- **Letting Claude write `state.json` gives a judgment authority over a record.** The state file decides what counts as new. It should be written only by code that tests can check (`tests/test_watch.py`, `tests/test_wrong_versions.py`).
- **Surface 2 adds file access without adding anything the judge uses.** It is the same text, delivered with more reach. Its read access may also reach beyond its folder; I did not test that.

So `agent/claude_judge.py` uses surface 1:

- `--tools ""`, an empty temporary working folder and `--no-session-persistence`;
- the résumé is sent without the `personal` block.

## Limits

- **One posting, one run per surface.** This shows what each surface *can* do and one thing that *did* go wrong. It does not measure how often surface 3's fetch loses text.
- **I did not see the agent's tool calls.** The CLI's JSON summary has no transcript, so "4 turns" and "0 permission denials" are all I know about how it fetched.
