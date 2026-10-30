# Two judges — databricks run 2026-10-30T204649Z (live)

- Rule: CONTRACT.md v2 (2026-10-30) — a **record**, recomputable by hand.
- Claude: `baseline.md` via `claude -p` — a **judgment**, not a fact. INVALID = rejected by the validator.

| id | title | location | rule (record) | Claude (judgment) | agree? |
|---|---|---|---|---|---|
| 8459031002 | Sr. Counsel, Regulatory | Bellevue, Washington; Seattle, Washington; Washington, D.C. | not_relevant | INVALID | — |
| 8569528002 | Lakebase Sales Specialist, Benelux | Amsterdam, Netherlands | not_relevant | INVALID | — |
| 8569578002 | Lakebase Sales Specialist (Greater China Region) | Singapore | not_relevant | not_relevant | yes |
| 8824171002 | AI Sales Director | San Francisco, California; United States; West Coast - United States | not_relevant | INVALID | — |
| 8860646002 | Analyst Relations Manager | United States | not_relevant | INVALID | — |
| 8917482002 | Business Development Representative (UKI) | London, United Kingdom | not_relevant | INVALID | — |
| 8922120002 | Sr. Counsel, Employment | Bellevue, Washington; Seattle, Washington; Washington, D.C. | not_relevant | INVALID | — |
| 8922730002 | Sr. Collections Analyst | Bengaluru, India | not_relevant | INVALID | — |
| 8924302002 | Business Development Representative (German-speaking, DACH) | Munich, Germany | not_relevant | not_relevant | yes |
| 8924844002 | Lakebase Sales Specialist (Greater China Region) | China | not_relevant | INVALID | — |

## Claude's reasons (verbatim, with date)

- **8459031002** (2026-10-30T21:15:28+00:00, claude-opus-5-5): resume_fields must be a non-empty list of strings
- **8569528002** (2026-10-30T21:15:34+00:00, claude-opus-5-5): resume_fields must be a non-empty list of strings
- **8569578002** (2026-10-30T21:15:38+00:00, claude-opus-5-5): The title 'Lakebase Sales Specialist (Greater China Region)' contains none of the required keywords and contains the excluded word 'Sales'. The location is Singapore, not the United States.
- **8824171002** (2026-10-30T21:15:44+00:00, claude-opus-5-5): resume_fields must be a non-empty list of strings
- **8860646002** (2026-10-30T21:15:48+00:00, claude-opus-5-5): resume_fields must be a non-empty list of strings
- **8917482002** (2026-10-30T21:15:54+00:00, claude-opus-5-5): resume_fields must be a non-empty list of strings
- **8922120002** (2026-10-30T21:16:00+00:00, claude-opus-5-5): resume_fields must be a non-empty list of strings
- **8922730002** (2026-10-30T21:16:05+00:00, claude-opus-5-5): resume_fields must be a non-empty list of strings
- **8924302002** (2026-10-30T21:16:10+00:00, claude-opus-5-5): The title (Business Development Representative) has none of the required keywords, and the location is Munich, Germany, not the United States. The content mentions only Databricks and Unity Catalog from the résumé, which is incidental for a sales role.
- **8924844002** (2026-10-30T21:16:16+00:00, claude-opus-5-5): resume_fields must be a non-empty list of strings
