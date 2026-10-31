# Action-surface comparison (Chapter 3) — Job-Search Agent 1

Same task three ways, October 30, 2026: "Is posting 4696752005 (Software Engineer, APIs & Context Platform) relevant for Alex Morgan, and why?" All three said **not_relevant** for the same reason: the posting requires 8+ years; Alex has about 3.

## The three ways

| | 1. Paste into a chat | 2. Give Claude a file to read | 3. Agent fetches and writes its own state |
|---|---|---|---|
| How I ran it | Prompt built by agent/manual_judge.py pasted into a fresh claude.ai incognito chat (runs/prompt_exp/v1/4696752005_a1_*) | Claude Code (desktop) told to read action_surface/posting_4696752005.json and data/persona_alex.json only (action_surface/way2_claude_code_reply.txt) | Claude Code told to fetch the Glean board, save raw.json, write state.json, then judge (action_surface/way3/) |
| Can read | Only the text I paste: permitted résumé fields + cleaned posting. No name/email/phone. | Any file in the project folder (it read only the 2 named files, shown as "Read 2 files"). It saw the whole raw posting and the whole résumé, including name, email, phone. | Anything the shell can reach. It ran `git rev-parse --show-toplevel` and read AGENTS.md at the class-repo root, outside my folder, without being asked. |
| Can write | Nothing | Nothing used (it could have written in the project) | Files: wrote raw.json and state.json, only inside action_surface/way3/ (confirmed by `git status`) |
| Can send | Only what I paste, to claude.ai | File contents to the model | Network requests from the shell: it used `curl` directly, which bypasses my allow-list in agent/net.py |
| Authority needed | None beyond a chat account | Read access to the project | Read, write, shell, network. In my session it did **not** ask permission before using the internet or writing files. |
| Output format | Fixed JSON, checked by validate_reply | Free text; not validated | Free text; its state.json is not my contract's state (no atomic write, no evidence naming) |
| What could go wrong | My own copy-paste errors (3 happened: Entries 17, 21, 22); fixed by validator + logs | Reads private files it wasn't asked to (e.g. labels/, a real résumé if one were in the folder); unvalidated answers | Fetches any host; overwrites or corrupts state; reads beyond the task (observed); acts and retries without asking (one command failed and it retried on its own) |

## My choice: the least autonomy that suffices

The task needs two kinds of work, and they need different autonomy:
- **Fetching, remembering, and detecting new postings** needs network and file writes, but no judgment. My own code does this: one allow-listed host, raw evidence saved, atomic state writes, all covered by tests.
- **Judging one posting** needs judgment, but no network, no files, and no state. Claude gets only the permitted résumé fields and one cleaned posting (Way 1), and its reply must pass the validator.

So Claude never needs Way 3's authority. Way 3 did reach the same verdict here, but it read files outside my folder, used the network without my allow-list, and did both without asking. Same answer, much larger surface. Way 2 sits in between, but it exposes the full résumé, including identity fields my contract keeps out, and its answer can't be validated.

## The cost of my choice
Least autonomy isn't free: in Way 1, I'm the courier. My three copy-paste mistakes came directly from that manual step. The validator caught them, and I logged and redid each one, but an API-based version (as in my original contract) would remove that error source without giving Claude any more authority.

## Not shown
- One posting only, one day, one model.
- Claude Code's permission behavior depends on its settings; I didn't test other settings.
- `git status` only shows writes; I can only see Way 3's reads because the agent listed them itself.