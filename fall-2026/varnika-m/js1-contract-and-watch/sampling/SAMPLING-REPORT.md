# Sampling report (Chapter 1)

*The tables were drafted by Claude Code on 2026-10-31 from the saved replies in `sampling/`, and recomputed with `python3 -m tools.score sampling`. The conclusions were drafted by Claude Code; Varnika reviewed them: [ ]*

## What ran

- **Postings:** 5 real postings from run 1's saved response. They were chosen by the method fixed in `tools/select_experiment.py` before any labeling: the first 3 development postings from stratum A (listed engineering title, not senior, US) and the first 2 from stratum B.
- **Hand labels:** mine, from `experiment/labels.csv`, committed (`7720143`) before any of these calls.
- **Prompt:** `prompts/baseline-v1.txt`, with the contract's JSON reply format.
- **Calls:** 4 per posting, each a fresh conversation: `claude -p --tools "" --no-session-persistence --setting-sources ""`, run in an empty folder, so no tools, files or memory could be used.
  - Model: `claude-opus-5-5`. A background `claude-haiku-4-5` call also appears in the CLI's usage report.
  - Asked on 2026-10-31, 08:20:32–08:20:49 UTC.
  - All 20 replies passed the validator. Total cost: $0.35.

## Results

| Posting | Hand label | Rule (record) | Claude replies r1–r4 | Same every time? | Agree with hand label |
|---|---|---|---|---|---|
| Software Engineer, Research Tools (4981828008) | NOT_MATCH | NOT_MATCH | N N N N | yes | 4/4 |
| Staff+ Software Engineer, Developer Productivity (5110511008) | NOT_MATCH | NOT_MATCH | N N N N | yes | 4/4 |
| Software Engineer, Business Technology (5400153008) | NOT_MATCH | NOT_MATCH | N N N N | yes | 4/4 |
| Data Engineer, GTM (5418610008) | NOT_MATCH | NOT_MATCH | N N N N | yes | 4/4 |
| Director, Infrastructure Lease Accounting (5441867008) | NOT_MATCH | NOT_MATCH | N N N N | yes | 4/4 |

N = NOT_MATCH. **Spread: none.** All 20 verdicts are the same, and all 20 agree with my hand label.

**Added after seeing those results** (not part of the pre-declared five). All five pre-declared postings turned out to be clear `NOT_MATCH`s, so I asked 4 more times about the only posting I labeled `MATCH`: row 4, "Machine Learning Infrastructure Engineer, Safeguards Research" (5364804008). Those replies are saved separately in `sampling/replies-added-after-results/` (08:22 UTC).

| Posting | Hand label | Rule (record) | Claude replies | Same every time? | Agree with hand label |
|---|---|---|---|---|---|
| ML Infrastructure Engineer, Safeguards Research (5364804008) | **MATCH** | NOT_MATCH | N N N N, plus N in the development baseline run | yes (5/5) | **0/5** |

## What varied, and what did not

- **The verdicts did not vary:** 24 of 24 calls gave the same verdict for their posting.
- **The wording always varied.** All 20 reasons in the main table are different texts. The facts they cite stay consistent: "5+ years" on Research Tools, "6+ years" on Business Technology, and "12+ years" on Lease Accounting, in every repeat.
- **Some reasons cite preferred qualifications.** On the Staff+ posting, all four replies cite "15+ years … and 3+ years as a tech lead". I checked the posting: that text is real, but it is under *"Strong candidates may have"*, a preferred section, which my labeling rule would not count. The verdict is still right on the title alone ("Staff+").
- **Twice, Claude noted that Anthropic makes it.** Two reasons say so: "Anthropic (the company that makes me)" on 5110511008 r1, and "which makes me (Claude), but judging only on the stated criteria" on 5400153008 r2. I saw no effect on the verdicts. It is still a reason to be careful when a model judges its own maker's jobs.

## What I can and cannot conclude

**I can conclude:**

- On these six postings, Claude's verdict under the baseline prompt was **repeatable**: no posting flipped in 4–5 fresh conversations.
- On the five clear cases it agreed with me 20/20.
- On row 4 it was **repeatably different from my label, 0/5.** Five identical answers there make Claude consistent, not right. Its stated reason (Python is in his skills list but in none of his job bullets) is a fair reading of the résumé, so either label is defensible. The repeats show the disagreement is stable; they cannot say who is right.

**I cannot conclude:**

- **That Claude is correct in general.** Repeating a verdict shows repeatability, not correctness, and five of these six postings were easy.
- **That it never flips.** With 0 flips in 4 tries on one posting, a flip rate of up to about 50% per posting is still consistent with what I saw (95% bound: 1 − 0.05^(1/4) ≈ 0.53). Pooling all 24 calls narrows that only if every posting behaves the same, which I have no reason to assume.
- **Anything about other prompts, other models, or a different day.**
