# Sources and contributions

## What I used

- **The assignment brief:** "Job-Search Agent 1 — The Contract and the Watch", INFO 7375 Fall 2026
  (`assignments/assignment-js1-the-contract-and-the-watch.md` in the course repository, and Canvas).
- **Data:** Klaviyo's public Greenhouse job board,
  `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true`, fetched 2026-10-30 and 2026-10-31.
  No key, no login. Postings are Klaviyo's text, saved unchanged as evidence in `runs/`.
- **Earlier probes (not in the submission):** on 2026-10-29 and 2026-10-30, Claude Code fetched the public
  boards of Datadog, Cloudflare, Stripe, Airbnb, Databricks, Robinhood, Toast, SimpliSafe and CarGurus, to
  count matching postings before I chose a board. Only the Cloudflare snapshot was committed (`snapshots/`).
- **Tools:** Python 3 standard library; Claude Code (CLI and desktop app) with Claude Opus 5.5
  (`claude-opus-5-5`); claude.ai chat for action surface 1; git.
- **Review:** on 2026-10-31 I used Codex to review the drafts. It reran the tests (64 at the time) on Python 3.9.6
  and 3.12.15, checked the saved response hashes and the 0-new / 8-changed-timestamp result, and made five
  findings: a validator crash and four documentation issues, all listed in FRICTIONAL.md. The agent itself
  uses only Claude.
- **Persona:** Supriya Sharma is invented for this assignment, following the brief's rule of `@example.com`
  addresses and 555 phone numbers. No real person's résumé is used.

## What I wrote

- `CONTRACT.md`: all of it. Claude Code applied the edits I asked for (below).
- The choice of board (Klaviyo, after a Datadog draft produced 0 relevant postings) and of the persona's name.
- `experiment/LABELING-PROTOCOL.md`: the seven rules, in my words. Claude Code added only the header.
- All 24 hand labels and their reasons (`experiment/labels.json`, `experiment/supplement-labels.json`).
- The seed 2608, the decision to add the supplement, and the one change for `revision-v2`.
- The decision paragraph in `action-surfaces/COMPARISON.md`.
- The claude.ai chat run (`action-surfaces/1-chat-paste/reply.txt` is the reply I pasted back).
- The experience lines in `FRICTIONAL.md`, and the README's sign-off (How, Not checked, Not claiming; signature withheld) and driver's-seat reasons.

## What Claude Code contributed

Claude Code wrote, at my direction:

- **The edits to my contract** (commit `470fae3`), and nothing else in it:
  1. persona name Aarav Patel → Supriya Sharma, with the data path and email;
  2. "nine fields" → "eight fields", which matches the JSON;
  3. "Claude API request" → wording for the Claude Code CLI (`claude -p`);
  4. validation rule 8 now requires each `posting_quote` to be nonempty.
- **All code and tests:** `jobwatch/`, `wrong_versions/`, `tests/` and `action-surfaces/file_read.py`,
  written against my contract (commits marked "written by Claude Code").
- **`prompts/baseline-v1.md`** (a draft, unchanged since). In `revision-v2.md`, Claude Code wrote the wording of the one sentence whose content I chose.
- **`data/supriya-sharma.resume.json`**, copied from the persona in my contract.
- **Running things:** the sampling and experiment Claude calls, the file-read surface, the final test runs,
  and the board probes before the contract.
- **First drafts** of `README.md`, `sampling/REPORT.md`, `experiment/REPORT.md`, the `COMPARISON.md` table
  and the factual lines of `FRICTIONAL.md`, written from the saved data and commit history. My review is
  not finished, which is why the sign-off is withheld.
- **The fix for the validator crash** Codex found (`c42f2c6`), and the corrections to the comparison and README.
- **Checks it reported to me:** the Datadog rule returning 0 relevant; the labels being all one class; the
  ambiguity of "up to 2 years" in my protocol, which I resolved myself.

Every Claude verdict in this folder is a real `claude -p` (or claude.ai) reply, saved unedited. Test
fixtures and the fake Claude replies inside `tests/` are constructed and are labeled as such in each test file.
