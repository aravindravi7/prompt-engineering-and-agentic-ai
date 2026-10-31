# Action-surface comparison

The same task three ways: judge posting **7855793003** (Software Engineer II, Test Frameworks &
Tooling, Klaviyo, Boston) for Supriya Sharma. Surfaces 1 and 2 used the `revision-v2` prompt rules.
Claude Code drafted the table from the saved records listed below; the decision at the end is Ashwin's.

**Surface 3 is not a like-for-like run.** The watch's two live runs found **no new posting**, so the watch
never asked Claude about anything. Its column describes what the watch can do, from its code, tests and
two live runs. The only Claude verdict on 7855793003 through the watch's judging code (`judge.judge` and
its validator) comes from the prompt experiment's `revision-v2` dev run, not from a watch run. Also, the
watch's default prompt is **`baseline-v1`** (`jobwatch/watch.py`, `--prompt` default), and with that
prompt Claude said NOT_RELEVANT to this posting in all five calls (sampling and dev).

| | 1. Chat paste | 2. File read | 3. Agent with its own state (the watch) |
|---|---|---|---|
| Where it ran | claude.ai chat, new conversation | `claude -p`, run by `action-surfaces/file_read.py` | `python3 -m jobwatch` (run 1) and `python3 -m jobwatch --judge claude` (run 2) |
| Who ran it | Ashwin, by hand, 2026-10-31 | Claude Code, 2026-10-31T18:05:00Z | Ashwin, both live runs |
| What Claude could touch | Only the pasted text | The Read tool only (`--tools Read`), started in a temp folder holding `resume.json` and `posting.json` | Nothing: each Claude call is `--tools ""` from an empty folder. The Python program holds the access |
| Can read | What Ashwin pastes | Files it can reach with Read (the folder held only the two inputs) | Claude: only the prompt. Program: one allow-listed URL, the persona file, its own state |
| Can write | Nothing outside the chat | Nothing (no Write or Bash tool) | Claude: nothing. Program: `runs/<timestamp>/` and `state/seen_ids.json`, state last |
| Can send | Nothing; the chat is its only output | Nothing; no network tool | Claude: nothing. Program: one GET to the allow-listed URL, with redirects refused. It never applies, emails or logs in |
| Authority it needs | A claude.ai account; Ashwin's hands | Claude Code on this machine, permission to read one folder | Claude Code on this machine, plus network access to one public endpoint and write access to two folders, given to the Python program, not to Claude |
| Who fetches the posting | Ashwin copies it | Someone must save it to a file first | The program, from one allow-listed URL |
| Who remembers what was already seen | Ashwin | Nobody | `state/seen_ids.json`, updated only after a complete run |
| Can it notice a new posting tomorrow? | No, unless Ashwin checks the board | No | Yes, by id. Shown by tests; the live runs saw 156 ids and 0 new |
| Saved record | Only what Ashwin pastes back | The prompt, inputs, reply, and selected envelope fields in `record.json` (model, turn count, permission denials). The full envelope and tool-call trace were **not** saved | Raw response and SHA-256 per run, and per new posting a rule record, AI judgment and report |
| Validated | Yes, afterwards, by the same validator: VALID | VALID | Nothing to validate in the live runs (0 new). When a posting is new, every reply is validated before it enters a report (tests) |
| Model shown | Not recorded by the chat UI | claude-opus-5-5 | — (no call in the live runs) |
| Turns | 1 | 3, as reported by the envelope. Which tool calls they were was not recorded | — |
| Verdict on 7855793003 | RELEVANT | RELEVANT | Not judged by the watch. The same judging code with `revision-v2` in the experiment: RELEVANT (2026-10-31T17:59:57Z) |
| Human work per day | Visit the board, read, paste each posting | Save each posting to a file, run, read | Run one command, read one report |
| What goes wrong if Claude misbehaves | One bad answer in a chat | It could read any file Read can reach; the folder held only the two inputs, and other paths were not tested | A bad answer is rejected or labeled; Claude cannot fetch, write state or act |

Surfaces 1 and 2 gave the same verdict with valid evidence. The comparison is mostly about what each
surface can reach, do and record, which comes from its setup rather than from this one answer.

Records:
- `1-chat-paste/`: `prompt.txt` and `reply.txt`. Ashwin pasted the reply back; the validator was run on it afterwards.
- `2-file-read/`: `prompt.txt`, `inputs/`, `reply.txt` and `record.json`.
- The watch: `../runs/` and `../state/seen_ids.json`.
- The experiment verdict: `../experiment/results/revision-v2-dev-2026-10-31T18-00-03Z/`.

## Decision: the least autonomy that suffices

Written by Ashwin Thankachan, 2026-10-31:

I would choose the watch because it can automatically check for new jobs, remember which ones it has already seen, and save the results. Chat paste works for checking one job, but I would have to do everything manually. File read lets Claude access the files, but it still cannot automatically monitor new postings or remember previous results. The watch gives enough automation for this task without giving Claude unnecessary tools or control, since Python handles the workflow and Claude only makes the relevance decision.
