# SOURCES.md — what I used, what I wrote, what Claude contributed

## Data

| Source | What it is | How it was obtained |
|---|---|---|
| `https://boards-api.greenhouse.io/v1/boards/reddit/jobs` | Reddit's public Greenhouse job-board listing. No authentication, no credentials, GET only. The only host on the agent's allow-list. | Saved from my own browser on 2026-10-26: 161 postings, 287,309 bytes, sha256 `01220c22df3c…`. `evidence/PROVENANCE.md` says exactly which bytes came from where, why the agent's own fetch path was not the one that retrieved them, and what that does and does not establish. |
| `data/resume.persona.json` | A fictional persona résumé. Invented for this assignment, with an `@example.com` address and a `555` phone number, as the assignment permits. Not a real person, and not based on my own résumé beyond being a new-grad software engineering profile. | Written by me; field *values* chosen by me, JSON formatting by Claude. |

My real résumé, my own contacts, and my application tracking are not in this
repository and were never given to the agent or to Claude. The agent refuses to
load a résumé that is not a validated persona (`CONTRACT.md` R2), and
`.gitignore` excludes `*.real.json`.

## Reading

- The course AI policy and the "Using AI Responsibly in Class" video.
- Chapters 1–3 of the course text, for the record/judgment distinction
  (Chapter 1), the output contract (Chapter 2), and action surfaces and
  autonomy (Chapter 3). The vocabulary in `CONTRACT.md` §2 and in
  `reports/action-surface.md` is from there.
- Greenhouse's public job-board API response shape, read directly off the
  response rather than from documentation.
- Python standard library documentation for `urllib.request` redirect handling.

## Tools

Python 3.13.16 (standard library only — no third-party runtime dependency),
pytest 8.x for tests, git. Claude Opus 5 through Claude Code (Cowork) for the
work described below. No other model, service, or library.

## What Claude contributed, specifically

Claude wrote most of the Python and most of the prose in this folder. Naming it
that plainly is the point of this file; below is the split that actually
happened, and `FRICTIONAL.md` has the timestamps and the commits.

**Mine, and not Claude's:**

- The decision of what layer 1 is for and what it refuses to do.
- `CONTRACT.md` §4 — the rule R-v1: which gates exist, in which order, over
  which four fields, and the decision to drop a scored rule for a gated one so
  that a TA could check it by hand. The sharp edges in §4.2 and the predicted
  failure in §6 are my predictions, written before any run.
- `CONTRACT.md` §5 — the choice of *which* wrong implementations matter. Claude
  then wrote the code for them.
- `experiments/labeling-rule.md` — L-v1, and the decision to keep my label
  separate from the agent's rule so that "the model is wrong" and "my rule is
  wrong" stay distinguishable.
- `experiments/labeling-rule.md` (L-v1), written before any posting was drawn.
- **4 of the 25 hand labels** in `experiments/labels/labels-L-v1.json`:
  postings 8299781, 6512458, 7131934 and 8282760 — the rows L-v1 does not
  settle mechanically. Two things about these that are recorded per row in that
  file and in both reports rather than buried here: the other **21** labels
  were derived mechanically by Claude from L-v1's L1/L2 wording (seniority
  token in the title → no; not an IC software/ML role → no; otherwise yes) and
  I accepted them without changing any, so they are not 21 independent human
  judgements and are not presented as such; and my 4 were **not blind** —
  Claude had already told me what R-v2 returns for each of them, and for
  6512458 also what the model returned, before I labelled them. I disagreed
  with the agent on all four, which is the opposite direction from the
  anchoring risk, but the comparison is not independent and the reports say so.
- The autonomy choice in `reports/action-surface.md`: surface C for the watch,
  no action surface at all for the judging. Claude drafted the table; splitting
  the task in two and giving the halves different authority is the argument I
  wanted to make.
- Every "Not checked" line in the sign-off, and the decision to keep the live
  socket gap in the submission rather than paper over it.

**Claude's, reviewed by me:**

- The implementation in `jobagent/` — module layout, the `urllib` fetch with
  redirects refused, the state file, the field-path resolver, the validator,
  the CLI, the human-readable run summary.
- The test suite, including the code of the wrong versions in
  `tests/wrong_versions.py`.
- First drafts of `CONTRACT.md`, `README.md`, `SOURCES.md`,
  `reports/action-surface.md`, and the report prose.
- The 60 model judgments in `experiments/results/transcript.json` are Claude
  outputs, labelled `judgment` everywhere they appear, with model, timestamp,
  transport, prompt-contract file and raw bytes. Obtained 2026-10-26, one per
  fresh context.
- Pointing out, when I asked what I actually had to do, which 11 of the 25
  worksheet rows contain a seniority token and which 4 are not engineering
  roles. That is Claude counting words against my own written criteria, not
  Claude judging fit, but it is why 21 of the labels are marked `derived`.

**What I accepted, changed, and rejected** is in `FRICTIONAL.md` rather than
summarised here, because the interesting part is the specific cases.

## Responsibility

I am responsible for everything in this folder, including the parts Claude
wrote. If a TA asks why a posting was judged relevant, the answer is in the
`justification` of its entry in `evidence/runs/`, it names the résumé field and
the posting field it rests on, and I can recompute it by hand from
`CONTRACT.md` §4.
