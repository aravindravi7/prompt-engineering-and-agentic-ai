# Action-surface comparison

## Summary

The same task (judge one Stripe posting for Maya Sehgal under my contract) done three ways, with what each surface can read, write and send, the authority it needs, and what could go wrong. My choice of the least autonomy that suffices is at the end.

## The three surfaces

| | 1. Paste one posting into a chat | 2. Give Claude a file to read | 3. Agent fetches and writes its own state |
|---|---|---|---|
| How it ran here | [Aravind: did you run this? date, what you pasted] | [Aravind: e.g. `claude -p` with `--tools Read` on one saved posting file, or not run] | `src/watch.mjs`: fetches the board, writes `runs/` and `state/`, calls `claude -p` per new posting |
| Can read | only what I paste | the file(s) the tool is allowed to open | the board response from one allow-listed host; the persona files; its own state |
| Can write | nothing | nothing (read-only tool) | `runs/<id>/` (raw response, reports) and the state file |
| Can send | nothing | nothing | one HTTPS GET to `boards-api.greenhouse.io`; prompts to Claude via the CLI |
| Authority needed | none beyond my chat account | file-read permission on chosen paths | network access, write access to its folder, the CLI's signed-in Claude session |
| Could go wrong | I paste the wrong text or a real résumé, and nothing is tracked between runs | Claude reads a file I didn’t intend, or instructions embedded in posting text steer it | it fetches off the allow-list, sends posting text to Anthropic, or corrupts the state file, then misses or re-reports postings |

In surface 3 the Claude call itself is the narrowest of all: `--tools ""` (no tools) in an empty temporary directory, so the model reads only the prompt and writes nothing; the agent's own code does the fetching and writing.

## My choice

Two surfaces, not one. The watch needs agent-level authority (allow-listed HTTP fetch, writing raw responses and the state file) because the task is defined by state across runs, and the code enforces that boundary, not Claude. The judge gets the least: posting text in, JSON out, with `claude -p --tools ''` in a fresh empty directory, no session persistence. The judge can read only what I hand it and can write or send nothing. I verified the tool-disable after the runs with identical flags (22:56 ET; session init showed `tools: []`, `mcp_servers: []`); the graded runs didn’t log their init messages.
