# Prompt experiment (Chapter 2)

A baseline prompt contract and one revision that changes one thing. Both were run on 10 development postings and then, once each at the end, on 10 held-out postings. Every answer was scored against my own hand labels.

**What was done by whom.** Yash wrote the labeling rule, the 25 labels, the pass definition, prompt v1, the one change in v2, and the prediction. Yash ran every command. Claude wrote `select_postings.py`, `harness.py` and `run_experiment.py`, and wrote this report's setup, results and limitations from the saved records. The conclusions at the end are Yash's.

## Order of events (UTC, 2026-10-31)

Commit times come from git; run times come from each run record.

| Time | Step | Evidence |
|---|---|---|
| 05:30:59 | Labeling rule committed | `f67a170`, [`LABELING-RULE.md`](LABELING-RULE.md) |
| 05:54:47 | 20 postings selected (seed 7375), split 10 development / 10 held-out | `0a9b18b`, [`selection.json`](selection.json) |
| 06:15:41 | My 25 labels committed (20 here + 5 for the sampling report) | `d93ab09`, [`LABELING-SHEET.md`](LABELING-SHEET.md) |
| 06:18:07 | Pass definition committed | `ee7f57e`, FRICTIONAL.md "My Pass Definition (Written Before Testing)" |
| 06:34:30 | **Baseline (v1), development** | `results/baseline-development-2026-10-31T063430Z.json` |
| 06:41:08 | Prompt v2 and my prediction committed | `13b75f0`, FRICTIONAL.md "My Prompt Revision Decision and Prediction" |
| 06:41:20 | **Revision (v2), development** | `results/revision-development-2026-10-31T064120Z.json` |
| 06:41:56 | **Baseline (v1), held-out**, the one held-out run allowed for v1 (`--final`) | `results/baseline-held_out-2026-10-31T064156Z.json` |
| 06:42:37 | **Revision (v2), held-out**, the one held-out run allowed for v2 (`--final`) | `results/revision-held_out-2026-10-31T064237Z.json` |

`run_experiment.py` refuses a held-out run without `--final`, and refuses a second held-out run for the same prompt name.

## Setup

- **Postings.** Real Databricks postings from the 2026-10-28 baseline response. The 10 "hard cases" have a topic word in the title, a US location and no seniority word. The 10 others were picked at random from titles without a topic word. Each group was split 5 / 5 between development and held-out. **These 20 are not a random sample of the board.**
- **Labels.** Mine, by my labeling rule. **All 20 are `not relevant`**: 10 of 10 in development and 10 of 10 in held-out.
- **Pass, written before testing.** *"I will count a Claude judgment as a pass only if its JSON response passes my validator and its verdict matches my label for that posting. If the response is invalid, unavailable, or disagrees with my label, I will count it as a failure."*
- **Model.** Requested `claude-sonnet-5-5`, one fresh `claude -p` call per posting with all tools off. Claude Code reported both `claude-sonnet-5-5` and `claude-haiku-4-5-20251001` on every call. Only model names were recorded, not tokens per model.

## The one change

`prompts/judgment-v2.md` is `prompts/judgment-v1.md` with one added instruction, plus its heading changed from "v1" to "v2" (which Claude also reads):

```diff
+ End your response immediately after the closing brace `}` of the JSON object. Do not add corrections, comments, or explanations after the JSON.
```

**Why this change.** v1 passed 10 of 10 development postings, so development showed no failure to fix. The change targets the one failure seen anywhere so far that the pass definition counts. In the second watch run (2026-10-31T06:18:34Z), one of 23 answers was valid JSON followed by *"Wait, I need to correct the matched terms… The JSON above stands as my answer."* The validator rejected it as invalid ([run record](../runs/run-databricks-2026-10-31T061834Z.json), posting 8921585002).

**My prediction, committed before v2 was run.** *"I predict that v2 will still pass 10 out of 10 development postings because v1 already passed all of them. I also expect little or no difference on the held-out postings because the sample is small and the extra-text problem was uncommon."*

## Results

| Prompt | Development | Held-out |
|---|---:|---:|
| v1 (baseline) | **10/10** | **10/10** |
| v2 (revision) | **10/10** | **9/10** (1 invalid) |

No answer said `relevant`, and no answer was unavailable. Per-posting tables are in [`results/RESULTS.md`](results/RESULTS.md), and every answer, raw text included, is in the four run records.

### The one failure

**Posting 8697991002, *Specialist Solutions Architect - AI/ML* (held-out), with v2.** The answer was well-formed JSON with verdict `not relevant`, which matches my label. The validator rejected it:

> `matched term 'mlflow' is not in any named posting field ['title', 'content', 'location']`

The posting's title, content and location do not contain "mlflow" at all, not even inside another word. Claude listed it as evidence anyway: `"matched_terms": ["python", "sql", "databricks", "unity catalog", "mlflow"]`.

**v1 made the same claim on the same posting,** but only in its free-text reason: *"…its technical work does overlap with Priya's Python, SQL, Databricks, MLflow, and LLM eval…"*, with `"matched_terms": []`. The validator checks only the structured fields, so v1 passed.

So this failure is **not the one the change targeted.** No answer from either prompt added text after the JSON in these 40 answers.

### A difference the pass rate does not show

| Prompt | Answers with non-empty `matched_terms` |
|---|---:|
| v1 | 2 of 20 (development 1, held-out 1) |
| v2 | 8 of 20 (development 4, held-out 4, including the invalid one) |

Every non-empty list from either prompt includes `databricks`. Some also include `unity catalog`. These are the two company product names that the RECORD rule excludes, because the "About Databricks" text in every posting contains them. The validator accepts them because they do appear in the posting and in `skills.data_bi`.

## Limitations

- **Only one kind of error could be measured.** With all 20 labels `not relevant`, an answer can fail only by being invalid or by saying `relevant`. Whether either prompt finds a relevant job (recall) was not tested. A prompt that always says "not relevant" would also score 10/10.
- **Development was at the ceiling.** v1 scored 10/10, so v2 could not score higher on development.
- **Ten cases per set show very little.** The targeted failure occurred in 1 of 23 answers in the watch run, about 4%. Over 10 answers, a 4% failure would most often appear zero times with either prompt. One answer separates 10/10 from 9/10.
- **One run per prompt per posting.** The sampling report showed that the same prompt cites different fields on different runs, so a single run per posting cannot separate an effect of the change from run-to-run variation. That applies both to the 9/10 and to the 2-versus-8 difference in matched terms.
- **Two text changes, not one.** v2 adds one instruction and also changes its heading from "v1" to "v2".
- **The selection is not the board.** The 20 are hard cases plus random non-topic titles from one day's Databricks board, not a sample of jobs in general.
- **One labeler, one model, one night.** All 40 answers came from one requested model within about nine minutes. Every call also reported Haiku, and what Haiku did is not recorded.
- **The validator does not read prose.** The MLflow claim passed under v1 because it was only in the reason.

## My conclusions

My prediction was mostly correct. Both prompts passed all 10 development postings, and their held-out results were close.

Prompt v1 passed 10 out of 10 held-out postings, while v2 passed 9 out of 10.

The additional instruction in v2 was supposed to prevent Claude from writing extra text after the JSON response. However, the only invalid answer came from an unsupported matched term, MLflow, rather than extra text.

I learned that a small prompt change does not guarantee better results. I also learned that my validator can catch unsupported evidence in structured fields, but not necessarily in the written explanation.

Based on these results, I would keep v1 because it passed all the tested postings. I cannot conclude that v1 is generally better than v2 because the sample is small and all the labels were not relevant.

If I repeated this experiment, I would include both relevant and not relevant jobs to test whether Claude can correctly identify suitable positions.
