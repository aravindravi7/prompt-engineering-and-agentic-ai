# CONTRACT — Job-Search Agent 1

**Author:** Lavanya R. **Written:** 2026-10-29, before any agent code existed.

**Provenance:** every decision below is Lavanya's, made by answering
multiple-choice questions on 2026-10-29. Claude typed the answers up into this
file. Lavanya chose the failure sentence from four options Claude offered. The
sponsorship phrase list was proposed by Claude, after reading the real Datadog
board, and approved by Lavanya. See SOURCES.md.

## In

| Input | Value | Needed for |
|---|---|---|
| Board | Greenhouse board token `datadog` | building the one allowed URL |
| Résumé | a fictional persona résumé as JSON (`persona/priya-nair.resume.json`) | judging relevance |
| State file | `state/seen_ids.json` (created on the first run) | remembering posting ids already seen |

The agent needs network access to **one host only**: `boards-api.greenhouse.io`.

## Out

For each posting that is **new since the last run**, the agent returns:

1. `posting_id`, `title` and `location`, copied from the posting.
2. **Rule verdict (a record).**
   - The verdict is `relevant` or `not_relevant`, computed by the rule below.
   - Anyone can recompute it.
   - Its justification names the résumé fields and posting fields that decided it, e.g. `skills.languages: Python` matched in `content`.
3. **Claude verdict (a judgment, labeled as one).**
   - Claude must answer in this exact JSON format and nothing else:
     ```json
     {"posting_id": 123, "verdict": "relevant | not_relevant",
      "resume_fields": ["skills.languages"], "posting_fields": ["title"],
      "reason": "one or two sentences"}
     ```
   - A validator rejects anything else: wrong id, extra keys, empty field lists, or a verdict outside the two values.
   - A rejected answer is shown as `INVALID`, never as a verdict.

The first run is a **baseline**: it saves the ids and reports **zero** postings as new.

## Refuses

The agent will not:

- **Fetch** any host that is not on the allow-list (`boards-api.greenhouse.io`).
- **Show a real résumé** on screen or on GitHub. It refuses to run on a résumé whose email is not `@example.com` or whose phone number has no `555`.
- **Present a model's judgment as a fact.** Every Claude verdict is labeled "judgment" and is never merged into the rule verdict.
- **Apply, email, message or log in** anywhere.

## The rule

A posting is **relevant** only if **all five** checks pass. Otherwise it is **not relevant**.

**Matching.** Matching is **whole words only, ignoring upper/lower case**. "SQL" does not match "PostgreSQL", and "AI" does not match "maintain".

**Description text.** The description is the posting's `content` field, HTML-unescaped and with tags removed.

1. **Good title.** `title` contains at least one of: `AI`, `Machine Learning`, `ML`, `Software Engineer`, `Intern`, `New Grad`, `Early Career`.
2. **No bad title word.** `title` contains none of: `Senior`, `Sr`, `Staff`, `Principal`, `Distinguished`, `Manager`, `Director`, `Lead`, `Sales`, `PhD`, `Research Scientist`.
3. **US location.**
   - Split `location.name` on `;`.
   - At least one part must contain `USA` or `United States`.
   - Any US city counts, and so does US remote.
4. **At least 2 skills.** The description mentions at least **2 different** skills from these résumé fields:
   - `skills.languages`
   - `skills.data_bi`
   - `skills.backend_automation`
   - `skills.database_cloud`

   For Priya those are: Python, SQL, Databricks, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake, AWS. `familiar_with_not_shipped` does **not** count.
5. **No "we can't sponsor".** Priya needs sponsorship, so the description must contain none of these phrases:
   - "unable to sponsor"
   - "not able to sponsor"
   - "cannot sponsor"
   - "can't sponsor"
   - "will not sponsor"
   - "does not sponsor"
   - "do not sponsor"
   - "without sponsorship"
   - "no sponsorship"
   - "sponsorship is not available"

   The bare word "sponsor" does **not** count. On 2026-10-29, all 9 Datadog postings that mentioned "sponsor" were about events or executive sponsors, not visas.

**Justification.** The justification lists every check, whether it passed, and the exact field and matched words. For example: `title: "AI"`, `location.name: "New York, New York, USA"`, `content ∩ skills: Python, AWS`.

## Wrong versions the tests must catch

1. **Verdicts on the wrong jobs.** Verdicts are paired with the wrong posting ids, e.g. after sorting one list but not the other.
2. **A "why" that cites nothing.** The justification names no résumé field and no posting field.
3. **Old jobs reported as new.** An id already saved in the state file shows up as "new" in the next run.

## What a failure looks like

> On Oct 29, 2026, I'd call this agent a failure if, for any new posting, the
> rule's verdict differs from the verdict I get by applying CONTRACT.md by hand.
