# Action-surface comparison — Job-Search Agent 1

Run on 2026-10-29 · Tushar Patel

**The task, done three ways:** judge whether posting **8314283** (Software Engineer, South San Francisco, CA) is relevant for the fictional persona Cole Palmer. My hand label is `relevant`.

## Way 1 — Paste the posting into a chat

**What I did:** I opened a new claude.ai chat, outside this Project, so it had no project files or memory. I typed a one-line summary of the persona (0 years, needs H-1B, US only, target titles, skills), pasted the posting text, and asked for relevant / not_relevant / cannot_tell with reasons.

- **Reply (2026-10-29):** `not_relevant`. Saved in `experiments/action-surface/way1-chat-paste-2026-10-29.md`.
- **Claude's reasons:** the posting asks for a Bachelor's plus 2 years of software development, and 2 years in each of seven areas, including Go and Ruby. Cole has 0 years, and neither Go nor Ruby is in his skills.

| | |
|---|---|
| Can read | Only what I pasted |
| Can write | Nothing on my machine. The conversation is stored in my claude.ai account |
| Can send | Nothing onward. The posting text and persona summary go to Anthropic as chat input |
| Authority needed | My claude.ai login |
| What could go wrong | I didn't give it my rule (0–3 years, R1–R6), so it used its own criteria: 2 years required > 0 held. There is no fixed output format and no validator. The verdict can't be recomputed or checked against a record. Every step depends on my copy and paste (I mistyped the save path once) |

## Way 2 — Give Claude a file to read

**What I did:** in Claude Code, inside `js1-contract-and-watch/`, I asked it to read only three files (`experiments/postings/dev/8314283.md`, `persona/cole-palmer.example.json`, `prompts/baseline.txt`), judge exactly as the prompt says, print only the JSON, and not write files, run commands, or read anything else.

- **Reply (2026-10-29):** `cannot_tell`. Saved in `experiments/action-surface/way2-file-read-2026-10-29.md`.
- R1, R3, R5 and R6 pass, and R4 is unknown ("two (2) years" doesn't count under the baseline prompt).
- **The justification has only 5 entries, and R2 is missing.** The posting file has dates, but I gave no run date, so Claude dropped the freshness check without saying so.

| | |
|---|---|
| Can read | Whatever Claude Code's session allows, which is any file in the folder and, through the repo, other students' folders. The "only these three files" limit was **my instruction, not enforced** |
| Can write | Files in the folder, and it can run shell commands, if the session permits. I told it not to |
| Can send | The file contents go to Anthropic as model input |
| Authority needed | A Claude Code session with read, and possibly write and command, permission in the folder |
| What could go wrong | It can quietly leave out a check when its context lacks an input (R2, here). Its scope is limited by a prompt, not by code. A wrong or extra file read would not show up unless I watched the transcript |

## Way 3 — The agent fetches, judges, and writes its own state

**What ran:**
- **Live runs:** `python -m agent` on 2026-10-27 (baseline) and 2026-10-28, plus the seeded re-run of 2026-10-28 (see README, "What ran").
- **8314283 itself:** it was already on the board at the baseline, so the agent loop never reported it as new. The same Claude call and validator judged it through the experiment harness (`experiments/run_prompt.py`, which uses the agent's own `build_request`, `judge` and validator):
  - **baseline prompt:** `cannot_tell` (`experiments/results/baseline-dev-2026-10-29T190534.*`, and 4/4 in sampling);
  - **revised prompt:** `relevant` (`experiments/results/revised-dev-2026-10-29T191746.*`).

| | |
|---|---|
| Can read | The Greenhouse board, the persona's five rule fields, `state/seen_ids.json`, and saved raw files |
| Can write | Only `raw/`, `state/` and `out/` in its own folder |
| Can send | HTTPS GET to `boards-api.greenhouse.io`, and posting text plus rule fields to `api.anthropic.com`. Both hosts are on an allow-list **enforced in code** (`agent/allowlist.py`, tests in `tests/test_allowlist_and_fetch.py`). Contact fields are never sent. It never applies, emails, messages, or logs in |
| Authority needed | Network access to two hosts, an Anthropic API key from the environment, and write access to its own folder |
| What could go wrong | A bad key made all 16 Claude calls fail in run 2 and still updated the state (now fixed: it stops at the first 401, CONTRACT v0.4). The state file can drift from what I've actually reviewed. Posting text is untrusted input sent to Claude; the fixed JSON output and the validator limit what comes back. The allow-list doesn't cover proxy environment variables |

## Comparison

| | Way 1: chat paste | Way 2: file read | Way 3: agent |
|---|---|---|---|
| Verdict on 8314283 | `not_relevant` | `cannot_tell` | `cannot_tell` (baseline) / `relevant` (revised) |
| Uses my rule | No | Yes, from the prompt file | Yes, from the prompt file, plus the code rule judge |
| Output checked | No | No | Yes, by the validator |
| Finds new postings | No | No | Yes (state file) |
| Scope limit | What I paste | My instruction only | Code (allow-list, write paths) |

The three ways gave **three different answers to the same question**, and the differences come from context:
- Way 1 had no rule, so it used its own idea of "new grad".
- Way 2 had the rule but no run date, so it silently skipped R2.
- Way 3 had both, and its answer changed when the prompt changed.

## My choice: the least autonomy that suffices

The job is "tell me, every day, which **new** postings on this board are worth my time, and why." Way 1 and Way 2 can't do that: neither can tell what's new since yesterday, and both depend on me fetching and pasting. So the job needs Way 3's two extra abilities: **fetching** from the board, and **writing its own state**. It needs nothing more. So the agent:

- **reads** from one allow-listed board and **sends** only to the Claude API, both enforced in code;
- **writes** only inside its own folder;
- **never** applies, emails, messages, or logs in;
- **labels** every Claude verdict as model judgment, and the decision to act on any posting stays with me.

For checking a single posting once, Way 1 would suffice. But its answer can't be recomputed, and here it used criteria different from mine.
