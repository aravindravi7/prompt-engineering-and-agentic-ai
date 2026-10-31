# CONTRACT.md — Job-Search Agent, layer 1 ("the contract and the watch")

Written before any implementation code existed. Nothing in this file describes
behaviour that was discovered by running the agent; where the implementation
later disagreed with this file, the disagreement is recorded in `FRICTIONAL.md`
and this file was amended with the amendment marked.

Author: Weiting W. (INFO 7375, Fall 2026)
Contract frozen: 2026-10-21
Version: 1.0

---

## 0. Scope, in one sentence

Layer 1 watches **one** public job board, notices **only postings it has not
seen before**, and for each new posting returns **two separately labelled
verdicts** — one recomputable record from a written rule, one model judgment —
each carrying a justification that names the résumé field and the posting field
it rests on. It does nothing else.

Deliberate limits of layer 1, stated up front so that nothing later reads as a
discovery: the agent judges a posting from the **board listing fields only**. It
does not open the job description. It does not rank, score, de-duplicate across
boards, track applications, or contact anyone.

---

## 1. In

### 1.1 Inputs

| Input | Form | Source | Required |
|---|---|---|---|
| Board identity | `{"host": "boards-api.greenhouse.io", "board_token": "reddit"}` | `config/board.json`, or `--board-token` on the command line | yes |
| Résumé | one JSON object, schema in §1.3 | `--resume <path>` | yes |
| Seen-state | JSON file of previously seen posting ids | `--state <path>`; absent on first run | no |
| Clock | wall-clock UTC, used only to stamp evidence | the host | yes |

### 1.2 What it needs from the environment

- Outbound HTTPS to exactly one host, `boards-api.greenhouse.io`, GET only.
- A writable directory for evidence (`evidence/raw/`, `evidence/state/`,
  `evidence/runs/`). Nothing else on the filesystem is read or written.
- For the Claude judge only: an `ANTHROPIC_API_KEY` in the environment, **or**
  a pre-recorded transcript file to replay. The rule judge needs neither, and
  the watch runs without the Claude judge if no key and no transcript is given.
- No credentials for the job board. No login. No cookies. No session.

### 1.3 Résumé schema (the only fields the rule may read)

```json
{
  "schema_version": "1.0",
  "persona": true,
  "name": "<fictional name>",
  "email": "<local>@example.com",
  "phone": "+1-555-01XX",
  "title_block":        ["senior", "sr", "staff", ...],
  "target_title_phrases": ["software engineer", ...],
  "target_job_families": ["software engineering", ...],
  "locations_ok":       ["new york", ...],
  "remote_ok": true
}
```

Every string in `title_block`, `target_title_phrases`, `target_job_families`
and `locations_ok` is already lower-case. The rule reads **no other résumé
field**; `name`, `email` and `phone` exist only so that the persona guard
(R2 in §3) has something to check, and they are never printed.

*(`target_job_families` replaced `target_departments` in R-v2; amendment A2.)*

### 1.4 Posting fields the rule may read

From the Greenhouse board listing endpoint
`GET https://boards-api.greenhouse.io/v1/boards/<board_token>/jobs`:

| Field | Use |
|---|---|
| `id` | identity for new-since-last. Nothing else is used as identity. |
| `title` | gates G1, G2 |
| the `metadata` entry whose `name` is `"Job Family"`, by its `value` | gate G3 *(R-v2; see amendment A2)* |
| `location.name` | gate G4 |
| `updated_at` | recorded in the run report; **not** used to judge |
| `first_published` | recorded in the run report; **not** used to judge. Used once outside judging, to construct the seeded earlier snapshot in `evidence/raw/`, which is labelled as seeded wherever it appears. |
| `absolute_url` | printed so a human can open the posting; **not** used to judge |

The `metadata` array also carries a `"Management Level"` entry (`IC3`, `IC5`,
`M2`, …). R-v2 deliberately does **not** read it; see §4.2 item 4.

Any other field in the response is carried into the saved raw evidence and
ignored by the judge.

---

## 2. Out

### 2.1 Per new posting

The object below is an **illustrative shape**, not a real verdict: the id and
title in it are made up to show the fields. Real verdicts live in
`evidence/runs/`.

```json
{
  "posting_id": 1000001,
  "title": "Senior Software Engineer, Ads",
  "absolute_url": "https://job-boards.greenhouse.io/...",
  "updated_at": "2026-10-14T18:22:05-04:00",
  "rule_verdict": {
    "kind": "record",
    "rule_version": "R-v1",
    "verdict": "not_relevant",
    "gate_failed": "G1_title_block",
    "justification": [
      {
        "resume_field": "title_block[0]",
        "resume_value": "senior",
        "posting_field": "title",
        "evidence": "senior software engineer, ads"
      }
    ]
  },
  "claude_verdict": {
    "kind": "judgment",
    "model": "<model id or label>",
    "retrieved_at": "2026-10-21T20:44:03Z",
    "prompt_contract": "experiments/prompts/baseline.txt",
    "validator": "pass",
    "verdict": "not_relevant",
    "gate_failed": "G1_title_block",
    "justification": [ ... same shape ... ],
    "confidence": "high",
    "raw": "<the model's output, byte-for-byte>"
  }
}
```

Required properties of the output, each of which has a test:

- **O1** Exactly one entry per new posting, and `entry.posting_id` equals the
  `id` of the posting that entry describes. No reordering, no zipping, no
  index arithmetic between the posting list and the verdict list.
- **O2** `justification` is non-empty. Every item names a `resume_field` that
  resolves in the résumé JSON actually loaded, and a `posting_field` that
  resolves in *that* posting, and `evidence` is a literal lower-cased substring
  of that posting field's value. A justification that cites nothing, or cites a
  field that is not there, is a contract violation and not a style problem.
- **O3** `rule_verdict.kind == "record"` and `claude_verdict.kind ==
  "judgment"`, always, in every output path. There is no third, merged verdict
  and no single "the answer" field.
- **O4** `gate_failed` is `null` exactly when `verdict == "relevant"`, and
  otherwise names the **first** gate that failed in the order G1 → G2 → G3 → G4.
- **O5** The run report names the raw-response file it was computed from, so any
  verdict can be recomputed from evidence on disk with no network access.

### 2.2 Per run

A run report at `evidence/runs/run-<utc-timestamp>.json` containing: the URL
fetched, HTTP status, the sha256 and path of the saved raw response, the counts
(`postings_in_response`, `already_seen`, `new`), whether the run was a
baseline, the state file path and its sha256 before and after, and the list of
per-posting entries from §2.1. On a baseline run the entries list is empty and
`new` is 0 **by construction, not by coincidence** (R5 in §3).

---

## 3. Refuses

- **R1 — Off-allow-list hosts.** `ALLOWED_HOSTS = {"boards-api.greenhouse.io"}`.
  Any other host raises `DisallowedHost` *before* a socket is opened. Scheme
  must be `https`; method is `GET`; there is no code path that sends a body.
  Redirects are not followed — a redirect is reported as a failed run.
- **R2 — A real résumé.** The agent loads a résumé only if `persona` is `true`,
  `email` ends in `@example.com`, and `phone` matches `+1-555-01\d\d`.
  Otherwise it raises `NonPersonaResume` and exits non-zero. It never prints
  `name`, `email` or `phone`; justifications cite résumé *field paths and the
  matched keyword*, never the whole document. No résumé other than
  `data/resume.persona.json` is in this repository, and `.gitignore` excludes
  `data/resume.real.json` and `*.real.json`.
- **R3 — A model's judgment presented as a fact.** The Claude verdict is
  labelled `judgment`, carries its model label, its retrieval timestamp, the
  prompt-contract file it came from, and its raw bytes. The agent never merges
  the two verdicts, never prints one without the other, and never resolves a
  disagreement on its own: disagreements are listed as disagreements.
- **R4 — Acting on the world.** No apply, no email, no message, no login, no
  form submission, no writing anywhere outside `evidence/`. The agent holds no
  credential for any site.
- **R5 — Reporting anything as new on a first run.** With no state file, every
  posting is recorded as seen and zero are reported. The agent would rather say
  nothing than hand over 56 postings as if they had just appeared.
- **R6 — Judging on a field it did not read.** Layer 1 does not fetch job
  descriptions, so it must not produce a justification that rests on anything
  but the four fields in §1.4.

---

## 4. The rule — predictable by hand

*Current version: **R-v2**. The gates below are R-v2; amendment A2 in §7 records
what changed from R-v1 and why.*

All comparisons are **case-folded substring** tests on lower-cased strings,
except `title_block`, which is a **whole-word** test (so that "sr" does not
match "sre" and "lead" does not match "leadership"). Whole-word means the
token is bounded by a non-letter or by the start/end of the string.

Evaluate the four gates **in order** and stop at the first failure.

- **G1 `title_block`** — if `title` contains, as a whole word, any token in
  `resume.title_block`, the verdict is `not_relevant`.
- **G2 `discipline`** — if `title` contains none of the phrases in
  `resume.target_title_phrases` as a substring, the verdict is `not_relevant`.
- **G3 `job_family`** — let *F* be the `value` of the posting's `metadata`
  entry whose `name` is `"Job Family"`. If *F* is missing, empty, or contains
  none of the phrases in `resume.target_job_families` as a substring, the
  verdict is `not_relevant`.
- **G4 `location`** — if `posting.location.name` contains none of the phrases
  in `resume.locations_ok`, **and** it is not the case that
  (`resume.remote_ok` is true and `location.name` contains `"remote"`), the
  verdict is `not_relevant`.

If all four gates pass, the verdict is `relevant` and `gate_failed` is `null`.

### 4.1 Worked examples a TA can check by hand

**These six rows are CONSTRUCTED EXAMPLES**, written by hand to exercise one
gate each. They are not real postings and no count, report or experiment in
this repository uses them; they exist so the rule can be checked without any
data, and they appear in the test suite as
`tests/conftest.py::CONSTRUCTED`. With the persona résumé in
`data/resume.persona.json`:

| `title` | `Job Family` | `location.name` | verdict | first gate failed |
|---|---|---|---|---|
| `Software Engineer, Ads Formats` | `Software Engineering` | `New York City, NY` | relevant | — |
| `Senior Software Engineer, Ads` | `Software Engineering` | `New York City, NY` | not_relevant | G1 (`senior`) |
| `Client Partner, Retail` | `Client Partner` | `New York City, NY` | not_relevant | G2 (no target phrase) |
| `Software Engineer, Payroll Tax` | `Payroll` | `Remote - United States` | not_relevant | G3 (no target job family) |
| `Software Engineer, Core` | `Software Engineering` | `Dublin, Ireland` | not_relevant | G4 (location) |
| `Site Reliability Engineer` | `Software Engineering` | `Remote - United States` | not_relevant | G2 — "site reliability engineer" is **not** in `target_title_phrases`; see §4.2 |

### 4.2 Known sharp edges of the rule

*Items 1–3 were written for R-v1 on 2026-10-21, before any real data; item 4
was added on 2026-10-26 after seeing the real response, and says so.*

1. `target_title_phrases` is a closed list, so a role the persona would in fact
   want ("Site Reliability Engineer", "Security Engineer") is rejected at G2
   rather than at a judgement about fit. That is a false negative built into the
   rule on purpose: a short closed list is auditable, and layer 1 is optimised
   for being checkable, not for recall.
2. `target_job_families` matching is substring, so `"software engineering"`
   matches `"Specialized Software Engineering"` and `"machine learning"`
   matches `"Specialized Machine Learning"`. In R-v2 I consider that correct
   rather than a leak — the specialised families are the same discipline — but
   it is the same mechanism that made the old `target_departments` gate unsafe,
   and it is written down here rather than relied on quietly.
3. `remote_ok` plus a `"remote"` substring admits `"Remote - Netherlands"`
   unless `locations_ok` is consulted first — the gate as written in G4 **does**
   admit it. This is a known false positive, not a bug to be quietly fixed;
   a later version may narrow it, and the change will be a version bump.
   *(Observed in the real response on 2026-10-26: the board carries
   `Remote - The Netherlands`, `Remote - Ontario, Canada`,
   `Remote - United Kingdom`, `Remote - Ireland`, `Remote - Germany` and
   `Remote - British Columbia, Canada`. R-v2 still admits all of them. Kept, to
   keep the amendment to one change.)*
4. **R-v2 reads the title to judge seniority while the board carries an
   explicit `Management Level` field, and ignores it.** Noted on 2026-10-26,
   after seeing the real response; `Management Level` takes values like `IC3`,
   `IC5`, `IC6`, `M2`, `D1`. A posting at `IC6` with a plain title passes G1.
   I did not change this in R-v2, because A2 is already one change and two
   changes in one bump make the prompt experiment unreadable. It is the first
   thing I would change in R-v3, and it is in the sign-off under
   "Not claiming".

---

## 5. Two plausible-but-wrong implementations the tests must catch

Both are implemented, as real code, in `tests/wrong_versions.py`, and the test
suite asserts that the contract tests **fail** on them and **pass** on the real
one. A test suite that cannot tell the wrong implementation from the right one
is not evidence.

### W1 — `wrong_pairing` (labels paired with the wrong postings)

Plausible because sorting the postings for a tidy report, then zipping the
verdict list back onto the original list by index, is the obvious way to write
it. It produces a report where every individual verdict is correctly *computed*
and attached to the wrong posting. Every count in the run report is right. The
only thing wrong is which job the sentence is about.

Caught by: `tests/test_contract_O1.py::test_verdict_is_attached_to_the_posting_it_quotes`
— for every entry, the `evidence` string in every justification item must be a
literal substring of the named field of the posting whose `id` equals
`entry.posting_id`. Under W1 that substring test fails for every posting whose
sort position moved.

### W2 — `empty_justification` (a justification that cites nothing)

Plausible because the boolean is the part that feels like the answer, and a
justification is easy to leave as `[]`, as a sentence with no field names, or as
a field path copied from the schema rather than from the loaded document. The
verdicts are all correct. The agent simply cannot say why.

Caught by: `tests/test_contract_O2.py` — non-empty justification; every
`resume_field` must resolve by path in the résumé that was actually loaded;
every `posting_field` must resolve in that posting; every `evidence` must be a
lower-cased substring of the resolved posting value. W2 fails the first
assertion; the variant `W2b` (a field path that exists in the schema but not in
the loaded document) fails the second.

### W3 — `eager_state` (extra, not required by the assignment)

Writes the seen-ids state *before* the verdicts are produced, so a crash in the
reporter loses the postings for good: the next run sees them as already seen and
reports nothing new. Caught by `tests/test_contract_state.py::test_state_unchanged_when_reporting_raises`.

---

## 6. What a failure looks like — written 2026-10-21, before anything was run

> On 2026-10-21, before the first run, I expect the agent's first real mistake
> to be a **false positive at G3**: a posting titled "Software Engineer,
> Something" whose department is `"Sales Engineering"` will pass G3 because
> `target_departments` contains `"engineering"` and the match is a substring,
> and it will then pass G4 on a US location and be reported as relevant — a
> verdict I would not act on, produced by a rule that did exactly what it says.
> If I widen `target_departments` to recover recall, this gets worse, not
> better.

Also pre-registered, so that neither can be claimed afterwards as a prediction:
the **false negative** I expect to notice first is G2 rejecting a role the
persona would want because its title phrase is not on the closed list, and the
**disagreement** I expect between the two judges is on `gate_failed` rather
than on `verdict` — the model agreeing on the answer and naming a different
gate for it.

Whether these happened is reported in `FRICTIONAL.md` and in the sign-off, in
past tense, with the run that showed it.

**2026-10-26, after first contact with the real response.** The prediction
above is now **untestable**, and not because it was right or wrong: the
endpoint does not return `departments` at all, so no posting can pass or fail a
departments gate and `"Sales Engineering"` never arises. I am leaving the
prediction where it is rather than deleting it, because the honest finding is
the one underneath it — I wrote a contract against a field I had never seen in
a real response, and predicted a failure mode of a gate that could not run.
What the real data did show is recorded in §4.2 items 3 and 4 and in
`FRICTIONAL.md`, dated, after the fact, and not dressed up as a prediction.

---

## 7. Amendments

Amendments to this contract after the freeze are listed here with a date and a
reason. An amendment that changes a verdict is a rule version bump.

- 2026-10-21 — none at freeze time.
- 2026-10-21, while implementing the Claude judge — **A1, non-behavioural.**
  §1.2 said the Claude judge needs an API key, but R1's allow-list named only
  the board host, so the contract did not say which host the model judge is
  allowed to talk to. Added: the model judge has its own separate single-host
  allow-list, `MODEL_HOSTS = {"api.anthropic.com"}`, in
  `jobagent/claude_judge.py`, enforced by its own check. Two allow-lists, so
  that widening one cannot widen the other. No verdict changes, so R-v1 is not
  bumped. This gap was found by writing the code, not by running it.
- 2026-10-26, on first contact with a real response — **A2, rule version bump
  R-v1 → R-v2.** §1.4 said the listing endpoint returns `departments[].name`
  and G3 judged on it. The real response from
  `https://boards-api.greenhouse.io/v1/boards/reddit/jobs`, saved on
  2026-10-26 (161 postings, sha256 `01220c22df3c…`), contains **no
  `departments` key on any posting**. Under R-v1 all 161 postings therefore
  failed G3 on a missing field, and the watch could not have reported a single
  relevant posting — not because nothing matched, but because the rule was
  written against a field that is not there. I had taken that field from how
  Greenhouse boards are usually described and never checked it against a
  response.

  The fix is one change: G3 now reads the posting's `metadata` entry named
  `"Job Family"` (values such as `Software Engineering`, `Machine Learning`,
  `Data Science`), and the résumé field it compares against is renamed
  `target_departments` → `target_job_families`. G1, G2 and G4 are untouched,
  character for character. Verdicts change, so the rule version is bumped, and
  every run report and transcript records which version produced it.

  What A2 deliberately does **not** change: the G4 remote false positive
  (§4.2 item 3) and the seniority gate reading titles while the board carries
  an explicit `Management Level` field (§4.2 item 4). Both are now known, both
  are left standing in R-v2, and both are named in the sign-off. One change per
  bump, so that the prompt experiment is reading one variable.
