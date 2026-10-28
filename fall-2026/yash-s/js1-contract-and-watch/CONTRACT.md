# CONTRACT.md: Job-Search Agent 1

Written before any code was written.

---

## 1. In: what the agent takes

The agent needs two things:

1. **A job board.** One public board only: **Databricks**, on **Greenhouse** (board name: `databricks`).
   It calls one host: `boards-api.greenhouse.io`.
2. **A résumé in JSON.** I use a made-up person, **Priya Nair**, from
   `search/examples/priya-nair/resume.example.json`. She has a fake email (`@example.com`)
   and a 555 phone number. My own résumé is never used in this project.
   The agent reads her `skills`, `experience` and `projects`. Her target roles
   (AI Engineer / ML Engineer, and Data Engineer) come from her `profile.yml`.

The agent also keeps a **state file**: a list of posting ids it has already seen.
If there is no state file, the run is the **first run** (the baseline).

## 2. Out: what the agent gives back

For each **new** posting, the agent gives:

- a **verdict**: `relevant` or `not relevant`
- a **reason** that names the résumé fields and the posting fields it used.
  Example: "résumé `skills` has Python; posting `content` has Python."

Every verdict has a label that says who made it:

- **RECORD**: made by my written rule (section 4). Anyone can check it by hand.
- **JUDGMENT**: made by Claude. It is an opinion, not a fact.

The first run only saves what it sees. It reports **zero** new postings.

## 3. Refuses: what the agent will never do

- Call any host that is not on the allow-list. The list has one host:
  `boards-api.greenhouse.io`. HTTPS only.
- Follow a redirect to another host.
- Show or upload my real résumé. Only Priya Nair appears on screen or on GitHub.
- Say that Claude's opinion is a fact. It is always labeled JUDGMENT.
- Apply to a job, send an email or message, or log in anywhere.
- Accept a Claude answer in the wrong format. It is rejected, not fixed.
- Give a reason that names a field that is not in the résumé or the posting.

## 4. The rule: how a posting becomes "relevant" (RECORD)

A posting is **relevant** only if **all three** are true:

1. The **title** has at least one of these words: "AI", "ML", "machine learning",
   "data engineer". The match ignores capital letters and must be a whole word,
   so "AI" does not match "Email".
2. At least **2** different skills from the résumé's `skills` list appear in the
   posting's `content` (same matching: ignore capitals, whole word).
3. The posting does **not** contain "security clearance".

If any one is false, the posting is **not relevant**.

The reason lists the title word that matched, the skills that matched, and
whether the blocker was found. If someone counts these by hand, they get the same verdict.

## 5. Wrong versions: two bad versions my tests must catch

1. **Verdicts on the wrong postings.** The verdicts are right, but they are
   attached to the wrong posting ids (for example, a list gets sorted or shifted).
   Test: use a small fixture where I already know which posting is relevant.
   Check that the verdict sits on that exact id.
2. **A reason that says nothing.** The verdict looks fine, but the reason is empty,
   vague, or names a field that is not in the data.
   Test: every field and value in a reason must exist in the input. Every
   `relevant` verdict must name at least one résumé field and one posting field.

## 6. What a failure looks like

2026-10-28: I will call a run a failure if any verdict is attached to a different posting id than the one it was computed from.

---

Yash Saraf, 28 October 2026
