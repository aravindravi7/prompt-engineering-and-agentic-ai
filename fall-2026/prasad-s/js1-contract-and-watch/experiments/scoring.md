# Scoring rule (JS1 prompt experiment) — written 2026-10-29, before any development or held-out Claude reply exists

- A reply PASSES only if the validator accepts it (CONTRACT.md §6) AND its verdict equals my hand label for that posting.
- A rejected reply counts as a FAIL. I record why it was rejected.
- Pass rate = passes / 10, reported separately for development and held-out, for the baseline and the revision.
- Known limit, written before results: all 10 development labels are not_relevant, so a pass here shows a valid reply that agrees on a negative case. With 10 cases, one reply changes the rate by 10 points.
