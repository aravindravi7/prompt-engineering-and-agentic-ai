# Job-Search Agent 1 — The Contract and the Watch

**Anisha Gaikar · INFO7375 · Language: Python 3.10+ (standard library only) · Toolchain: python3, Claude Code CLI (`claude -p`), git**

Watches one public Greenhouse board (Klaviyo), reports only postings new since the last run, and judges each one twice: by my written rule (a RECORD) and by Claude under a prompt contract (a JUDGMENT). Contract: [CONTRACT.md](CONTRACT.md).

## Commands (from a fresh clone, inside this folder)
```bash
python3 -m unittest discover -s tests -v                 # tests written from the contract
python3 agent.py run --board klaviyo                     # run 1: baseline (reports none as new)
python3 agent.py run --board klaviyo                     # run 2: later / next day: reports new postings only
# if the board has not changed, a SEEDED second run (clearly labelled):
python3 agent.py seed runs/<run1>-raw.json --drop 3 --out runs/seeded-earlier.json
rm state/seen.json && python3 agent.py run --from-file runs/seeded-earlier.json && python3 agent.py run --from-file runs/<run1>-raw.json
python3 agent.py labels runs/<run1>-raw.json --analytics-only   # 20 postings for hand labels -> labels/labels.csv
python3 agent.py experiment runs/<run1>-raw.json --split dev     # baseline vs revised prompt on 10 dev postings
python3 agent.py experiment runs/<run1>-raw.json --split heldout # only at the end
python3 agent.py sample runs/<run1>-raw.json --n 4               # 5 postings x 4 fresh claude -p calls
```

## What ran
All on 2026-10-31.
- **Tests:** `python3 -m unittest discover -s tests -v` → `Ran 9 tests … OK` (my Mac).
- **Run 1 (live, baseline):** `runs/2026-10-31T173836-live-raw.json` — 156 postings on Klaviyo's board, 0 reported as new (baseline), ids saved in `state/seen.json` (my Mac).
- **Run 2 (SEEDED, clearly constructed):** the board did not change within the evening, so I used the assignment's "saved earlier response" option. `runs/seeded-earlier.json` = run 1's real response minus its 3 highest ids. Baseline on it: `2026-10-31T175858-SEEDED` → 153 postings, 0 new. Replay of the real response: `2026-10-31T175859-from-saved` → **3 new** (Associate Growth Specialist German-Speaker; Lead Product Data Scientist, Agents; Lead Product Data Scientist, Forecasting). Rule and Claude both said `not_relevant` for all three; all three Claude replies passed the validator. State: `state/seen-seeded.json`.
- **Claude calls:** my own Claude Code hit its spend limit (`You've hit your individual spend limit`, exit 1) at ~5:56 pm, so my first experiment run produced 60 empty replies, all correctly rejected as `INVALID`. The real runs (dev, held-out, sampling, and run 2's three judgments) were made with `claude -p` in Claude's workspace at ~6:00 pm on the same code, raw response and labels — see FRICTIONAL.md.

## Files
`agent.py` (fetch, watch, rule judge, Claude judge + validator, reports) · `tests/` (10 tests) · `reports/action-surfaces/` (the real chat and file runs) · `persona/resume.json` (fictional) · `prompts/baseline.txt`, `prompts/revised.txt` (one change: the revised prompt states the three-part rule) · `runs/` raw responses and reports · `state/seen.json` · `labels/labels.csv` (my hand labels) · `label.py` (the helper I labelled with) · `reports/SAMPLING.md`, `reports/EXPERIMENT-dev.md`, `reports/EXPERIMENT-heldout.md` · [ACTION-SURFACES.md](ACTION-SURFACES.md) · [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md)

## Sampling report — conclusion
`reports/SAMPLING.md`: 5 postings × 4 fresh `claude -p` conversations (revised prompt). **Zero variation:** every posting got the same verdict 4/4, and all 20 replies passed the validator. On 4 of 5 that verdict matched my hand label. On the 5th — *Senior CS Compensation Analyst*, the only posting I labelled `relevant` — Claude said `not_relevant` **4 times out of 4**. That is the point of this report: Claude was perfectly repeatable and still disagreed with me, so repeatability is not correctness. I also cannot conclude Claude is "wrong" there: the posting asks for "3–5 years", my rule takes the top of the range (5 > 3) and also says `not_relevant`; I read it as reachable at 3. Four tries per posting also can't show rare flips.

## Prompt experiment — conclusion
One change only: `prompts/revised.txt` adds my three-part rule; nothing else differs. "Pass" = a reply that passes the validator AND matches my hand label.

| set | baseline | revised | written rule |
|---|---|---|---|
| dev (10) | 8/10 (2 INVALID) | 10/10 | 10/10 |
| held-out (10, looked at last) | 5/10 (4 INVALID, 1 wrong) | 9/10 | 9/10 |

What it shows: most of the baseline's failures were **format**, not judgment — 4 replies cited `resume_fields` the contract doesn't allow, and 2 quoted the location line (`"San Francisco, CA"`), which my validator rejects because it only checks the posting's title and body (a strictness in my validator, not an invention by Claude). With the rule stated, every reply was valid. The single held-out miss is the same *Senior CS Compensation Analyst* posting, where the rule itself disagrees with me. What it can't show: 19 of my 20 labels are `not_relevant`, so "always say not_relevant" would score 19/20 — ten cases per split cannot separate a good judge from a lazy one, and one disagreement is one posting, not a rate.

## Sign-off — Job-Search Agent 1
- **Checked:** allow-list refusal, slug refusal, real-looking résumé refused at load time, baseline-then-new-by-id, rule verdicts on 4 contract examples, both wrong versions, validator rejections — by `tests/test_agent.py` (written from CONTRACT.md); runs 1 and 2 by reading `runs/*-report.json` myself.
- **How:** tests drafted with Claude's help from my contract, then I ran them myself; rule verdicts rechecked by hand against my labels on all 20 labelled postings (19 agree; the one disagreement is explained in the sampling conclusion) and on run 2's 3 new postings.
- **Not checked:** (1) whether the years regex reads every way a posting states experience (e.g. "three years", ranges in prose); (2) whether Claude's quotes *support* its verdict (the validator only checks they exist); (3) any board other than Klaviyo, or Greenhouse API changes; (4) whether the rule should read the bottom or the top of a years range ("3–5 years") — my label and the rule disagree on exactly this; (5) a real second calendar-day run: run 2 is seeded.
- **Not claiming:** that the agent finds good jobs; that 20 hand labels make a valid benchmark; that Claude's verdicts are correct.
- **Signed or withheld:** Signed — Anisha Gaikar, 2026-10-31
## Driver's seat
| Part | Claude | Me | Why it stays mine |
|---|---|---|---|
| Contract and rule | Drafted wording | Chose rule, refusals, approved the failure sentence Claude drafted| Only I decide what "worth my time" means |
| Code and tests | Wrote `agent.py` and tests against the contract | Ran tests and both runs myself | I sign what ran, not what was written |
| Hand labels | Copied my labels, unchanged, into its workspace run (my Claude Code hit its spend limit) | Labelled all 20 by reading | Labels are the ground truth; Claude can't grade itself |
| Verdict on a posting | Gives a JUDGMENT | Decides whether to apply | My time, my name |
Evidence of the split: commit `509e6ca` (contract committed before any run); `labels/labels.csv` filled by me one posting at a time with `label.py` (my reasons are in the `my_reason` column, e.g. "director, 10 yrs PM"); my Claude Code spend-limit error and the decision to run the judge calls in Claude's workspace are logged in FRICTIONAL.md.
