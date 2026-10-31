# Action-surface comparison

The same task on three surfaces: judge posting **7855793003** (Software Engineer II, Test
Frameworks & Tooling, Klaviyo, Boston) for Supriya Sharma, with the `revision-v2` prompt
rules. Draft table by Claude Code from the saved records below; the decision at the end is
Ashwin's.

| | 1. Chat paste | 2. File read | 3. Agent with its own state (the watch) |
|---|---|---|---|
| Where it ran | claude.ai chat, new conversation | `claude -p`, run by `action-surfaces/file_read.py` | `python3 -m jobwatch --judge claude` (runs 1 and 2); judging path exercised in the experiment |
| Who ran it | Ashwin, by hand, 2026-10-31 | Claude Code, 2026-10-31T18:05:00Z | Ashwin ran both live runs; Claude Code ran the experiment calls |
| What Claude could touch | Only the pasted text | The Read tool only, inside a temp folder holding `resume.json` and `posting.json` | Nothing: each Claude call is `--tools ""` from an empty folder. The Python program holds the tools |
| Can read | What Ashwin pastes | Files in its working folder (here, only the two inputs) | Claude: only the prompt. Program: one allow-listed URL, the persona file, its own state |
| Can write | Nothing outside the chat | Nothing (no Write or Bash tool) | Claude: nothing. Program: `runs/<timestamp>/` and `state/seen_ids.json`, state last |
| Can send | Nothing; the chat is its only output | Nothing; no network tool | Claude: nothing. Program: one GET to the allow-listed URL; redirects refused. It never applies, emails or logs in |
| Authority it needs | A claude.ai account; Ashwin's hands | Claude Code on this machine, permission to read one folder | Claude Code on this machine, plus network access for one public endpoint and write access to two folders, given to the Python program, not to Claude |
| Who fetches the posting | Ashwin copies it | Someone must save it to a file first | The program, from one allow-listed URL |
| Who remembers what was already seen | Ashwin | Nobody | `state/seen_ids.json`, updated only after a complete run |
| Can it notice a new posting tomorrow? | No, unless Ashwin checks the board | No | Yes, new-since-last by id (run 2: 156 ids, 0 new) |
| Saved record | Only what Ashwin pastes back | Prompt, inputs, reply, envelope (`2-file-read/`) | Raw response, SHA-256, per-posting rule record and AI judgment, report |
| Validated | Yes, afterwards, by the same validator: VALID | VALID | VALID, every call, before it enters a report |
| Model shown | Not recorded by the chat UI | claude-opus-5-5 | claude-opus-5-5 |
| Turns | 1 | 3 (two file reads, then the answer) | 1 per posting |
| Verdict on 7855793003 | RELEVANT | RELEVANT | RELEVANT (`revision-v2` dev run, 2026-10-31T17:59:57Z) |
| Human work per day | Visit the board, read, paste each posting | Save each posting to a file, run, read | Run one command, read one report |
| What goes wrong if Claude misbehaves | One bad answer in a chat | It could read other files in its folder; here the folder held only the two inputs | A bad answer is rejected or labeled; Claude cannot fetch, write state or act |

All three gave the same verdict with valid evidence, so the surfaces differ in *what else
they can do and record*, not in this answer.

Records: `1-chat-paste/prompt.txt` and `reply.txt` (the reply was pasted back by Ashwin;
the validator was run on it afterwards), `2-file-read/` (prompt, inputs, reply, `record.json`),
`../runs/` and `../experiment/results/revision-v2-dev-2026-10-31T18-00-03Z/`.

## Decision: the least autonomy that suffices

Written by Ashwin Thankachan, 2026-10-31:

I would choose the watch because it can automatically check for new jobs, remember which ones it has already seen, and save the results. Chat paste works for checking one job, but I would have to do everything manually. File read lets Claude access the files, but it still cannot automatically monitor new postings or remember previous results. The watch gives enough automation for this task without giving Claude unnecessary tools or control, since Python handles the workflow and Claude only makes the relevance decision.
