
# CONTRACT.md: Job-Search Agent 1 (v2)

Updated on 2026-10-28 after checking the Databricks board. This version replaces my first contract before I build the agent.

## 1. In: what the agent takes

The agent uses:

1. **One public job board:** Databricks on Greenhouse (board name `databricks`). It can make HTTPS requests only to `boards-api.greenhouse.io`. It uses the jobs endpoint with `content=true`.
2. **A fake résumé:** Priya Nair's JSON résumé at `search/examples/priya-nair/resume.example.json`. For the submitted project, I will keep a copy inside my JS1 folder so it works without my other local repository. The agent reads `skills`, `experience`, and `projects`. It does not use my real résumé.
3. **A state file:** A list of job posting IDs seen in earlier successful runs. If the state file does not exist, this is the first run (the baseline).

I will use the target job titles written in section 4. The agent will not depend on `profile.yml` to choose titles.

Before running, the agent checks that the fake résumé has an email ending in `@example.com` and a phone number containing `555`. If it fails either check, the agent stops.

The résumé's `skills` value is not one list. It has groups. I will use skills from `languages`, `data_bi`, `backend_automation`, and `database_cloud`. I will not count `familiar_with_not_shipped` or the `agent_note` text as proven skills.

## 2. Out: what the agent gives back

The agent first saves the **raw response** from Greenhouse to a dated JSON file, before parsing or changing it. It also records the fetch time.

For each new posting, it reports:

- The posting `id` and `title`.
- A **RECORD** result: `relevant` or `not relevant`, based on my exact rules in section 4.
- A reason that names the posting fields and résumé fields used, including the matching title, matching skills, and whether the clearance blocker was found.
- A separate **JUDGMENT** from Claude, if Claude is available. This is Claude's opinion and is never presented as a fact.

Claude's response must be valid JSON with exactly these fields:

```json
{
  "posting_id": 12345,
  "verdict": "relevant",
  "reason": "The posting title and requirements match the resume skills."
}
```

`posting_id` must be the ID of the job being checked, `verdict` must be `relevant` or `not relevant`, and `reason` must be a non-empty string. The reason must refer to real fields and values from that posting and the résumé. A wrong-format response or wrong ID is saved as **invalid** and is not silently fixed or used as a verdict. The RECORD result still stays available.

On the **first successful run**, the agent saves all posting IDs as the baseline and reports **zero new postings**. On later successful runs, it reports only IDs not already in state. It updates the state file **after** saving the raw response and successfully processing the run. If fetching, parsing, or processing fails, the old state file stays unchanged.

The agent counts postings by unique `id`, not by title. If two postings have the same title but different IDs (for example, different locations), they are two postings. It will also show the number of unique titles so repeated titles are visible. An ID repeated within the same response is processed only once.

## 3. Refuses: what the agent will never do

- Contact a host other than `boards-api.greenhouse.io`, use HTTP instead of HTTPS, or follow a redirect to another host.
- Read, upload, publish, or show my real résumé.
- Continue if the fictional résumé fails the email or phone check.
- Apply for a job, send messages or emails, or log in to a site.
- Treat Claude's JUDGMENT as a confirmed fact or replace the RECORD result with it.
- Accept a Claude response with missing fields, extra fields, the wrong posting ID, a wrong verdict value, or an unsupported reason.
- Make up résumé skills, job requirements, or reasons that are not supported by the input.
- Change the state file when a run fails.

## 4. The rule: how a posting becomes relevant (RECORD)

A posting is **relevant** only when **all three** checks pass.

**Rule 1: Job title.** I match the `title` field, ignoring capital letters. The title must include one of these exact phrases as whole words:

- `AI Engineer`
- `ML Engineer`
- `Machine Learning Engineer`
- `Applied AI Engineer`
- `Data Engineer`
- `GenAI Engineer`

I also allow a title with both `Software Engineer` and one of `AI`, `ML`, `GenAI`, or `Machine Learning` as whole words. A general mention of `AI` by itself is not enough. This avoids matching titles such as AI marketing or AI finance roles just because they contain AI. `Data Engineering` by itself is not the same as `Data Engineer` under this rule.

**Rule 2: Skills.** I use the posting's `content` field, first decoding HTML entities and removing HTML tags to get readable text. I ignore capital letters and only count whole-word or whole-phrase matches. I count distinct skills, not repeated mentions of the same skill.

I do **not** count these company product names even if they appear in Priya's résumé: `Databricks`, `Unity Catalog`, `MLflow`, and `Delta Lake`. I also do not count skills in `familiar_with_not_shipped`. The posting must contain at least **two different remaining skills** from the allowed résumé skill groups.

For v2 I am still searching the full cleaned posting text. This is a known limit: a skill in general company text may still count. I will report that limit instead of claiming the agent can always separate requirements from boilerplate.

**Rule 3: Blocker.** I look for the exact phrase `security clearance`, ignoring capital letters, in the `title` and cleaned `content`. If it appears anywhere, the posting is **not relevant**, even if it says `no security clearance required`. This is a simple and strict rule that I can test.

If **any** rule fails, the RECORD verdict is `not relevant`. The RECORD reason must identify which checks passed or failed and include actual field names such as `title`, `content`, and `skills.languages`.

## 5. Wrong versions: two bad versions my tests must catch

1. **A verdict is attached to the wrong job ID.** This can happen if jobs get sorted or shifted after checking them. My test uses a small saved fixture with known posting IDs and expected results. I will check the result against each exact ID, not its position in a list.
2. **A reason is empty, vague, or unsupported.** My test checks reasons for both relevant and not relevant results. Each reason must name the actual posting field and résumé field used, and any skill or title match in the reason must exist in that input. It must also explain a failed check when the verdict is not relevant.

I will also test that different IDs with the same title are counted separately, and that a failed run does not update state.

## 6. What a failure looks like

2026-10-28: I will call a run a failure if any verdict is connected to the wrong posting ID, if a RECORD result breaks the rules above, or if a failed run changes the state file.

## Why I changed v1

I predicted that around 80% of jobs would pass the original two-skill check. Claude fetched 897 Databricks postings and found that **897 out of 897 (100%)** passed. When Claude tested the rule without Databricks product names, **338 out of 897 (37.7%)** passed. I decided to remove those product names from my skill count and make the title check more specific.

Claude wrote and ran the pre-build check. The test output is recorded in `evidence/precheck-2026-10-28/output.txt`. My prediction, the test findings, and my decisions are also recorded in `FRICTIONAL.md`.

---

Yash Saraf, 28 October 2026
