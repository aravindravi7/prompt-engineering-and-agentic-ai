# Boundary tests: predictions written before running

> **Predictions written Oct 31, 2026, about 7:10 PM ET, before the permission-policy code existed.** Claude Code derived each prediction from the permission policy in `GATE.md`, which Hemanth accepted at 7:07 PM (commit `92b5c77`). This table was committed on its own before any policy code. The "Observed" column is filled in only after the tests run; a mismatch stays in the table.

All paths are relative to this folder (`js2-loop-tools-diff/`). "Refused" means the policy raises `Refused` **before** any request is sent or any byte is written, and the refusal is logged in the trace.

| # | Case | Kind | Predicted | Observed |
|---|---|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` | host on list | **allowed** | |
| 2 | GET `https://api.ashbyhq.com/posting-api/job-board/notion` | host on list | **allowed** | |
| 3 | GET `https://api.lever.co/v0/postings/palantir` | host off list | **refused** | |
| 4 | GET `http://boards-api.greenhouse.io/...` (not HTTPS) | scheme | **refused** | |
| 5 | GET `https://boards-api.greenhouse.io.evil.example/...` | host suffix trick | **refused** | |
| 6 | POST to `https://api.ashbyhq.com/...` | method | **refused** | |
| 7 | A redirect from an allowed host to `https://evil.example/` | redirect | **refused** before the redirect is followed | |
| 8 | GET a posting's own link, `https://jobs.ashbyhq.com/notion/<id>` | following links in postings | **refused** (not on list) | |
| 9 | Write `runs/<run>/report.md` | write inside `runs/` | **allowed** | |
| 10 | Write `state/seen.json` | write inside `state/` | **allowed** | |
| 11 | Write `runs/../../escape.txt` | `..` escape | **refused** | |
| 12 | Write `runs-evil/x.txt` (a folder beside `runs/`) | prefix trick | **refused** | |
| 13 | Write `runs/link/x.txt`, where `runs/link` is a symlink to a folder outside this one | symlink escape | **refused** | |
| 14 | Write `/tmp/x.txt` (absolute path outside) | absolute path | **refused** | |
| 15 | Read `persona/priya-nair.resume.json` | read inside | **allowed** | |
| 16 | Write `persona/priya-nair.resume.json` | read-only file, write request | **refused** (a read permission is not a write permission) | |
| 17 | Read `../js1-contract-and-watch/CONTRACT.md` | read outside this folder | **refused** | |
| 18 | Reset (delete) a state file **without** `--approve reset-state` | needs approval | **refused** | |
| 19 | Reset a state file **with** `--approve reset-state` | needs approval, given | **allowed**, and the approval is logged | |
| 20 | The same GET twice in one run | repeat rule | the second is **refused and not sent** | |
