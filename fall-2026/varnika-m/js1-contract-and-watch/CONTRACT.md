# CONTRACT.md

**Date written:** 2026-10-31

## 1. In

I am building a job-search agent that checks Anthropic's public job board and finds new software engineering jobs that may match a candidate's résumé.

The agent uses:

- **Company:** Anthropic
- **Board token:** `anthropic`
- **API URL:** `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true`
- **Résumé:** `persona/aarav-patel.resume.example.json`
- **State file:** `state/anthropic.state.json`
- **Python:** Version 3.9 or later.
- **Judge:** Claude Code CLI, used for the separate AI judgment step.
- **Internet access:** Only the approved Greenhouse API host.

I request `content=true` so I can compare the candidate's skills with the full job description, not just the title.

The résumé belongs to a fictional candidate named Aarav Patel. Before running, the agent checks that the email ends in `@example.com` and the phone number contains `555`. If either check fails, the agent refuses to use the résumé.

## 2. Out

For every new job, the agent reports:

- Job title
- Company name
- Location
- Job posting URL
- Job ID
- Deterministic verdict: `MATCH` or `NOT_MATCH`
- A short explanation for the verdict

Each explanation must name the exact résumé field and job posting field used for every rule, along with the values that were compared.

For example, a skill explanation must name the résumé field, such as `skills.languages`, and the posting field, such as `content`, and show the matching skill.

The agent also produces a separate Claude judgment. It must be labeled **Claude judgment — opinion, not fact**. Claude's output must use this exact JSON format:

`{"label":"CLAUDE_JUDGMENT","verdict":"MATCH","reason":"Short explanation"}`

The verdict must be either `MATCH` or `NOT_MATCH`. A validator checks that the response is valid JSON, has exactly these three keys, uses an allowed verdict, has `label` set to exactly `CLAUDE_JUDGMENT`, and has a non-empty `reason`. The whole reply must be only this JSON object; any other text makes it invalid. If it does not pass, the agent rejects the response instead of accepting it.

The deterministic verdict and Claude's judgment are kept separate. Claude's opinion does not change the deterministic result.

The agent saves the raw API response exactly as received, before processing it. It then processes the jobs and updates the state file with the job IDs it has seen.

On the first run, the agent saves the current jobs as its baseline and reports zero new jobs. On later runs, it reports only job IDs that are not already in the state file.

If I run the agent using a previously saved API response instead of a fresh API request, I label that run **seeded**.

If fetching the job board fails, the agent does not change the state file.

## 3. Refuses

My agent will not:

- Access websites outside the approved Greenhouse API host.
- Use a résumé whose email does not end in `@example.com` or whose phone number does not contain `555`.
- Apply for jobs on the candidate's behalf.
- Send emails or contact recruiters.
- Log in to private accounts.
- Pretend that a job is a match without evidence.
- Treat skills under `familiar_with_not_shipped` as skills used in a shipped project.
- Present Claude's opinion as a proven fact.
- Accept a Claude judgment that fails the output validator.

## 4. The rule

I use the following checklist to decide whether a job is a match. A job must pass **all five rules** to receive a deterministic `MATCH`.

**Rule 1: Job title**

I read the posting's `title` field.

The title must contain at least one of these phrases:

- Software Engineer
- Backend Engineer
- Infrastructure Engineer
- Platform Engineer
- Site Reliability Engineer
- DevOps Engineer
- Data Engineer
- Cloud Engineer

I ignore uppercase and lowercase differences. I match complete words, not partial words.

**Rule 2: Seniority**

I read the posting's `title` field.

The title must not contain any of these complete words:

- Senior
- Sr
- Staff
- Principal
- Lead
- Manager
- Director
- Head
- VP
- Intern
- Internship

I ignore uppercase and lowercase differences.

**Rule 3: Location**

I read the posting's `location.name` field.

A job passes if at least one location in that field contains either:

- The words `United States`, or
- A US state abbreviation or `DC` after a comma, such as `, CA` or `, MA`.

I check each location separately when the field contains multiple locations.

Examples:

- `Remote-Friendly (Travel Required) | San Francisco, CA` — **PASS**
- `London, UK; San Francisco, CA` — **PASS**
- `Remote-Friendly (Travel Required) | Canada` — **FAIL**

A location that only says `Remote` without a US location or the words `United States` fails this rule.

**Rule 4: Experience**

I read the posting's `content` field.

I count every digit-based `N+ years`, `at least N years`, or `N–M years` phrase in the job description, regardless of the words that follow it. A range may be written with a hyphen or a dash, such as `5-8 years` or `3–5 years`. I do not count numbers written as words.

For a range, I use the higher number. For an `N+` or `at least N` phrase, I use N.

I count these phrases wherever they appear in the description, including required and preferred qualifications. If there are multiple qualifying phrases, I use the highest number.

The maximum number must be **three years or less**.

Examples:

- `2+ years of experience` — **PASS**
- `at least 3 years in data engineering` — **PASS**
- `3–5 years of software engineering experience` — **FAIL**
- `4+ years building secure IT systems` — **FAIL**
- `within the last two years` — **not counted**
- `last three years of work` — **not counted**
- No qualifying digit-based phrase — **PASS**

I chose three years because the résumé shows 25 months plus 4 months of experience, which is 29 months in total. The three-year limit is 36 months, so it allows some room above the candidate's stated experience without accepting jobs that ask for substantially more.

**Rule 5: Skills**

I read the candidate's skills from these résumé fields:

- `skills.languages`
- `skills.backend_automation`
- `skills.database_cloud`
- `skills.devops_cicd`

I compare those skills with the posting's `title` and `content` fields.

The skills I check are:

- TypeScript
- Python
- Java
- SQL
- Node.js
- Kafka
- Redis
- MSSQL
- PostgreSQL
- AWS
- Kubernetes
- Docker
- Helm
- Fluent Bit
- Jenkins

At least **two different skills** from this list must appear in the job title or description.

I ignore uppercase and lowercase differences and match complete terms. For example, `Java` must not match `JavaScript`.

I do not count skills listed under `familiar_with_not_shipped`.

The explanation must name the résumé field or fields containing the matching skills and the posting field (`title` or `content`) where each skill appears.

**Worked example**

Imagine a posting with these values (a constructed example, not a real posting):

- `title`: Software Engineer
- `location.name`: United States
- `content`: The job asks for 2+ years of experience and mentions Python, AWS, and Kubernetes.

This job passes all five rules:

1. The title contains Software Engineer.
2. The title does not contain an excluded seniority word.
3. The location contains United States.
4. The experience requirement is two years.
5. The description contains three skills from the candidate's skill list.

I would mark it `MATCH` and explain the result using the exact résumé and posting fields.

## 5. Wrong versions

I will test two incorrect versions of my matching rule. These tests should catch the mistakes before I use the final rule.

**Wrong version 1: Matching skills only in the title**

If I only check the job title for skills, I could reject a good job because the title might say `Software Engineer` while the description mentions Python and AWS.

**Test:** A posting titled `Software Engineer` with Python and AWS only in its description must pass Rule 5 in my final version. The wrong title-only version would fail it.

**Wrong version 2: Matching partial words**

If I search for `Java` without checking word boundaries, I could accidentally match `JavaScript`.

**Test:** A posting that mentions JavaScript but never mentions Java must not count Java as a matching skill. The wrong partial-word version would incorrectly count it.

## 6. Failure

**2026-10-31:** My agent has failed if it reports an already-seen job as new, misses a genuinely new posting, or produces a verdict that cannot be checked against the résumé and posting fields it lists.