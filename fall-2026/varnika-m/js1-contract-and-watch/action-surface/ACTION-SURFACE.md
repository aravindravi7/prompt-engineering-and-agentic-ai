# Action-surface comparison (Chapter 3)

*Drafted by Claude Code on 2026-10-31 from the saved transcripts of ways 2 and 3 (summaries in this folder; the full transcripts stay on my machine). Way 1 is my own chat. Varnika reviewed the conclusions on 2026-10-31, from Claude Code's summary of them in chat, and agreed; she did not re-derive the numbers herself.*

**The task.** Decide whether posting 5440427008, "Software Engineer, Sandboxing", is a `MATCH` for the Aarav Patel persona, and reply in the contract's JSON format. I did the same task three ways on 2026-10-31, all with the same instructions.

**What my rule says.** The contract's rule gives this posting `MATCH`: the title is on the list, it is not senior, the locations are in the US, there is no years phrase, and two skills (AWS, Kubernetes) appear. So the three ways below are also three chances to see a judgment disagree with the record.

## What each way could do, and what happened

| | Way 1: paste into a chat | Way 2: Claude reads a file | Way 3: an agent fetches and writes its own state |
|---|---|---|---|
| **How it ran** | I pasted `way1-paste-this.txt` into a new chat at claude.ai (Free plan, model shown: **Sonnet 5.5, Medium**), just before 08:41 UTC, and copied the reply with the chat's copy button | `claude -p --tools Read` in an empty temp folder holding `posting.txt` and `resume.json` (contact details removed), 07:46:59 UTC | `claude -p --tools WebFetch,Read,Write --allowedTools "WebFetch(domain:boards-api.greenhouse.io)" Read Write` in an empty temp folder holding `resume.json`, 07:47:07 UTC |
| **Can read** | Only the text I paste | Any file in its folder (here, two) | Any file in its folder, plus web pages on the allowed host |
| **Can write** | Nothing on my machine (the chat is kept in my claude.ai account) | Nothing (no Write tool) | Any file in its folder |
| **Can send** | Nothing beyond the chat | Nothing beyond the conversation | HTTP requests to `boards-api.greenhouse.io` |
| **Authority it needs** | A person with a Claude account, copying text | Permission to read a folder | Network access, write access, and a permission rule that has to be right |
| **What it actually did** | Replied `NOT_MATCH` (`way1-chat-reply.txt`): the posting needs Linux systems or kernel work, a systems language and KVM/Firecracker/gVisor/runc experience, while the résumé shows TypeScript, Python, Java and SQL work, Rust only as "familiar but not shipped", and Kubernetes/Docker tooling. The reply was valid JSON with no extra text, and the contract's validator accepted it when I checked it afterwards. In the chat itself nothing checked the format: I had to copy it out. | Read `posting.txt`, then `resume.json`. Replied `NOT_MATCH`: the role needs Linux kernel or systems work, a systems language (Rust, C, C++, Go) and container-isolation experience, and the résumé lists Rust only as "familiar with, not shipped". Validator: accepted. Cost: $0.057. | Called WebFetch on `…/jobs/5440427008` with a prompt it wrote itself ("Return the job id, title, location, and full requirements…"). The tool returned a **1,721-character Markdown summary**, not the posting's raw JSON. It read `resume.json`, then **wrote `state.json` in a format it invented**: `{"seen": ["5440427008"], "verdicts": {"5440427008": "NOT_MATCH"}}`. Replied `NOT_MATCH`, with the same reasons as way 2. Validator: accepted. Cost: $0.059. |
| **What could go wrong** | Pasting the wrong posting or an old version, or pasting a real résumé by mistake. No record unless I save the reply. Nothing checks the format unless I paste the reply back. | Run in a real folder, it could read any file there, including a real résumé. The prepared file has to be the right posting. | **Seen here:** the verdict rests on a summary another model wrote, and the raw response was not saved, so nobody can check what it read. The state file used its own key (`seen`) and stored the id as text, while the agent's `state/anthropic.state.json` uses `seen_ids` and numbers. A later run that compared them would treat every posting as new, which is my contract's failure sentence. **Possible:** with a broader permission rule it could fetch other hosts, or overwrite files in the folder. Its steps can differ from run to run. |

All three Claude runs disagreed with the rule's `MATCH`, for the same reason, which none of my keyword checks can see: the must-haves are kernel and isolation work that the résumé does not show. One difference between the ways is not about autonomy: way 1 used the model my claude.ai Free plan offers (Sonnet 5.5), while ways 2 and 3 used Opus 5.5 through Claude Code. The verdict was the same anyway.

## The choice: the least autonomy that suffices

**What my agent uses.** Claude gets way 1's surface, automated: `agent/claude_judge.py` sends the posting and résumé as text to `claude -p --tools ""`, in an empty folder. That means no tools, no files and no network. The parts that need authority, fetching and writing the state file, are done by my own Python code:

- it can fetch only from one host (`agent/fetch.py`);
- it saves the raw response before reading it;
- it writes one state format, which the tests check (`tests/test_watch.py`).

**Why not way 2.** Reading files adds nothing here: the code already has the posting text. It would only widen what Claude could see.

**Why not way 3.** The judgment does not need network or write access. In this run, that access made things worse in two ways I can show from the transcript: provenance was lost (a summary instead of the raw posting), and the state file drifted to a different format. Both are the failures my contract is written to prevent.

**What this choice costs.** Someone has to write and test the fetch and state code. A Claude-only agent would have done that in one prompt, but untested, and differently each time.

## Files

- `way1-paste-this.txt`: the exact text pasted in way 1. `way1-chat-reply.txt`: the reply.
- `way2-file/summary.json`: way 2's tools, calls and reply.
- `way3-agent/summary.json`: way 3's tools, calls, the state file it wrote, and its reply.
- The full stream-json transcripts of ways 2 and 3 are **kept on my machine, not committed**. The assignment says conversation transcripts stay on your machine, and these also hold machine details: my macOS username in paths, the installed Claude Code skills, and session ids. Each `summary.json` records its transcript's SHA-256, so I can show a TA the original and prove it is unchanged. `.gitignore` stops them from being committed again.
