# Action-surface comparison (Chapter 3), applied to this agent

The task held fixed across all three surfaces: *decide whether one job posting
is relevant to the persona résumé under R-v1, and justify it by naming the
fields.* Only the surface changes.

**Status as of 2026-10-26.** Surface B exists and has run: the `prompt` and
`rule` subcommands read a saved response off disk, and the test suite drives
them. Surface C exists as `watch` and has run against constructed fixtures in
`tests/test_state_and_watch.py`, but **not yet against the real board** —
`evidence/runs/` is still empty, for the reason in `FRICTIONAL.md`. Surface A
is how the model judgments for the sampling report and the prompt experiment
are to be collected — one posting handed to a fresh context with no tools — and
**none have been collected yet**. The comparison below is therefore an analysis
of the three surfaces and the authority each needs, which is what Chapter 3
asks for; it is not a report of 60 completed judgments, and it does not claim
to be.

---

## A — Paste one posting into a chat

| | |
|---|---|
| **Can read** | exactly the text pasted into the turn. Nothing else: no file, no network, no state. |
| **Can write** | nothing. The output is text in a reply. |
| **Can send** | nothing. |
| **Authority needed** | none beyond the person's own session. No host allow-list, no filesystem path, no credential. |
| **What could go wrong** | the human is the loop, so every error is a human error: pasting the wrong posting, pasting a truncated one, pasting yesterday's, mis-reading the reply, or doing it inconsistently across 56 postings. Prompt injection via the pasted text is possible but has nothing to act on. The real failure mode is that it does not scale and so does not get done. |
| **Volume it survives** | one to about five postings per sitting. |

## B — Give the model a file to read

| | |
|---|---|
| **Can read** | whatever file it is pointed at, and in a general-purpose agent, anything else on the filesystem it can reach. |
| **Can write** | nothing, if the surface is read-only. In this repository the `prompt` and `rule` subcommands have no write path at all. |
| **Can send** | nothing. |
| **Authority needed** | read access to a path. That is a real grant: "read this file" and "read this folder" are different sizes, and the second is how a real résumé ends up in a transcript. |
| **What could go wrong** | reading the wrong file, or a file that has moved on since it was saved. A stale snapshot producing a confident answer about a posting that was filled a week ago. Over-broad read scope: pointed at a home directory instead of one file, it can read the real résumé the contract promised to keep off screen. The file's contents are untrusted input, so a posting whose title contains instructions is a prompt-injection vector — in this agent the model is given only `id`, `title`, `location`, `departments`, and it has no tool to act with, which is why that vector is cheap here and would not be in layer 2. |
| **Volume it survives** | the whole board at once, as long as a human triggers each pass. |

## C — The agent fetches and writes its own state file

| | |
|---|---|
| **Can read** | one URL on one allow-listed host (`boards-api.greenhouse.io`), by GET; plus its own config, the persona résumé, and its own state file. |
| **Can write** | `evidence/raw/`, `evidence/state/`, `evidence/runs/`, and nothing else. |
| **Can send** | nothing. There is no POST path to the board, no mail, no message, no form, no login, and no credential in the process for any site. The model judge's POST to `api.anthropic.com` is the one outbound write-shaped call, and it is on its own separate single-host allow-list. |
| **Authority needed** | outbound HTTPS to one host; write access to one directory; optionally one API key. |
| **What could go wrong** | this is the surface where mistakes outlive the run. A corrupt or half-written state file silently redefines "new" — either reporting 56 postings as new, or swallowing them (W3 in CONTRACT.md §5 is exactly this, and `test_state_unchanged_when_reporting_raises` is why the state is written last). A widened allow-list is one string away. A board that changes `id` semantics breaks the only identity the watch has. Repeated fetching is a load on someone else's server, so the watch runs at human cadence, not in a loop. And the agent now holds a verdict that nobody reads at the moment it is produced, which is the failure I take most seriously: an unattended judgment is a judgment nobody checked. |
| **Volume it survives** | the whole board, repeatedly, unattended. |

---

## The choice, and the defence

**Chosen: C for the watch, A for the judging.** Not C for everything.

The task has two halves and they do not need the same authority.

*Noticing what is new* cannot be done at surface A or B. "New since the last
run" is a claim about two points in time, so something has to remember the
first one, and a human pasting postings into a chat is exactly the thing that
will not happen on a Tuesday in November. So the watch gets C — but C narrowed
to the smallest shape that still does the job: one host, GET only, no
credentials, no redirect following, writes confined to one evidence directory,
state written only after the verdicts exist, and the first run reporting
nothing at all rather than everything.

*Judging a posting* needs no action surface whatsoever. Each model judgment in
this layer is one posting and one résumé handed to a fresh context with no
tools, no filesystem, no network, and no memory of any other judgment. It
cannot fetch the wrong posting, because it cannot fetch. It cannot write a
state file, because it has no filesystem. The only thing that can go wrong is
that the answer is wrong — which is why the answer is labelled `judgment`,
validated against a fixed output format, and printed next to a recomputable
record instead of replacing it.

The temptation worth naming is the merge: one process that fetches, judges, and
emits a single verdict, because that is one command instead of two concepts.
That costs the thing this layer exists to preserve — that the autonomous part
cannot judge and the judging part cannot act.

**What would change my mind.** If layer 2 needs job descriptions, surface C
grows: more URLs, more hosts, HTML from a page rather than JSON from an API,
and untrusted free text going into the model's context. At that point the
model's input stops being four short fields that I can eyeball and becomes a
document somebody else wrote, and the injection risk I called cheap above stops
being cheap. The allow-list and the "model gets no tools" rule are what I would
hold on to hardest, in that order.
