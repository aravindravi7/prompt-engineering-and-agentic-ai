
# CONTRACT.md: Job-Search Agent 1 (v3)

Updated on 2026-10-28 after testing CONTRACT.md v2 and running the first baseline.

This version replaces v2 before building the two judges.

## 1. In: what the agent takes

The agent uses:

1. **One public job board:** Databricks on Greenhouse (board name `databricks`). It can make HTTPS requests only to `boards-api.greenhouse.io`. It uses the jobs endpoint with `content=true`.

2. **A fake résumé:** Priya Nair's JSON résumé at `persona/priya-nair.resume.example.json`. The agent does not use my real résumé.

   The agent uses the résumé's skills for the RECORD rules. Claude can also read `experience` and `projects` when making its JUDGMENT.

3. **A state file:** A list of job posting IDs seen in earlier successful runs. If the state file does not exist, this is the first run (the baseline).

I use the target job titles written in section 4. The agent does not depend on `profile.yml` to choose titles.

Before running, the agent checks that the fake résumé has an email ending in `@example.com` and a fictional phone number using the `555-01xx` range. If either check fails, the agent stops.

The résumé's `skills` value contains groups instead of one list.

I use skills from these four groups:

- `languages`
- `data_bi`
- `backend_automation`
- `database_cloud`

I do not count `familiar_with_not_shipped` or `agent_note` as proven skills.

## 2. Out: what the agent gives back

The agent first saves the raw response from Greenhouse to a dated JSON file before parsing or changing it. It also records the fetch time.

For each new posting, it reports:

- The posting `id` and `title`.
- A **RECORD** result: `relevant` or `not relevant`, based on the rules in section 4.
- A reason showing which rules passed or failed and the matching fields.
- A separate **JUDGMENT** from Claude.

RECORD is based on my written rules. JUDGMENT is Claude's opinion and is never treated as a confirmed fact.

### Claude's response format

Claude must return valid JSON with exactly these six fields:

```json
{
  "posting_id": 12345,
  "verdict": "relevant",
  "resume_fields": ["skills.languages"],
  "posting_fields": ["content"],
  "matched_terms": ["Python"],
  "reason": "The posting and resume both mention Python."
}
```

The fields must follow these rules:

1. `posting_id` must match the exact job ID being checked.
2. `verdict` must be `relevant` or `not relevant`.
3. `resume_fields` must be a list of valid résumé field paths. Claude can use the four allowed skill groups, `experience`, and `projects`.
4. `posting_fields` must be a list containing only `title` and `content`. No other posting fields are allowed.
5. `matched_terms` must be a list of strings. Every term must appear in at least one résumé field and one posting field named in the response. Matching ignores capital letters and uses whole words or phrases on the cleaned text, just like Rule 2.
6. `reason` must be a non-empty string explaining Claude's decision.

A `relevant` JUDGMENT must include at least one matched term.

A `not relevant` JUDGMENT can have an empty matched terms list, but it must still give a reason.

The validator checks the JSON structure, field names, posting ID, and matched terms against the input data. It does not claim to prove that Claude's full written explanation is correct.

### Invalid or unavailable judgments

If Claude returns an answer with the wrong format, wrong posting ID, or unsupported matched terms, the agent records the JUDGMENT status as `invalid`.

If Claude is unavailable or cannot return an answer, the agent records the JUDGMENT status as `unavailable`.

In both cases:

- The RECORD result is still provided.
- No Claude verdict is invented.
- The run can still succeed if the other required steps finish correctly.
- The state file is updated after successful processing.

### Baseline and state updates

On the first successful run, the agent saves all posting IDs as the baseline and reports zero new postings.

On later successful runs, it reports only IDs not already in the state file.

The state file updates only after the raw response is saved and the required processing is completed successfully.

If fetching, parsing, or required processing fails, the old state file stays unchanged.

The agent counts postings by unique ID, not by title.

If two postings have the same title but different IDs, they count as separate postings.

If an ID appears more than once in the same response, it is processed only once.

### Live and seeded runs

A run using the live Greenhouse API is recorded as a live run.

A run using `--from-file` is labeled `SEEDED` because it uses saved data instead of fetching new data.

The run record must clearly show which type was used.

## 3. Refuses: what the agent will never do

- Contact a host other than `boards-api.greenhouse.io`, use HTTP instead of HTTPS, or follow a redirect to another host.
- Read, upload, publish, or show my real résumé.
- Continue if the fictional résumé fails the email or phone validation.
- Apply for a job, send emails or messages, or log in to any website.
- Treat Claude's JUDGMENT as a confirmed fact.
- Replace a RECORD result with Claude's opinion.
- Accept a Claude response with missing fields, extra fields, a wrong posting ID, an invalid verdict, or unsupported matched terms.
- Make up résumé skills, job requirements, or evidence.
- Change the state file if a required part of the run fails.
- Label saved-data runs as live API fetches.
- Give Claude access to external tools, websites, or project files while making a JUDGMENT. 
Claude will receive the provided job posting, fictional résumé, and judgment prompt. Claude Code may also include some of its own internal context, as explained in the model check below. Each judgment will use a fresh session, and I will record the model used.



## 4. The rule: how a posting becomes relevant (RECORD)

A job posting is relevant only when all three rules pass.

### Rule 1: Job title

I check the posting's `title` field, ignoring capital letters.

The title must contain at least one of these phrases as whole words:

- `AI Engineer`
- `ML Engineer`
- `Machine Learning Engineer`
- `Applied AI Engineer`
- `Data Engineer`
- `GenAI Engineer`

I also allow titles containing `Software Engineer` together with at least one of these terms:

- `AI`
- `ML`
- `GenAI`
- `Machine Learning`

A general mention of AI is not enough.

For example, a marketing or finance job containing AI in its title should not automatically pass.

`Data Engineering` by itself does not count as `Data Engineer`.

### Rule 2: Skills

I check the posting's `content` field after decoding HTML and removing HTML tags.

Matching ignores capital letters and uses whole words or phrases.

I count each different skill only once, even if it appears many times.

After testing v2, I decided to exclude only these two skills:

- `Databricks`
- `Unity Catalog`

I will count these eight remaining skills:

- Python
- SQL
- Power BI
- LangGraph
- MLflow
- Mem0
- Delta Lake
- AWS

I decided to keep MLflow and Delta Lake because the test showed they were not common in the general company description.

The posting must contain at least **two different skills** from this list.

I am keeping the two-skill rule because I want the agent to match jobs using Priya's skills, not just job titles.

For now, matching checks the full cleaned posting text.

I know this has a limitation because skills mentioned outside the actual job requirements might still count.

I will report this limitation instead of assuming every match is a real requirement.

### Rule 3: Security clearance blocker

I search for the phrase `security clearance` in the posting's `title` and cleaned `content`.

If the phrase appears anywhere, the job is marked `not relevant`.

This includes cases where the posting says `no security clearance required`.

I am keeping this simple rule because it is easy to check and test.

### Final RECORD verdict

A posting is `relevant` only if:

1. The title matches Rule 1.
2. At least two different allowed skills match Rule 2.
3. The security clearance blocker is not found.

If any rule fails, the result is `not relevant`.

The reason must explain which checks passed or failed and name the actual fields and values used.

## 5. Wrong versions: two bad versions my tests must catch

### Wrong version 1: Verdict attached to the wrong posting

The verdict might be correct but attached to the wrong job ID.

This could happen if jobs are sorted or shifted after checking them.

**Test:** I use a saved fixture with known posting IDs and expected results.

I check every verdict against the exact ID instead of its position in a list.

### Wrong version 2: Reason without real evidence

A result might have an empty, vague, or unsupported reason.

**Test:** I check that RECORD reasons use actual input fields and matching values.

For Claude's JUDGMENT, I check the structured fields and matched terms against the résumé and job posting.

A relevant Claude verdict must contain at least one supported matched term.

I also check that invalid Claude answers are rejected rather than silently fixed.

### Additional tests

I will also test that:

- Different IDs with the same title are counted separately.
- Duplicate IDs in one response are processed only once.
- Failed runs do not change the state file.
- Invalid Claude answers are labeled correctly.
- Claude being unavailable does not remove the RECORD result.
- Seeded runs are labeled `SEEDED`.
- The fictional résumé validation works correctly.

## 6. What a failure looks like

My original failure statement from CONTRACT.md v1, committed as `16ecbcd`, was:

2026-10-28: I will call a run a failure if any verdict is attached to a different posting ID than the one it was computed from.

In v2, I added that a run also fails if the RECORD result breaks my written rules or if a failed run changes the state file.

In v3, I am keeping those conditions and adding checks for Claude's structured responses.

An invalid or unavailable Claude JUDGMENT does not automatically make the entire run fail, as long as it is correctly labeled and the RECORD result and other required processing succeed.

## Why I changed v1

I predicted that around 80% of Databricks postings would pass my original two-skill rule.

Claude tested 897 postings and found that all 897 passed.

This happened because the general company description included Databricks and Unity Catalog, which were also in Priya's résumé.

When Claude tested the rule without company product names, 338 of 897 postings passed (37.7%).

I decided to make the matching rules stricter.

Claude wrote and ran the pre-build check.

Evidence: `evidence/precheck-2026-10-28/output.txt`

My prediction and decisions are also recorded in `FRICTIONAL.md`.

## Why I changed v2

Claude tested CONTRACT.md v2 against the same 897 saved postings.

With v2 as written, only 2 of 897 postings were marked relevant.

Claude then tested another version where MLflow and Delta Lake were counted again.

With only Databricks and Unity Catalog excluded, 4 of 897 postings were marked relevant.

I originally removed MLflow and Delta Lake because I trusted Claude's first review. After checking the data, Claude corrected its earlier claim.

I decided to count MLflow and Delta Lake again because they are useful technical skills and removing them could cause my agent to miss relevant jobs.

I also decided to keep the two-skill rule for now.

Claude pointed out that free-text reasons are difficult to verify automatically. I agreed to use structured fields so the code can check the posting ID, field names, and matched terms.

I also clarified what happens when Claude is unavailable or gives an invalid response.

These changes are being written before the judges are built.

Evidence: `evidence/precheck-2026-10-28/output-v2.txt`, part B.

### Additional Note: Claude Code Model Check

On October 28, 2026, I tested Claude Sonnet 5.5 using the command line.

I first ran it from my course folder. The result showed 730 input tokens.

I then ran the same command from an empty temporary folder. This time, it showed 176 input tokens.

Claude pointed out that the folder I run the command from can affect the input sent to the model.

Even in an empty folder, the command used more tokens than my short prompt. Around 170 tokens may come from Claude Code's own instructions or setup, but I cannot see exactly what they contain.

I learned that disabling tools and using an empty folder reduces extra context, but does not guarantee that Claude receives only my prompt.

For my project, I will run judgments from an empty temporary folder with tools disabled and record the model used.

Evidence: `evidence/model-check-2026-10-28/`

---

Yash Saraf, 28 October 2026
