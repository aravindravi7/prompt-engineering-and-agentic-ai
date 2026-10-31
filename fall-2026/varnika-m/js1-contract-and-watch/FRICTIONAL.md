# FRICTIONAL — Job-Search Agent 1

My log of what I tried, what happened, what I checked or changed, and what I accepted, changed or rejected from Claude. Claude Code first drafted the factual lines from the session record, the commits and the saved files. In a later chat, Claude reworded them from this log without adding facts. **The "What I learned" lines are mine. I wrote them myself and did not use the rough suggestions Claude offered for them.**

### 2026-10-31 — The contract: from "Claude writes it" to writing it myself
- **What I tried:** I asked Claude Code to write `CONTRACT.md`. Its draft included a note saying Claude wrote it. I asked Claude Code to remove the note and to have `SOURCES.md` say I wrote the contract. It declined to record authorship that wasn't true and gave me two options: keep its draft and disclose that, or write my own. I wrote my own.
- **What happened:** A first review of my draft found four problems:
  - **Out** did not name the résumé and posting fields.
  - **Rule 3** could not be decided by hand ("based in the United States", "does not automatically pass").
  - **Rule 4** did not say which phrases count or whether preferred qualifications count.
  - **The failure sentence** described error handling, not failure.

  A second review found that Rule 4 contradicted itself. One line said "connects years to experience", while another gave a literal "N+ years of experience" list. About half of the years phrases in engineering postings on the board do not use those words.
- **What I checked, changed, or learned:**
  - I rewrote Rule 3 to require "United States" or a state code after a comma, with three real examples.
  - For Rule 4 I chose digit-based phrases, whatever words follow (option a).
  - I rewrote the failure sentence.
  - **What I learned:** A rule I can't check by hand isn't a rule yet, and I only saw that once I had to write the rules myself instead of approving someone else's.
  - **Still unresolved:** The Rule 1 title list, the Rule 2 seniority list, the 15 skills and the two thresholds come from Claude's discarded draft. I kept them without deriving them myself.
- **From Claude, accepted / changed / rejected:**
  - Accepted every review finding.
  - Kept those lists and thresholds, disclosed in `SOURCES.md`.
  - Rejected nothing.
- **Trace:** `93afbb8`; `SOURCES.md` rows "Discarded contract draft", "Reviews of my CONTRACT.md" and "What I wrote".

### 2026-10-31 — Writing the tests found a gap in my contract
- **What I tried:** Claude Code wrote tests from my committed contract before any code existed.
- **What happened:** My section 2 requires every rule to name a résumé field, but Rules 1–3 did not. The tests could not check something the contract left undefined.
- **What I checked, changed, or learned:**
  - I agreed to name the fields: `experience[].title`, the `experience[]` dates, and `personal.location`.
  - They went into a dated **Changes** section added after the first commit, so the original text stayed as committed.
  - **What I learned:** Writing tests before code showed me that my contract said every rule names a résumé field but never said which one, so a rule I thought was finished wasn't testable.
- **From Claude, accepted / changed / rejected:** Accepted the fields Claude Code proposed. It wrote the addition at my request.
- **Trace:** `7681e8e`; `CONTRACT.md` "Changes".

### 2026-10-31 — Due today, and the board did not change
- **What I tried:** I needed run 2 to show a real change, but the assignment was due the same day.
- **What happened:** The board's response was byte-for-byte identical at 06:00:09 (the board check), 07:40:11 (my run 1) and 08:29:09 UTC (live run 2), with SHA-256 `1e5b62fe…` each time. Live run 2 reported 0 new.
- **What I checked, changed, or learned:**
  - I used the assignment's other option, a seeded run. Run A is a **constructed** earlier response: run 1's saved response minus the 9 postings first published on or after 2026-10-30.
  - Run B replays run 1's saved response and reported those 9 as new, each with both judges.
  - Both runs are labeled seeded, and run A is also labeled constructed.
  - **What I learned:** A seeded run lets me exercise the "new posting" path, but it can't show that the path works on live data, so I have to label it as seeded and constructed.
  - **Still unresolved:** Run A cannot contain postings that closed before run 1. I never saw the "new posting" path on live data.
- **From Claude, accepted / changed / rejected:** Accepted Claude Code's proposal of the seeded pair and its labeling. Claude Code built and ran it.
- **Trace:** `64ca94c`; `seeded/`; README "What ran".

### 2026-10-31 — My labels came out 19 NOT_MATCH, 1 MATCH
- **What I tried:** I hand-labeled the 20 postings using the labeling rule. Claude Code drafted the rule at my request, and it was committed before I saw the postings.
- **What happened:**
  - 19 labels are `NOT_MATCH` and 1 is `MATCH` (row 4, ML Infrastructure Engineer). All 10 held-out labels are `NOT_MATCH`.
  - Claude Code found five notes whose commas broke the CSV and fixed the quoting without changing any wording.
  - It checked my 11 years notes and found that every cited phrase sits in a must-have section. Row 6's heading reads "You might be a good fit if you have".
- **What I checked, changed, or learned:**
  - I did not change any label to make the experiment look better.
  - **What I learned:** With almost no MATCH labels, a high score can come from a prompt that always says NOT_MATCH, so 10/10 on held-out tells me little.
  - **Still unresolved:** With no `MATCH` in held-out, a prompt that always says `NOT_MATCH` would also score 10/10.
- **From Claude, accepted / changed / rejected:** Accepted the labeling rule draft and the CSV quoting fix. The labels themselves are mine.
- **Trace:** `808270d` (rule), `1b50ba1` (the 20 postings), `3ff2be4` (my labels).

### 2026-10-31 — Recomputing one verdict by hand
- **What I tried:** I checked the Rule 4 verdict on "Data Engineer" (5464234008) in seeded run B: "FAIL, highest years phrase is 5 (limit 3)".
- **What happened:** On the live posting page I searched for "years" and found "5+ years of experience in data engineering, analytics engineering, or GTM data roles". The verdict is correct as written, since 5 is more than 3. The phrase, though, sits under **Preferred qualifications**.
- **What I checked, changed, or learned:**
  - The contract's Rule 4 counts preferred qualifications, but my labeling rule says nice-to-haves never count. On postings like this one, the record and my own human rule disagree.
  - **What I learned:** The verdict was right, but checking it showed that my contract and my labeling rule disagree about preferred qualifications, which the automated record could never have told me.
  - **Still unresolved:** I did not change the contract's Rule 4.
- **From Claude, accepted / changed / rejected:** Claude Code pointed me to the line to check. I did the check myself.
- **Trace:** `SOURCES.md` "Recomputation by hand"; `seeded/runs/anthropic-2026-10-31T074535Z.md`, line 104.

### 2026-10-31 — My prediction held, but the revision changed no verdict
- **What I tried:** Claude Code suggested three single changes, and I chose "judge only must-have qualifications". I predicted 9/10 on development. That matched Claude Code's own prediction and reasoning rather than an independent one of mine.
- **What happened:**
  - Revision-v1 scored 9/10 on development, the same as the baseline, and 10/10 on held-out.
  - No verdict changed, but replies citing "minimum" or "must-have" rose from 1 of 20 to 4 of 20.
  - On row 4, Claude still said `NOT_MATCH`: Python is a must-have and appears in none of Aarav's job bullets, only in his skills list.
- **What I checked, changed, or learned:**
  - **What I learned:** My prediction came true, but the prompt change only shifted how Claude worded its replies, not its verdicts, and ten cases can't tell the two prompts apart.
  - **Still unresolved:** Whether row 4 should be `MATCH`. Claude's reading is defensible, and the ten-case sets cannot tell the two prompts apart.
- **From Claude, accepted / changed / rejected:** Accepted the change I picked and the shared prediction. Claude Code ran all the calls.
- **Trace:** `31f068e` (revision and prediction frozen at 08:28:34 UTC, before the first call at 08:28:59); `experiment/PROMPT-EXPERIMENT.md`.