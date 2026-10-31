# Action-surface comparison (Chapter 3)

**The same task, done three ways.** Judge one real posting for Priya under `prompts/judgment-v1.md`. The posting is 8546367002, *AI Engineer – Forward Deployed Engineering (AI FDE)*, United States, a development hard case. My label is `not relevant`: the posting says it is "not intended for internship, new graduate, or entry-level applicants."

**What was done by whom.** Claude wrote `make_inputs.py`, `check.py` and the setup and capability parts of this file. Yash ran every live step. The choice at the end is Yash's.

## Who does what

| Step | Who | Live call? | What happens |
|---|---|---|---|
| 0 | code (`make_inputs.py`) | no | Builds the inputs from saved data: the posting and Priya's six résumé fields exactly as the judge shows them, the paste text for (a), and the task for (c). |
| 1 | **you, by hand** | yes, in a Claude chat | (a) Paste one posting into a chat. |
| 2 | **you run the command** | yes, `claude -p` | (b) Claude reads two files in an empty folder. |
| 3 | **you run the command** | yes, `claude -p`, plus fetches to Greenhouse | (c) An agent fetches the board itself and writes its own state file. |
| 4 | code (`check.py`) | no | Puts all three answers through the judge's validator and my pass definition, compares the agent's state file with the watcher's saved ids, and writes `CHECK.md`. |

Run every command from the `js1-contract-and-watch` folder.

### Step 0 (code, offline, already run once)

```bash
python3 action-surface/make_inputs.py
```

### Step 1 (a): paste into a chat, by hand

1. Open a **new** chat in Claude (claude.ai or the Claude app). Write down the model it shows, and whether web search, memory or a project is on.
2. Open `action-surface/a-paste-into-chat.txt`. It holds the v1 prompt, then `---`, then the posting and résumé JSON. Copy all of it, paste it as one message, and send.
3. Create `action-surface/a-chat-reply.txt` and paste Claude's **whole** reply into it, exactly as given.
4. Record the date and time (Eastern) and the model, in FRICTIONAL.md or below.

### Step 2 (b): Claude reads a file

The working folder is a new empty folder holding only the two input files. The only tool is `Read`; there is no write tool and no web tool.

```bash
J="$PWD"; D="$(mktemp -d)"; cp action-surface/inputs/job_posting.json action-surface/inputs/resume.json "$D"/ && cd "$D" && claude -p --model claude-sonnet-5-5 --tools "Read" --strict-mcp-config --no-session-persistence --system-prompt "$(cat "$J/prompts/judgment-v1.md")" --output-format json "Read job_posting.json and resume.json in this folder. They are one job posting and Priya's résumé. Then give your answer." > "$J/action-surface/b-file-read.json"; cd "$J"
```

### Step 3 (c): an agent fetches and writes its own state

The working folder is a new empty folder holding only `resume.json`. Tools: `Read`, `Write` and `WebFetch`.
- **Fetches:** pre-approved only for `boards-api.greenhouse.io`. A fetch anywhere else needs permission that a non-interactive run cannot get, so it should be refused and listed under `permission_denials` in the output.
- **Writes:** auto-accepted only inside the working folder (`acceptEdits`).

The task is in `action-surface/c-task.txt`: fetch the board, write every posting id to `state.json`, fetch the one posting, read the résumé, then answer.

```bash
J="$PWD"; D="$(mktemp -d)"; cp action-surface/inputs/resume.json "$D"/ && cd "$D" && claude -p --model claude-sonnet-5-5 --tools "Read,Write,WebFetch" --permission-mode acceptEdits --allowedTools "WebFetch(domain:boards-api.greenhouse.io)" --strict-mcp-config --no-session-persistence --system-prompt "$(cat "$J/prompts/judgment-v1.md")" --output-format json "$(cat "$J/action-surface/c-task.txt")" > "$J/action-surface/c-agent.json"; ls -la "$D" > "$J/action-surface/c-agent-folder.txt"; cp "$D/state.json" "$J/action-surface/c-agent-state.json" 2>/dev/null || echo "the agent wrote no state.json"; cd "$J"
```

### Step 4 (code, offline)

```bash
python3 action-surface/check.py
```

## What each surface can do

From how each one is set up. "Anthropic" means the text goes to Claude's servers.

| | (a) paste into a chat | (b) Claude reads a file | (c) agent fetches and writes | the agent as built (`watch.py` + `judge.py`) |
|---|---|---|---|---|
| **Can read** | Only what I paste, plus whatever the chat app adds (its own instructions, and memory or past chats if they are on) | Files in its working folder (here, the two inputs). Reading elsewhere needs permission it cannot get. | Its working folder, and any page on `boards-api.greenhouse.io` it decides to fetch | Code reads one board (one host, HTTPS, no redirects) and the persona file. Claude reads only the message it is given: no tools at all. |
| **Can write** | Nothing on my machine. The chat is saved in my Claude account. | Nothing (no write tool) | Any file in its working folder, chosen and filled by the model | Code writes `runs/` and `state/`. Claude writes nothing. |
| **Sends** | The pasted text, to Anthropic | The prompt and the file contents it reads, to Anthropic | The prompt, the files it reads and the pages it fetches, to Anthropic. Its fetch requests go to Greenhouse. | The prompt, one posting and six résumé fields, to Anthropic. Code's one request goes to Greenhouse. |
| **Authority it needs** | My logged-in Claude account, and me copying text in and out | Claude Code login, plus read access to one folder | Claude Code login, network access to one host, and write access to one folder. The model decides which actions to take. | Claude Code login. Code holds the network access and the files. |
| **What could go wrong** | Copy and paste mistakes. App features add context I cannot see. Nothing checks the format unless I run `check.py`. No record unless I save one. A real résumé pasted by mistake leaves my machine. It does not scale past a few postings. | Run in the wrong folder, it could read other files, such as a real résumé. It might not read a file, or misread one. Text inside a posting could try to instruct it. | The state file holds whatever the model writes: ids could be missing or invented, and nothing checks them. It has no tool that saves the raw response byte for byte, so there is no evidence file. Text inside a posting could try to steer an agent that can write files and fetch pages. Every run can differ. | Claude Code adds about 170 tokens of its own, and reported Haiku on every call. The validator does not read the prose reason. A wrong JUDGMENT can only be a wrong opinion: RECORD and state are unaffected. |

## What happened

All three ran on 2026-10-31. These results come from [`CHECK.md`](CHECK.md) and the saved outputs. Claude wrote this section from those files after Yash ran the steps.

| | (a) paste into a chat | (b) Claude reads a file | (c) agent fetches and writes |
|---|---|---|---|
| Saved output | [`a-chat-reply.txt`](a-chat-reply.txt) (copied by hand) | [`b-file-read.json`](b-file-read.json), written 07:23:59 UTC | [`c-agent.json`](c-agent.json), written 07:26:54 UTC; [`c-agent-state.json`](c-agent-state.json); [`c-agent-folder.txt`](c-agent-folder.txt) |
| Answer under the validator | `not relevant`: **pass** | `not relevant`: **pass** | **invalid: fail.** `posting_id` came back as the string `"8546367002"`, not the number. Its verdict, `not relevant`, would have matched my label. |
| Turns, time, permission denials | by hand | 3 turns, 5.0 s, none | 5 turns, 23.4 s, none |
| Models Claude Code reported | Claude.ai, Sonnet 5.5, web search off, memory off. The response appeared as plain JSON text without code fences. | Sonnet 5.5: 6 input + 2,506 cache-read + 5,166 cache-creation tokens, 537 output. Haiku 4.5: 469 input, 14 output. | Sonnet 5.5: 8 input + 9,903 cache-read + 7,119 cache-creation tokens, 1,921 output. **Haiku 4.5: 35,378 input, 1,059 output.** |
| Reported cost | n/a | $0.029 | $0.099 |
| `matched_terms` | `Databricks`, `Unity Catalog`, `AWS`, `LLM`, `evaluation` | none (the reason names Python, Databricks, MLflow, LangGraph and AWS) | none |
| What it saw | Exactly the judge's view (pasted) | Exactly the judge's view (two files) | Whatever its fetches returned. It cited "Remote - California", which is in the posting's `offices` field, a field the judge does not send. |
| State it kept | none | none | `state.json`, a JSON list of **117** ids |

**The agent's state file.** All 117 ids are real: each appears in the watcher's saved response from 06:18:34 UTC, and none was invented. But that response has **901** ids, so **784 are missing**. The board can change in the hour between the two fetches, but not by 784 postings. A watcher using this state file would report about 784 postings it had already seen as "new" on its next run. Nothing in the agent checked the file it wrote.

**What the records do not show.** Why the agent wrote only 117 ids: Claude Code's run record does not include the pages it fetched. Haiku's 35,378 input tokens appear only in the run that fetched pages, which is consistent with the fetched pages passing through Haiku before the agent saw them. This record does not confirm that.

**Same verdict, different reliability.** All three reached `not relevant`, matching my label. The two surfaces that had no way to act (a and b) followed the format. The most autonomous one broke the format, and it kept a state file that silently lost most of the board.

## Least autonomy that suffices

I would choose the file-reading approach for checking one job posting.

It passed my validator without needing web access or permission to write files. The manual chat also passed, but I had to copy and paste the information myself.

The agent approach had more permissions, but its response failed validation because it returned the posting ID as a string instead of an integer.

The agent also saved only 117 posting IDs, compared with 901 in my watcher's earlier saved response.

For my complete job-search agent, I prefer using Python to fetch postings and manage state while Claude only judges the job content.

This gives me better control over the data and limits what Claude can do.

