# Action-surface comparison (JS1, Chapter 3) - 2026-10-30

Same task three ways: judge posting 8154295 for Alex under CONTRACT.md §4.

| | Way 1: paste into a chat | Way 2: give Claude a file | Way 3: agent fetches and writes state |
|---|---|---|---|
| What it can read | only the text I paste | only the file I attach | the network, any file it chooses to open |
| What it can write | nothing (I save the reply) | nothing (I save the reply) | files on my disk |
| What it can send | nothing | nothing | network requests |
| Authority it needs | none beyond the chat | file upload | network, shell, file read/write |
| What happened | VERDICT: not_relevant, accepted (claude_outputs/8154295.txt) | VERDICT: | What happened | VERDICT: not_relevant, accepted (claude_outputs/8154295.txt) | VERDICT: not_relevant (way2_reply_8154295.txt) | not_relevant; read files outside its folder; one failed command (actions_log.md) |
 one failed command (actions_log.md) |
| What could go wrong | the paste is the evidence: I can paste the wrong posting, a stale copy, or a silently truncated one, and nothing checks the pasted text against the saved raw response; I also save the reply by hand, so a reply can end up saved against the wrong posting id | I can attach the wrong file or an old snapshot and Claude judges that instead, with no way to tell from the reply; and I still save the reply myself, so the verdict-to-posting pairing is mine to get right | it already left its lane once - read files outside its folder, one command failed; with network, shell and write access it could fetch a URL that is not allow-listed, overwrite state, or pair a verdict with the wrong id, and the damage is on disk before I see it |

## The least autonomy that suffices, and why

Way 2. Judging one posting needs exactly two inputs - the saved posting and the persona - and one output, text. Giving Claude the file gives it precisely that: it cannot fetch, cannot wander into other files, and cannot touch state. It beats Way 1 on the input side, because the file is the saved posting itself, not a paste I could truncate or alter. Way 3's extra authority bought nothing for the judging - the verdict was the same not_relevant - and it cost the incidents in its own row. My agent keeps the same split: Claude judges outside the agent, and the agent only reads saved Claude outputs. Fetching and state need no model at all: the fetch is one fixed allow-listed URL, and the state update is comparing id strings between the response and state.json. Code does both deterministically and I can recompute them; a model would only add nondeterminism, plus authority the task never uses.

## Reconciliation with what I actually did

All 89 judging chats in this project used Way 1, not Way 2. That does not
contradict the choice above, because the choice is about the level of
autonomy, and Ways 1 and 2 are the same level: in both, Claude reads only
what I give it, writes nothing, and sends nothing. They differ only in how
the posting gets in, paste or file. So the experiment did run at the least
autonomy that suffices — by paste instead of by file.

The Way 1 risk I named, a reply judged against the wrong posting, did not
show up in the scored record. The validator checks every POSTING_FIELD
against the posting the reply is saved under, so a reply about a different
posting would usually be rejected; across the 69 baseline-v1 replies, all
6 rejections were the same form failure (a whole candidate list written as
one RESUME_FIELD value), never a citation from the wrong posting. Way 1
did fail me twice in a different way: two clipboard slips saved a command
instead of a reply. Both were caught before any commit (once by the
no-overwrite refusal) and redone in fresh chats. Way 2 remains the cleaner
form of the same level, one less manual step, but nothing in the scored
results depended on the difference.