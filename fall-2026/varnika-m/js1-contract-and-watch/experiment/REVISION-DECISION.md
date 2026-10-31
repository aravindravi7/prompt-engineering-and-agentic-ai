# Revision decision: revision-v1

Frozen on 2026-10-31, after the baseline's development results and before revision-v1 or the held-out set was run.

**The one change.** `prompts/revision-v1.txt` is `prompts/baseline-v1.txt` with one instruction added:

> Judge only the posting's must-have qualifications (for example "Minimum qualifications", "Requirements" or "You may be a good fit if you"). Preferred or nice-to-have qualifications (for example "Preferred qualifications" or "Strong candidates may also have") never count against the candidate.

Nothing else changed. `diff prompts/baseline-v1.txt prompts/revision-v1.txt` shows only that line and the blank line before it.

**Why this change.** The baseline scored 9/10 against my hand labels on the development set. Its one miss was row 4, "Machine Learning Infrastructure Engineer, Safeguards Research" (5364804008), which I labeled `MATCH`. Claude's reason (2026-10-31 08:20 UTC) leaned on ML-pipeline experience, most of which the posting lists under *Preferred qualifications*, and on the salary range. My labeling rule says nice-to-haves never count against him, so this change brings the prompt closer to my rule.

**Chosen by:** me (Varnika). Claude Code suggested three options; I chose this one.

**My prediction for the development set:** 9/10. I agreed with Claude Code's reasoning: the change removes the preferred ML items, but Claude's main reason on row 4, that Python is not shown in any job bullet, is about a must-have.

**What Claude Code predicted, for comparison:** 9/10. In all five baseline replies on row 4, the main reason was that Python appears in his skills list but in no job bullet, and Python proficiency is a must-have. This change does not touch that reason.

**What I will not do.** Look at the held-out set's Claude replies before both prompts have run on it, or change either prompt after seeing held-out results.
