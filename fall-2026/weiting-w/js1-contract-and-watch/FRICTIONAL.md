# FRICTIONAL.md — what actually happened

Kept in order, with times. Everything here is past tense because it happened.
Where something is still unresolved it says so and does not say it was fixed.
Commit hashes are from the local history of this folder; the final hash on
Canvas is the one from the course repo after the push.

Toolchain: Python 3.13.16, pytest 8.x, git. Claude Opus 5 via Claude Code
(Cowork), session 2026-10-21.

---

## 2026-10-21 ~19:40 ET — the contract first, and it was not theatre

I wrote `CONTRACT.md` before any `jobagent/` file existed, and committed it on
its own (`9280d05`, "freeze CONTRACT.md before any implementation code") so the
ordering is checkable rather than asserted. `git show --stat 9280d05` lists
`CONTRACT.md` and `.gitignore` and nothing else.

Writing it first changed the design twice, before any code existed to change:

1. **The rule shrank.** My first draft of §4 had a scoring rule — points for
   skill keywords found in the job description, a threshold, tie-breaks. Trying
   to write §4.1, the worked-examples table a TA can check by hand, I could not
   produce a row I was confident about without re-running my own arithmetic.
   A rule I cannot evaluate by hand is a rule I cannot check the agent against,
   so I replaced it with four ordered boolean gates over four listing fields.
   That is a worse recommender and a far better layer 1.
2. **Writing §5 told me what my tests had to be.** I had assumed a test that
   compared verdict counts would be a reasonable check. Writing W1
   (labels paired with the wrong postings) made it obvious that W1 produces
   *identical counts* and identical verdict multisets — it is only wrong about
   which job each sentence is about. That is now an explicit test,
   `test_W1_verdict_counts_are_identical_so_counts_cannot_catch_it`, which
   exists to record why the easy test would have passed a broken agent.

## 2026-10-21 ~19:47 ET — the fetch does not work from where I was building

The agent is supposed to fetch `https://boards-api.greenhouse.io/v1/boards/reddit/jobs`.
From the cloud sandbox I was building in, it does not: the egress proxy answers
`403` to `CONNECT boards-api.greenhouse.io:443` — a policy denial, logged by
the proxy as `connect_rejected / gateway answered 403 to CONNECT`. The same
denial came back for `api.lever.co`, `api.ashbyhq.com`,
`api.smartrecruiters.com`, and `example.com`. `api.github.com` answered 200, so
the network itself was up; the host was simply not allowed.

What I tried, in order, and what happened:

| Attempt | Result |
|---|---|
| `curl` to the board, six Greenhouse board tokens | `000` / proxy `403` on every one |
| Proxy status endpoint, to find out why | named the denial explicitly, and said not to route around policy denials |
| The desktop app's built-in browser pane | access was granted for the host, then every `navigate` returned "denied or failed" — including to `example.com`, so it was the pane, not the host |
| Claude in Chrome (the browser extension) | "Browser extension is not connected" |
| A web-fetch tool, asking for the response verbatim | it reached the host and reported 56 postings, but refused to reproduce the body verbatim, so it could not produce a raw response I could save as evidence |

**Where that left the evidence — unresolved when this entry was written, resolved later on 2026-10-26 (see the entries below).** I was not
willing to transcribe a response through a summarising tool and then call the
result a saved raw response, and the assignment forbids invented postings, so
neither a paraphrase nor a fabricated board was available to me. When this entry
was written, `evidence/raw/`, `evidence/runs/` and `evidence/state/` were
**empty** and nothing in the folder claimed otherwise. The plan was to save the
JSON from my own browser and replay it through the agent's `--from-raw` path,
with every run report labelling it. That is what happened on 2026-10-26, and
the later entries record it; `evidence/PROVENANCE.md` says which bytes came
from where. What is still true is the part this entry was about: the agent's
own HTTP path has never reached the real host from here.

`tests/test_fetch_transport.py` does exercise the GET, the redirect refusal and
the raw-bytes save against a stub HTTP server on 127.0.0.1, so the transport is
tested; the live socket to `boards-api.greenhouse.io` is not, from here.

## 2026-10-21 ~20:05 ET — two allow-lists, because one would have been a lie

While writing the Claude judge I found a hole in my own contract: §1.2 said the
model judge needs an API key, but R1's allow-list named only the board host, so
the contract did not say which host the model judge may talk to — and the
obvious fix, adding `api.anthropic.com` to `ALLOWED_HOSTS`, would have let the
board fetcher talk to the model host and vice versa. I gave the model judge its
own separate single-host allow-list and recorded it as amendment A1 in
CONTRACT.md §7, marked non-behavioural. Found by writing code against the
contract, not by running anything.

## 2026-10-21 ~20:10 ET — the tests passed first time, which I did not trust

All 64 tests passed on the first run (65 after the fix below). On a suite I had just written against
code I had just written, that is weak evidence, so I checked that the tests can
fail: the contract tests are run against `tests/wrong_versions.py` and are
asserted to fail there. If the W1 and W2 assertions ever start passing on the
wrong versions, that is a broken test suite and the tests say so.

Still unresolved: `test_fetch_transport.py` widens the allow-list by monkeypatch
so it can open a socket to localhost. That means it proves the transport and
not the policy, and I split it into its own file with that written at the top
rather than leaving one file that appears to prove both.

## 2026-10-21 ~20:30 ET — a run report overwrote another one

Running the CLI twice in quick succession, both run reports were named from a
whole-second UTC timestamp, so the second overwrote the first and the baseline
report was gone — the exact evidence `evidence/runs/` exists to hold, destroyed
silently by the thing that was supposed to preserve it. Fixed in `a810f17` with
a non-colliding suffix, and pinned by
`test_two_runs_in_the_same_second_do_not_overwrite_each_other`.

Writing the regression test then exposed a second, smaller thing: my own test
helper picked "the latest report" with `sorted(glob(...))[-1]`, and
`run-...Z-2.json` sorts *before* `run-...Z.json` because `-` is below `.` in
ASCII, so the helper silently read the wrong report and the test failed for a
reason that had nothing to do with the bug. The helper now diffs the directory
before and after the call and asserts exactly one new file. A test that fails
for the wrong reason is only one edit away from a test that passes for the
wrong reason.

## 2026-10-26 — I caught myself writing the report before running it

Reviewing this folder before touching it again, I found that three files I had
written on 2026-10-21 described, in the past tense, work that had not happened:

- `FRICTIONAL.md` said I had saved the board JSON and that "the two runs in
  `evidence/runs/` are replays of files on disk". `evidence/runs/` was empty.
  It also referred to `evidence/PROVENANCE.md`, a file that did not exist.
- `SOURCES.md` credited me with "every one of the 20 hand labels in
  `experiments/labels/`" and Claude with "the 60 model judgments in
  `experiments/results/`". Both directories were empty.
- `reports/action-surface.md` opened with "All three were actually exercised
  while building this layer" and said surface A "was used for the 60 model
  judgments". Surface A had been used for none.

Nothing in the data was invented — there were no postings, no counts and no
model outputs to invent, because none had been collected. What I had done is
worse in a quieter way: I wrote the prose for the submission I intended to make
and put it in past tense, so the folder claimed results it did not have. If it
had been submitted on 2026-10-21 it would have read as fabricated, and the
honesty rule for this assignment is specifically about tense.

The three files are corrected as of 2026-10-26: each forward-looking claim is
either deleted or rewritten as what is planned and still outstanding, and the
empty directories are described as empty. The sign-off's "Not checked" list
carries this, and the fact that the mistake was mine and had to be caught by
re-reading rather than by any test is the honest version of how it was found.

## 2026-10-26 — the contract met the real response and lost

The saved response has **no `departments` key on any of its 161 postings**.
R-v1's G3 judged on `departments[].name`, so every posting failed G3 on a
missing field and the watch could not have reported a single relevant posting.
Not because nothing matched — because I had written a gate against a field I
had never seen in a real response, taken from how Greenhouse boards are usually
described.

What the response does carry is better: a `metadata` array with a `Job Family`
entry (`Software Engineering`, `Machine Learning`, `Data Science`, …) on all
161, and a `Management Level` entry (`IC3`…`IC7`, `M2`, `D1`). I amended the
contract to **R-v2** — G3 now reads `Job Family`, G1/G2/G4 untouched character
for character — committed the amendment *before* touching the code, and bumped
the rule version because verdicts change. Amendment A2 in CONTRACT.md §7.

Two things I deliberately did **not** fix in the same bump, because one change
per version is the only way the prompt experiment reads one variable:

- the G4 remote false positive I pre-registered on 2026-10-21. The real board
  has 24 non-US remote postings (`Remote - Ontario, Canada`,
  `Remote - United Kingdom`, `Remote - The Netherlands`, `Remote - Ireland`,
  `Remote - Germany`, `Remote - British Columbia, Canada`) and R-v2 admits all
  of them. The prediction was right and I left the defect standing.
- G1 reading title words for seniority while the board states `Management
  Level` outright. A plain-titled IC6 posting passes G1. Pinned as behaviour in
  `test_seniority_is_judged_from_the_title_not_management_level`.

Also noticed, and not acted on: `updated_at` has only 26 distinct values across
161 postings — most of the board was touched the same morning — which is a
concrete reason the contract was right to make `id` the only identity.

## 2026-10-26 — the sampling result was the opposite of reassuring

Zero variance: 5 postings × 4 fresh contexts, 20/20 the same verdict and the
same gate, 20/20 agreeing with the recomputable rule, 20/20 passing the
validator. For about ten minutes I read that as the agent working.

It is not. On my own labels the model is right 12 times out of 20 on that set,
and the two postings it is wrong about are the two I most wanted it to get
right: a Remote-US ML engineering role rejected 4/4 at `confidence: high`
because one metadata field is `null`, and a Canada-only remote role accepted
4/4 at `confidence: high`. Four identical high-confidence answers told me the
pipeline is deterministic and nothing whatsoever about whether it is right.
That sentence is in Chapter 1; seeing my own numbers say it is different.

## 2026-10-26 — the prompt revision did nothing, and I am reporting that

One change (evaluate gates in order, report the first failure). Result:
identical on every metric, on development and on held-out. The baseline was
already at 10/10 on gate fidelity, so the experiment had no room to show a
difference — I chose a change aimed at something that was not broken. The thing
that *was* broken is in the rule, and no prompt edit reaches it.

The one validator rejection in all 40 is the same posting under both prompts.
`Principal Data Scientist, Ads` made the model emit a JSON object, then prose
("Wait — correcting the index…"), then a second object. Under the baseline the
first answer was right and the self-correction made it wrong
(`title_block[3]` → `[4]`); under the revision the first was wrong and the
correction landed right. The validator rejected both, for the right reason
(not one JSON object) — but it would **not** have caught the wrong index in a
single clean object, because `title_block[4]` resolves and the evidence
`"Principal"` does occur in the title. My validator checks that a citation is
well-formed, not that it is about anything. That is the most useful thing I
learned this week and it is in the sign-off under "Not checked".

## 2026-10-26 — I contaminated my own hand labels

When I asked Claude what I actually had to do, its explanation of the four
judgement rows included what the agent had already decided about them — "the
agent fails it at G3", "the model said relevant 4/4". I then labelled those
four rows. So the four labels that carry both reports' disagreements were made
with the agent's verdict in view.

I disagreed with the agent on all four, which is the opposite of what anchoring
would produce, so I do not think the labels are wrong. But they are not blind,
and a held-out agreement number resting partly on non-blind labels is weaker
than the number looks. Recorded per row in
`experiments/labels/labels-L-v1.json`, in both reports, and in the sign-off.
Next layer: labels first, in a file, committed, before any judgment is run —
which is what I thought I was doing, and the ordering slipped because I ran the
60 judgments while waiting for the labels.

Also recorded there: 21 of the 25 labels were derived by Claude applying L-v1's
own wording mechanically to the titles, and I accepted them without changing
any. They are marked `derived`, not `author`, because 21 rows I did not write
out are not 21 human judgements.
## 2026-10-26 — the clean-copy check, and the mistake inside it

I wanted to confirm a TA could run this from a fresh clone, so I copied the
folder somewhere else and ran everything there. The copy command was `rsync`,
which does not exist in this environment, so the copy silently did not happen
and the verification commands — including `rm -f evidence/state/seen.json` and
`rm -f evidence/runs/*.json` — ran against the **deliverable** instead of a
copy. I deleted the committed run reports and the state file.

Nothing was lost, because regenerating them is the point: both runs are replays
of files that are still in `evidence/raw/`, and the re-run produced the same
145/0/0 and 161/145/16 counts against the same two sha256 digests. The reports
in the folder now carry the later timestamp, which is why the README and
`evidence/PROVENANCE.md` name those filenames and say where they came from
rather than quietly presenting them as the originals.

Two things worth keeping from this. First, I redid the check with `cp -a` and
it passed properly: 68 tests from a clean copy with no `.git`, no
`__pycache__`, no `.pytest_cache`; `tools/score.py` reproduced every reported
number there; and `tools/make_seeded_snapshot.py` rebuilt the seeded snapshot
byte-for-byte. Second, both re-run reports landed in the same second, so the
filename-collision bug I fixed on 2026-10-21 was a condition that actually
occurs in ordinary use — the second report is `run-...Z-2.json` and the
baseline was not overwritten.

The lesson I am taking is narrower than "check your copy command": a
verification step that deletes things has to run somewhere it cannot damage the
thing being verified, and mine did not.
## 2026-10-30 — the labels became mine, and I am saying how

Checking the submission against the assignment line by line turned up one thing
that genuinely did not meet it: Step 4b asks me to hand-label 20 real postings,
and only 2 of the 20 were labels I had decided. The other 18 were Claude's
mechanical application of L-v1's own wording to the titles.

So I went through all 20 (all 25, including the sampling set) row by row. They
matched what I would have filled in myself and I changed none, which is
unsurprising — L1 and L2 are mostly word-counting once the rule is written
down, and that is the point of writing the rule down. They are my labels now,
and `labels-L-v1.json` marks each row `author_first` or
`derived_then_confirmed` so nobody has to take my word for which was which.

What this does not fix: I confirmed them on 2026-10-30, after I had seen the
aggregate results of all 60 judgments. That is a second, separate way the
labels are not blind, on top of the four author rows being decided with the
agent's verdict already disclosed to me. Both are now written into both reports
and the sign-off. The ordering that would have avoided all of this is dull and
cost nothing: labels in a committed file before the first judgment runs. I ran
60 judgments while waiting for labels, which is exactly backwards.

## 2026-10-30 — the live fetch, on my own machine

Ran the three README commands on my MacBook (Python 3.14 from python.org,
pytest 9.2.0). `python3 -m pytest -q` gave **68 passed** — so the suite is not
tied to the 3.13 I had been building against, which is the first time anything
here has been checked on a second Python.

`python3 -m jobagent watch` did not reach the board either, but for a different
reason than it does in the cloud sandbox:

```
REFUSED (FetchFailed): could not reach
https://boards-api.greenhouse.io/v1/boards/reddit/jobs:
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
unable to get local issuer certificate (_ssl.c:1081)
```

That is not the allow-list and not the egress policy: python.org's macOS builds
ship with no root certificates and do not read the system keychain, so every
HTTPS call from that interpreter fails until `Install Certificates.command` has
been run. Two things I am keeping from it.

First, the agent's own error text was enough to tell the three failure modes
apart without reading any code: `DisallowedHost` for a host the contract
refuses, `FetchFailed: ... 403 Forbidden` for the sandbox's egress policy, and
`FetchFailed: ... CERTIFICATE_VERIFY_FAILED` for a local trust store. That was
not a design goal — I had written one refusal class and one message format
because the contract said refusals are refusals — and it paid off here.

Second, this is a real portability problem and a TA on a Mac will very likely
hit it, so the fix is now in the README's toolchain section rather than left as
folklore. The agent needed no change.
## 2026-10-31 02:25 UTC — the live fetch finally ran, and the board had moved

`SSL_CERT_FILE=$(python3 -m certifi) python3 -m jobagent watch` on my Mac:

```
[WATCH] https://boards-api.greenhouse.io/v1/boards/reddit/jobs  http=200
  postings=163  already_seen=152  new=11
```

So the agent fetched the real host itself, by GET, through its own allow-list,
and saved the bytes as evidence — `evidence/raw/20261031T022528Z-reddit.json`,
290,888 bytes, sha256 `8871e1bb5de4…`. The largest "Not checked" item in the
sign-off is now a checked item, rewritten rather than deleted so the earlier
state of it is still visible.

Three things came out of this that I did not get from any replay.

**It is a real second calendar day.** Five days separate this capture from the
2026-10-26 one, and the board moved: 11 postings appeared, **9 disappeared**,
152 unchanged. The agent reported exactly the 11. That is the stronger of the
two options the assignment allows, and I now have both it and the seeded run.

**The state file only grows, and I can prove it.** `seen.json` went from 161
ids to 172 — 161 + 11 — not to 163. The 9 withdrawn postings are still in it.
So the agent cannot distinguish "withdrawn" from "never existed", and a posting
removed and re-listed under the same id would never be reported again. Nothing
in the contract said the state should be pruned and nothing in it said it
should not; I noticed this only because the arithmetic did not match my
expectation of 163, and it is now an explicit item in the sign-off rather than
a thing I half-knew. I did not change the behaviour: that would be a new
decision about what "seen" means, and it belongs in a contract amendment, not
in a patch the night before the deadline.

**None of the 11 new postings was relevant.** Five of eleven are "Senior"
something, three are "Staff", two are an "Engineering Manager" listed twice
under two ids, one is an Associate General Counsel. The one I would actually
look at twice is `8287466 Senior Frontend Engineer, Ads Formats` — rejected at
G1 on the word "Senior", which is R-v2 doing exactly what it says and exactly
what I would want a human to overrule. The agent is working. The rule is still
blunt. Both of those are in the sign-off.

Afterwards I re-ran every justification in the live report through the agent's
own citation checker against the live response: 11 of 11 passed, so the
field paths and quoted evidence in a report produced from a live fetch verify
the same way they do from a replay.

One confusion worth recording because it cost me ten minutes: `SSL_CERT_FILE=…`
prefixes a single command. Running `python3 -m jobagent watch` again on the
next line, without it, failed with the same certificate error — which looked
like a regression and was not.
