# evidence/PROVENANCE.md — which bytes came from where

Nothing in `evidence/` was generated, paraphrased, or filled in by hand. This
file says exactly how each artefact arrived, so a TA can tell a live capture
from a replay from a construction without reading the code.

## The live capture — the agent's own fetch

`raw/20261031T022528Z-reddit.json`

| | |
|---|---|
| URL | `https://boards-api.greenhouse.io/v1/boards/reddit/jobs` |
| Retrieved | 2026-10-31 02:25:28 UTC, **by the agent itself** (`python3 -m jobagent watch`, no `--from-raw`), from the author's Mac |
| HTTP | 200 |
| Size | 290,888 bytes |
| sha256 | `8871e1bb5de49c071f3b661a7d59e5fc879b29c187dd0a90409521aa479b86d5` |
| Contents | `meta.total` = 163, `jobs` = 163 entries, 163 distinct `id` values |
| Report | `runs/run-20261031T022528Z.json`, `raw_response.source = "live"`, 163 in / 152 already seen / **11 new**, none relevant |

This is the only file in `evidence/raw/` that the agent fetched itself, and the
only run report with `source: "live"`. It needed `SSL_CERT_FILE` pointed at
certifi first — python.org's macOS build ships with no root certificates; see
`FRICTIONAL.md`.

It also makes the watch a **second-calendar-day** demonstration rather than only
a seeded one: between the 2026-10-26 capture and this one the board gained 11
postings and lost 9, and the agent reported exactly the 11 new ids. All 11
justifications in the report were afterwards re-checked against this response
with the agent's own citation checker and all 11 passed.

## The 2026-10-26 response

`raw/20261026-reddit-browser-save.json`

| | |
|---|---|
| URL | `https://boards-api.greenhouse.io/v1/boards/reddit/jobs` |
| Retrieved | 2026-10-26, by me, from my own browser (open the URL, Cmd+S) — **not** by the agent |
| Size | 287,309 bytes |
| sha256 | `01220c22df3c14863ea3033f2ad1a8e8224076f81191e809fb8e516ecbdcc865` |
| Contents | `meta.total` = 161, `jobs` = 161 entries, 161 distinct `id` values |
| Integrity checks that passed | parses as JSON; `meta.total` equals `len(jobs)`; every posting has an `id`; ids are unique |

**Why it came from a browser and not from the agent.** The environment this
agent was built in routes outbound HTTPS through an egress proxy that answers
`403` to `CONNECT boards-api.greenhouse.io:443` — a policy denial, not a
network failure (`api.github.com` answered 200 from the same shell). The same
denial applied to Lever, Ashby, SmartRecruiters and `example.com`. Rather than
transcribe a response through a summarising tool and call the result raw, I
saved the bytes from a browser on my own machine and handed the file to the
agent. `FRICTIONAL.md` has the full list of what was tried.

**What this does and does not establish.** The bytes are a genuine, unmodified
response from the live endpoint on 2026-10-26. The agent's own HTTP path —
`jobagent/fetch.py` — was **not** exercised against that host; it is exercised
against a stub HTTP server on 127.0.0.1 in `tests/test_fetch_transport.py`.
This is stated again in the README sign-off under "Not checked".

## The seeded earlier snapshot

`raw/SEEDED-20261026-reddit-earlier-than-2026-10-20.json`

**SEEDED — NOT A LIVE RESPONSE.** Constructed from the file above by
`tools/make_seeded_snapshot.py`, which is committed, so the construction can be
rebuilt byte-for-byte:

```bash
python3 tools/make_seeded_snapshot.py \
  evidence/raw/20261026-reddit-browser-save.json \
  evidence/raw/SEEDED-20261026-reddit-earlier-than-2026-10-20.json \
  2026-10-20
```

| | |
|---|---|
| Rule | kept every posting whose `first_published` is before `2026-10-20` |
| Kept | 145 postings, unmodified, in their original order |
| Removed | 16 postings; their ids are listed in the file's own `seeded` block |
| Edited | nothing. `meta.total` is corrected to 145 and a `seeded` block is added saying what was done. No field of any posting was changed, and no posting was invented. |
| sha256 | `6a9432fe175e461aefb7b68616585e765a501e1061a4348efef2c72eed9e767e` |

`first_published` is used here and **nowhere** in judging; `CONTRACT.md` §1.4
says so.

## The two runs

`runs/run-20261026T223511Z.json` — **run 1, baseline.** Replay of the seeded
snapshot. 145 postings in, 0 already seen, 0 reported as new. No entries, by
construction (`CONTRACT.md` R5), not because nothing matched.

`runs/run-20261026T223511Z-2.json` — **run 2.** Replay of the real response.
161 postings in, 145 already seen, **16 reported as new**, 1 of them
`relevant`. The state file's sha256 before and after is recorded in the report.

Both ran in the same second, which is why the second is suffixed `-2`: the
whole-second filename collision was a real bug found on 2026-10-21, fixed, and
pinned by `test_two_runs_in_the_same_second_do_not_overwrite_each_other`. The
reports in this folder are from a re-run on 2026-10-26 during the clean-copy
verification; same inputs, same sha256s, same counts as the first pair, later
timestamps. See `FRICTIONAL.md`.

Both reports carry `raw_response.source = "replay"` and a `source_label`, so
neither can be mistaken for a live fetch. Each names the raw file and its
sha256, which is what makes `CONTRACT.md` O5 true: any verdict in either report
can be recomputed offline with
`python3 -m jobagent rule --from-raw <that file> --posting-id <id>`.

## The state file

`state/seen.json` — written by the agent, after the verdicts existed, on each
of the two runs. 161 seen ids and `runs: 2` at the end of run 2.

## The model judgments

`../experiments/results/transcript.json` — 60 raw model outputs, stored
byte-for-byte as returned, each with its model label, retrieval timestamp,
transport, and the prompt-contract file it came from.

Obtained on 2026-10-26, each judgment in a **separate fresh context** (a Claude
Code subagent with no shared history), with the rendered prompt passed inline —
nothing was read from disk by the model, and no tool was used by it
(`tool_uses: 0` on every call). Two caveats recorded rather than smoothed over:

- the harness exposes the model as `claude-sonnet` without a pinned build, so
  these are not reproducible to the exact version;
- the harness indents the subagent's reply, and it wraps it in a frame; the
  stored `raw` is that reply with the harness indentation removed and nothing
  else changed. The two multi-object outputs for posting 7330347 are stored
  complete, including the prose between the objects, which is why the validator
  rejects them.

`../experiments/rendered/` holds the exact 60 prompts, rendered by
`jobagent/claude_judge.py` from the two prompt-contract files.
