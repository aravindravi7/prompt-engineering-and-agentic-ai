# Sampling report — Job-Search Agent 1

Run on 2026-10-29 · model claude-sonnet-5-5 · temperature not set in the request (API default) · prompt `prompts/baseline.txt` (SHA-256 `f5d787a9…`) · Tushar Patel

## What was done

- **Postings:** 5 postings from the dev set, chosen **on purpose because they are borderline**. Repeating easy rejects would show no variation.
  - 8314283 Software Engineer: the only posting I labeled `relevant`
  - 8160776 Software Engineer, New Grad (Singapore)
  - 8257892 Security Engineer, New Grad
  - 8128745 Software Engineer, Intern
  - 7947546 Engineering Manager, Forward Deployed
- **Calls:** each posting was asked **4 times**, each a fresh, independent API call with no shared conversation. That's 20 calls in total, and all 20 replies were valid.
- **Inputs:** run date 2026-10-27, postings from `raw/greenhouse-stripe-2026-10-27T203128.json`.
- **Output:** `experiments/results/sampling-2026-10-29T190752.json` and `.md`.

## Results

| Posting | My label | Verdicts (4 calls) | All 4 agree | Matches my label |
|---|---|---|---|---|
| 8314283 | relevant | cannot_tell ×4 | yes | **0 / 4** |
| 8160776 | not_relevant | not_relevant ×4 | yes | 4 / 4 |
| 8257892 | not_relevant | not_relevant ×4 | yes | 4 / 4 |
| 8128745 | not_relevant | not_relevant ×4 | yes | 4 / 4 |
| 7947546 | not_relevant | not_relevant ×4 | yes | 4 / 4 |

**Spread:** none. Every posting got the same verdict on all 4 calls.

## What I can conclude

- **Repeatable is not correct.** On 8314283, Claude gave the same answer 4 times out of 4, and it was wrong 4 times out of 4 against my label. The baseline dev run gave the same `cannot_tell`, which makes 5 calls out of 5.
  - The saved justification shows why: the prompt's R4 didn't count "two (2) years", so R4 was unknown.
  - Consistency here came from Claude following the prompt faithfully, including its gap. Repeating the question could never have revealed that; comparing against my hand label did.
- **On these 5 postings, with this prompt and default settings, I saw no variation.** That's all the sample shows.

## What I cannot conclude

- **That Claude never varies.** 4 calls × 5 postings is a very small sample. Variation that appears less often than about 1 call in 4 could easily go unseen.
- **That the 4 agreeing rejects are correct for the right reasons.** I checked the verdict matched my label, not every justification line. One baseline justification (8314283) cited `job_search.years_experience` for R2, which isn't a field R2 uses.
- **Anything about the revised prompt.** I only sampled the baseline.
- **Anything about other postings, other models, or other settings.**
