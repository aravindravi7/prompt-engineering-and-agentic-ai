# Action-surface comparison (Chapter 3)

Same task each time: "Is this Klaviyo posting relevant for the persona, and why?"

| | 1. Paste one posting into a chat | 2. Give Claude a file to read | 3. Agent fetches and writes its own state |
|---|---|---|---|
| Can read | Only the text I paste | Only the file I hand it (posting + résumé JSON) | The board API (any posting on the allow-listed host), `state/seen.json`, the persona |
| Can write | Nothing (a chat reply) | Nothing, unless I let it edit files | `runs/*-raw.json`, `runs/*-report.json`, `state/seen.json` |
| Can send | Nothing | Nothing | HTTP GET to `boards-api.greenhouse.io` only |
| Authority it needs | None | Read access to one file | Network access (one host), write access to two folders, the ability to run `claude -p` |
| What could go wrong | I paste the wrong posting; no memory of what is new | It reads a stale file; still no "new since last run" | Fetches a host it shouldn't, corrupts state (re-reports old postings or drops new ones), leaks a real résumé if one were loaded |

**My choice: 3, but fenced.** The assignment's job is "new postings since last run", which needs state and a fetch, so 1 and 2 cannot do it. I give the agent the least autonomy that still does that: one allow-listed host, GET only, writes only inside `runs/` and `state/`, a fictional persona only, and Claude itself has no tools — it only receives text and returns JSON that my validator checks. The agent never applies, messages, or logs in.
