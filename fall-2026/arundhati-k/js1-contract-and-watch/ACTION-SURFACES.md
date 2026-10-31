# Action-surface comparison (Chapter 3)

Same task three ways: judge **posting 8128744** (Software Engineer, New Grad — SF / Seattle / New York) for
Rohan Desai under the CONTRACT §5 rule. My hand label for this posting: **RELEVANT** (Java, JavaScript, Go).

Surfaces 2 and 3 were run on 2026-10-31 (~23:08 UTC) through `claude -p` (Claude Code 2.1.283), no project
settings, no MCP servers. Outputs are saved under [`action-surfaces/`](action-surfaces/). Surface 1: _not yet run
— I run it myself in claude.ai and record the date and reply in `action-surfaces/1-chat-paste/`._

| | 1 · paste into chat | 2 · give Claude a file to read | 3 · agent fetches and writes its own state |
|---|---|---|---|
| how it ran | I pasted the posting text + rule into claude.ai | `--tools Read`; cwd held `posting.md` + `resume_skills.json` | `--tools WebFetch,Read,Write`; WebFetch allowed only for `boards-api.greenhouse.io`; told to fetch `/jobs/8128744` and write `state.json` |
| can **read** | only what I paste | any file the Read tool can reach — not limited to the two I named (nothing in the run stopped it) | the allowed host + local files |
| can **write** | nothing | nothing | files in its working directory (it wrote `state.json`) |
| can **send** | nothing beyond the chat | nothing | HTTP GETs to the allowed host |
| authority it needs | none beyond my account | read access to the folder | network + write access; I pre-approved the tools with `--allowedTools` |
| verdict it gave | _(my run — fill in)_ | NOT RELEVANT ([output](action-surfaces/2-file-read/claude-output.json)) | NOT RELEVANT ([state it wrote](action-surfaces/3-agent-fetch-write/state-written-by-agent.json)) |
| matched my label? | | no | no |
| what went wrong / could go wrong | | quoted real text with correct résumé fields — the format held. Reads beyond the two files were possible. | **it ignored the evidence schema**: `evidence` became free-text sentences, so my validator's checks would reject it; the run used **two models** (`claude-opus-5-5` and `claude-haiku-5-5`) — WebFetch hands the page to a smaller model, so the judge may have seen a summary, not the raw posting; nothing saved the raw response; the state file is whatever the model chose to write; a wrong allow-list entry would let it fetch elsewhere |

Observed facts above come from the saved outputs: turns 3 (file) vs 4 (agent); cost reported $0.063 vs $0.075;
`permission_denials` empty in both runs.

## Which surface my agent uses, and why

_My words — to write._ Questions to answer:
- Which is the least autonomy that still does the job (watch a board every day, remember ids, judge only new ones)?
- What does `run.py` keep in *my* code that surface 3 hands to the model (fetching, the allow-list, raw evidence,
  the state file, the validator)?
- What did surface 3 actually do wrong in this run that my design prevents?
