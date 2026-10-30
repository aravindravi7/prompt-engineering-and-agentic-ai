# Held-out runs

Every run of `experiments/run_prompt.py` on the held-out split, appended by the script,
including runs that stopped early. LABELING-RULE.md: held-out is run last, once per prompt.

| Timestamp (America/New_York) | Prompt file | Prompt SHA-256 | Model | Outcome |
|---|---|---|---|---|
| 2026-10-29T19:19:45-04:00 | `prompts/baseline.txt` | `f5d787a9b88c5ec036b6ba98e1fc254a309e696120f3521e05b9208d0dc92496` | claude-sonnet-5-5 | 10/10 passes, 0 invalid; `experiments/results/baseline-held-out-2026-10-29T191945.json` |
| 2026-10-29T19:20:30-04:00 | `prompts/revised.txt` | `57a45a61215283556329b7e15000f1be5fc59bd9600c6be96ea91151790e6509` | claude-sonnet-5-5 | 10/10 passes, 0 invalid; `experiments/results/revised-held-out-2026-10-29T192030.json` |
