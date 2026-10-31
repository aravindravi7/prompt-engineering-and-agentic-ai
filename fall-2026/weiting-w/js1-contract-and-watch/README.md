# Job-Search Agent 1 — the contract and the watch

INFO 7375, Fall 2026 · Weiting W. · rule version **R-v2**

One board, one persona résumé, new postings only, every verdict justified by
naming the résumé field and the posting field behind it. Two judges, separately
labelled: a recomputable **record** from a written rule, and a **judgment** from
Claude under a prompt contract. The agent never applies, never messages anyone,
never logs in, and fetches exactly one allow-listed host, GET only.

The specification is `CONTRACT.md`, written and committed before any
implementation code existed. Where the code and the contract disagree, the
contract is the specification and the code is the bug.

---

## Language and toolchain

- **Python 3.13.16**, standard library only. `jobagent/` imports nothing
  outside the stdlib — no `requests`, no third-party runtime dependency at all.
- **pytest 8.x**, for tests only (`requirements-dev.txt`).
- git. Nothing else.

```bash
python3 --version          # 3.11+ (standard library only)
python3 -m pip install -r requirements-dev.txt   # pytest, for the test suite only
```

Verified on Python 3.13.16 (Linux) and Python 3.14 (macOS, python.org build) —
68 tests pass on both.

**If the live fetch fails with `CERTIFICATE_VERIFY_FAILED`** (`unable to get
local issuer certificate`), that is a macOS python.org trust-store problem, not
this agent: those builds ship with no root certificates and do not read the
system keychain. The agent's own refusal message distinguishes it from an
allow-list refusal (`FetchFailed: could not reach …` versus
`DisallowedHost: … is not on the allow-list`). Either fix works:

```bash
python3 -m pip install certifi
SSL_CERT_FILE=$(python3 -m certifi) python3 -m jobagent watch   # this run only

/Applications/Python\ 3.x/Install\ Certificates.command        # once, system-wide
```

## Exact commands

Run from this directory (`js1-contract-and-watch/`).

```bash
# 1. The tests, including the ones that must fail on the wrong implementations
python3 -m pytest -q

# 2. The two runs, offline, from the saved evidence in this repo.
#    Delete the state file first to reproduce them from scratch:
rm -f evidence/state/seen.json

#    Run 1 - baseline against the SEEDED earlier snapshot. Reports 0 as new.
python3 -m jobagent watch \
  --from-raw evidence/raw/SEEDED-20261026-reddit-earlier-than-2026-10-20.json \
  --source-label "SEEDED: earlier snapshot built from the 2026-10-26 save, postings first_published before 2026-10-20"

#    Run 2 - the real saved response. Reports exactly the 16 ids that are new.
python3 -m jobagent watch \
  --from-raw evidence/raw/20261026-reddit-browser-save.json \
  --source-label "REAL: browser save of the live response, 2026-10-26"

# 3. A live fetch against the one allow-listed host (needs outbound HTTPS)
python3 -m jobagent watch

# 4. Recompute any verdict in this repo offline, by hand-checkable rule
python3 -m jobagent rule --from-raw evidence/raw/20261026-reddit-browser-save.json --posting-id 8319655

# 5. Print the exact prompt that was sent to the model for one posting
python3 -m jobagent prompt --from-raw evidence/raw/20261026-reddit-browser-save.json --posting-id 6512458

# 6. Rebuild the seeded snapshot, the posting selection, and every report number
python3 tools/make_seeded_snapshot.py \
  evidence/raw/20261026-reddit-browser-save.json \
  evidence/raw/SEEDED-20261026-reddit-earlier-than-2026-10-20.json 2026-10-20
python3 tools/select_experiment_postings.py
python3 tools/score.py
```

`--ask-claude` additionally calls the Anthropic Messages API and needs
`ANTHROPIC_API_KEY`. Nothing in this repository requires it: every model
judgment here is replayed from `experiments/results/transcript.json`.

## What ran

Past tense, with dates, for things that happened on my machine and in this
repository. Everything below is reproducible from the files in this folder with
no network.

- **2026-10-21** — `CONTRACT.md` written and committed on its own, before any
  `jobagent/` file existed (`git show --stat` on that commit lists `CONTRACT.md`
  and `.gitignore` and nothing else). `experiments/labeling-rule.md` (L-v1) and
  `reports/action-surface.md` committed before any label file existed.
- **2026-10-26** — the board response saved from my own browser:
  161 postings, 287,309 bytes, sha256 `01220c22df3c…`, in
  `evidence/raw/20261026-reddit-browser-save.json`. Provenance in
  `evidence/PROVENANCE.md`.
- **2026-10-26** — contract amended to **R-v2** after first contact with that
  response, which contains **no `departments` key** (amendment A2, CONTRACT.md
  §7). Contract amended first, then the code.
- **2026-10-26** — **run 1**, baseline against the seeded earlier snapshot:
  145 postings in, 0 already seen, **0 reported as new**, by construction.
- **2026-10-26** — **run 2**, the real saved response: 161 postings in, 145
  already seen, **16 reported as new**, of which **1 relevant**
  (`8319655 Software Engineer, Ad Signals`, Remote - United States).
  Both run reports in `evidence/runs/`
  (`run-20261026T223511Z.json` and `run-20261026T223511Z-2.json`), each naming
  the raw file and sha256 it was computed from. They are from the clean-copy
  re-run later the same day; the counts and digests are identical to the first
  pair and `FRICTIONAL.md` says why they were regenerated.
- **2026-10-26** — **60 model judgments**, each in its own fresh context with
  the prompt passed inline: 20 for the sampling report (5 postings × 4), 40 for
  the prompt experiment (20 postings × 2 variants). Raw outputs stored verbatim
  in `experiments/results/transcript.json`; all numbers recomputed by
  `tools/score.py`.
- **2026-10-31 02:25 UTC** — **a live fetch, from my own Mac**: `python3 -m
  jobagent watch` with no `--from-raw`, `http=200`, 163 postings in, 152
  already seen, **11 reported as new**, none of them relevant. Raw response
  saved to `evidence/raw/20261031T022528Z-reddit.json` (290,888 bytes, sha256
  `8871e1bb5de4…`), report in `evidence/runs/run-20261031T022528Z.json`
  (`raw_response.source = "live"`). This is also a genuine **second calendar
  day**: the board gained 11 postings and lost 9 between 2026-10-26 and
  2026-10-31, and the agent reported exactly the 11. All 11 justifications in
  that report were re-verified against the live response by the agent's own
  citation checker after the fact.
- **2026-10-26** — **68 tests pass**, from a clean copy of this folder with no `.git`, no `__pycache__` and no `.pytest_cache`, and `tools/score.py` reproduced every reported number there. `tools/make_seeded_snapshot.py` rebuilt the seeded snapshot byte-for-byte (sha256 match), including the assertions that the
  contract tests *fail* on `tests/wrong_versions.py`.

Headline results, with the honest caveats in the reports themselves:

| | |
|---|---|
| Live run, 2026-10-31 | `http=200`, 163 postings, 11 new, 0 relevant. Five days after the 2026-10-26 capture; 9 postings had disappeared from the board in between. |
| Sampling spread | 20/20 identical verdicts and gates; 0 variance. Justification text varied on 2 of 5 postings. |
| Sampling vs my hand label | 12/20 (0.60). Both disagreements are R-v2's own defects, pre-registered on 2026-10-21. |
| Prompt experiment | validator 10/10 development, 9/10 held-out, **identical for both prompts**. Rule fidelity 100% on everything that validated. |
| Held-out agreement with my label | 7/9 for both prompts. Both misses are R-v2 errors the model reproduced faithfully. |

## Layout

```
CONTRACT.md                  the specification, frozen 2026-10-21, amended twice (§7)
SOURCES.md                   what I used, what I wrote, what Claude contributed
FRICTIONAL.md                dated log of what I tried, what broke, what is unresolved
jobagent/                    the agent (stdlib only)
tests/                       68 tests, incl. tests/wrong_versions.py (W1, W2, W2b, W3)
tools/                       seeded-snapshot builder, posting selection, scoring
config/board.json            host + board token; the allow-list lives in jobagent/allowlist.py
data/resume.persona.json     fictional persona, @example.com, 555 phone
evidence/raw/                the saved real response and the SEEDED earlier snapshot
evidence/state/seen.json     the watch's memory: posting ids already seen
evidence/runs/               the two run reports
evidence/PROVENANCE.md       which bytes came from where, and when
experiments/                 prompts, the 25-posting selection, my labels, the 60 raw judgments, scores
reports/                     sampling report, prompt experiment, action-surface comparison
```

## Privacy and boundaries

One host on the allow-list (`boards-api.greenhouse.io`), GET only, no
credentials, no login, redirects refused. The model judge has its own separate
single-host allow-list so widening one cannot widen the other. The agent writes
only under `evidence/`. The résumé in this repository is a fictional persona
and the agent refuses to load one that is not (`CONTRACT.md` R2);
`.gitignore` excludes `*.real.json`. My real résumé, contacts and application
tracking are not here and were never given to the agent.

---

## Sign-off — Job-Search Agent 1

**Checked**

- The rule, by hand, against `CONTRACT.md` §4.1, and by a test per row
  (`tests/test_rule_worked_examples.py::test_contract_table`). I can recompute
  any verdict in `evidence/runs/` from the contract with a pen.
- Verdict/posting pairing and justification integrity, by tests I wrote before
  reading Claude's implementation and ran against deliberately broken versions:
  `test_contract_O1_pairing.py` and `test_contract_O2_justification.py` pass on
  the real code and are asserted to **fail** on `tests/wrong_versions.py`
  (W1 mispaired labels, W2 empty justification, W2b uncited field, W3 eager
  state).
- The allow-list refusal, by test, with no network involved
  (`test_refusals.py`): 8 off-list URLs refused before a socket opens,
  including a look-alike host and an https-upgrade attempt.
- The GET transport — 200 returns raw bytes unchanged, a redirect is refused,
  a 500 is a failed run — against a stub HTTP server on 127.0.0.1
  (`test_fetch_transport.py`). That file widens the allow-list by monkeypatch
  to reach localhost, so it proves the transport and **not** the policy; the
  two are in separate files on purpose.
- The baseline-then-new behaviour, by recomputation: run 1 reported 0 new from
  145 postings, run 2 reported exactly the 16 ids whose `first_published` was
  on or after the cut, and a third run on the same response reported 0.
- Every number in the three reports, by `tools/score.py` recomputing them from
  the stored raw transcript — not by hand, and not typed in.
- The 60 raw model outputs, by re-running all of them through the agent's own
  validator during scoring rather than trusting my reading of them.

**How**: by hand for the rule and the worked-examples table; by tests I wrote
against the contract before reading Claude's code, for O1/O2/O4 and the
refusals; by recomputation for the watch and for every report number; with
Claude's help for the implementation of `jobagent/`, the test code, the wrong
versions, and the first drafts of all the prose here.

**Not checked** — real items, not a formality.

1. **The live fetch has run exactly once, on one machine.** On 2026-10-31 it
   worked from my Mac: `http=200`, 163 postings, 11 new (previously this said
   it had never run, which was true until then). What is still unchecked is
   everything a single successful call does not cover — retries, a rate limit,
   a 5xx from Greenhouse, a partial or truncated body, a changed response
   shape. It also needed `SSL_CERT_FILE` pointed at certifi, because
   python.org's macOS build trusts no root certificates out of the box; the
   cloud environment I built in refuses the host outright (403 on CONNECT), so
   the three earlier runs in `evidence/runs/` are replays and say so.
2. **Whether a justification means anything.** The validator checks that a
   field path resolves and that the quoted evidence occurs in the field named.
   It does not check the pairing. `{"resume_field": "title_block[0]",
   "posting_field": "title", "evidence": "Software Engineer, Ads"}` — `senior`
   paired with a title that does not contain it — passed, repeatedly, in the
   real transcript.
3. **Whether a citation points at the right element of the right list.**
   Posting 7330347's model output cited `title_block[4]` (`"lead"`) for the
   token `Principal`; that citation would have passed the validator had it
   arrived in one clean JSON object.
4. **Anything beyond the four listing fields.** No job description was ever
   fetched or read, so nothing here checks years-of-experience requirements,
   clearance requirements, visa sponsorship, whether a "new grad" role is open
   to new grads, pay, or whether the posting is still live.
5. **None of my 25 hand labels were blind.** Four I decided on 2026-10-26, but
   Claude had already told me what R-v2 returns for each of them (and for one,
   what the model returned). The other 21 were derived mechanically from L-v1's
   wording by Claude and I confirmed them row by row on 2026-10-30 — after I
   had seen the aggregate results of all 60 judgments. They are my labels and
   they match what I would have written, but no agreement number here is an
   independent comparison. `experiments/labels/labels-L-v1.json` records which
   rows are which.
6. **Whether the model is the same model next time.** The harness exposes
   `claude-sonnet` and no pinned build, so these 60 judgments are not
   reproducible to the build.
7. **The board's own semantics.** I am assuming Greenhouse `id` is stable and
   never reused, because the entire watch depends on it, and I have not verified
   it against anything.
8. **The state file only grows.** The live run showed 9 postings had vanished
   from the board since 2026-10-26, and `seen.json` still holds their ids — it
   went from 161 to 172, not to 163. So the agent cannot tell "withdrawn" from
   "never existed", and if a posting were ever removed and re-listed under the
   same id it would not be reported again. I found this on 2026-10-31 and have
   not changed anything about it.

**Not claiming**

- Not that the agent finds good jobs. On its 5-posting sampling set it agreed
  with my own judgement 12 times out of 20, and the two postings it got wrong
  are the two I most wanted it to get right.
- Not that R-v2 is a good rule. It admits every non-US remote posting on this
  board (24 of them), rejects "Analytics Engineer" and "Site Reliability
  Engineer" because they are not on a closed list, and judges seniority from
  title words while the board states `Management Level` explicitly and the rule
  ignores it. All three are written down in CONTRACT.md §4.2, left standing in
  R-v2 on purpose, and would each be their own version bump.
- Not that the prompt revision helped. It changed nothing measurable, on
  development or held-out. The baseline was already at ceiling on the only
  thing that change could affect.
- Not that four identical answers mean a right answer. See the sampling report.
- Not that 10 held-out cases measure anything about the board: 143 of its 161
  postings fail G1, and my sets were stratified by gate, not sampled.

**Signed**: Weiting W. — 2026-10-26

---

## Driver's seat

| For this task | Claude | Me | Why that part stays mine |
|---|---|---|---|
| The contract | drafted the prose of `CONTRACT.md` | decided what layer 1 refuses, and wrote §4 (which gates, in which order, over which fields), §4.2 and §6 | A contract is where I decide what I will stand behind. Claude cannot know which errors I am willing to live with. |
| The rule's shape | offered a scored rule with weighted keywords | threw it out for four ordered booleans, because I could not evaluate the scored version by hand | If a TA cannot predict my verdict by hand, I cannot check the agent against anything. |
| The two wrong versions | wrote the code for W1/W2/W2b/W3 | chose *which* wrong implementations matter, and noticed that W1 produces identical verdict counts so a count-based test proves nothing | Picking the failure modes worth testing is the judgement; typing them up is not. |
| Implementation | wrote `jobagent/`, the tests, the CLI, the scoring | read it, ran the tests against the broken versions, and fixed the run-report overwrite bug it introduced | I am answerable for code I did not write, so I check it against the contract rather than against my impression of it. |
| The 25 hand labels | derived 21 rows mechanically from L-v1's wording | wrote L-v1 before seeing any posting; decided the 4 rows L-v1 does not settle; checked and confirmed the other 21 row by row; disclosed that neither set was blind | The label is the standard the agent is measured against. If Claude sets the standard, Step 4 measures nothing. |
| The autonomy choice | drafted the three-surface table | split the task so the watch gets surface C and the judging gets no action surface at all, and defended it | "How much authority does this thing get" is the question I am responsible for. |
| The sign-off | offered to draft it | wrote every "Not checked" and "Not claiming" line | Claude cannot know what I did not test. |

**Where the split is visible in the record**

- Commit `9280d05` contains `CONTRACT.md` and `.gitignore` and no code: the
  contract existed before the implementation, provably.
- `CONTRACT.md` §7 amendment A2 and the commit before it: the contract was
  amended, and then the code was changed to match — not the other way round.
- `FRICTIONAL.md`, 2026-10-21 entry: Claude's scored rule, and why I replaced
  it with four gates.
- `FRICTIONAL.md`, 2026-10-26 entry "I caught myself writing the report before
  running it": three files in which Claude's draft described work in past tense
  that had not happened, and which I corrected rather than submitted.
- `tests/test_contract_O1_pairing.py::test_W1_verdict_counts_are_identical_so_counts_cannot_catch_it`:
  the test that exists because I did not trust the easy test.
- `experiments/labels/labels-L-v1.json`, the `provenance` block: which labels
  are mine, which Claude derived, and that four were not blind.
