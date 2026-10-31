# Model check, 2026-10-28

Two live calls to Claude made **before any live judgment**. They checked that `claude-sonnet-5-5` is available and how the judge's call setup behaves. Neither call was sent a posting or a résumé. Yash ran both commands himself in Terminal. Claude saved the outputs from his paste, word for word, and wrote this README.

| File | Run from | When (Eastern Time) | Input tokens |
|---|---|---|---:|
| `ping-1-course-folder.json` | the course folder (`Prompt Engineering Course`) | about 10:19 pm, 2026-10-28 (approximate, not recorded) | 730 (4 + 726 cache creation) |
| `ping-2-empty-folder.json` | a new empty temporary folder, the way `judge.py` runs | 10:21 pm, 2026-10-28 (02:21 UTC, 2026-10-29) | 176 |

Input tokens = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens` from each file's `usage` field.

**Commands.** Ping 1:

```bash
claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --no-session-persistence \
  --system-prompt "Reply with the single word OK." --output-format json <<< "ping"
```

Ping 2 was the same command run in a new empty folder:

```bash
cd "$(mktemp -d)" && claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --no-session-persistence --system-prompt "Reply with the single word OK." --output-format json <<< "ping"
```

**What they show.**
- `claude-sonnet-5-5` was available. Both files list it under `modelUsage`, so Claude Code reports which model answered.
- No tools were used: no web search or fetch requests, and no permission denials.
- The CLI output has the fields `judge.py` reads: `result`, `is_error` and `modelUsage`.
- About 554 of ping 1's input tokens depended on the folder it ran in: 730 in the course folder, 176 in an empty folder. `judge.py` always calls Claude from an empty folder.

**What they do not show.**
- What those ~554 folder-dependent tokens contained. Claude Code's memory or settings for the course folder are a likely source, but this was not checked.
- What the remaining tokens contain. The system prompt and the word "ping" are only about 10 tokens, so Claude Code adds roughly 165 tokens of its own even in an empty folder. Their content is not visible here. The way to turn them off is `--bare`, which needs an API key that this project does not use.
- That a judgment call adds exactly the same amount. Only these two pings were measured.
