# Prompt run — `prompts/baseline.txt` on held-out

- Passes: **10 / 10**
- Invalid replies: 0 (each counted as a miss)
- Model requested: claude-sonnet-5-5; named in responses: claude-sonnet-5-5
- Temperature: not set in the request (API default)
- Prompt file: `prompts/baseline.txt`
- Prompt SHA-256: `f5d787a9b88c5ec036b6ba98e1fc254a309e696120f3521e05b9208d0dc92496`
- Run date for R2: 2026-10-27 (the date the labels used)
- Postings from: `raw/greenhouse-stripe-2026-10-27T203128.json`; labels from `experiments/labels.csv`
- Run at: 2026-10-29T19:19:45-04:00

Claude verdicts are **model judgment**. My labels are hand labels. A pass is an exact
match; `cannot_tell` against `relevant` is a miss. With 10 cases, a difference of one
or two may be noise.

| Posting | My label | Claude verdict | Match | Valid |
|---|---|---|---|---|
| 7982720 | not_relevant | not_relevant | yes | yes |
| 6717520 | not_relevant | not_relevant | yes | yes |
| 8260980 | not_relevant | not_relevant | yes | yes |
| 8161567 | not_relevant | not_relevant | yes | yes |
| 7208537 | not_relevant | not_relevant | yes | yes |
| 7819426 | not_relevant | not_relevant | yes | yes |
| 8206731 | not_relevant | not_relevant | yes | yes |
| 8203975 | not_relevant | not_relevant | yes | yes |
| 7983456 | not_relevant | not_relevant | yes | yes |
| 8197891 | not_relevant | not_relevant | yes | yes |
