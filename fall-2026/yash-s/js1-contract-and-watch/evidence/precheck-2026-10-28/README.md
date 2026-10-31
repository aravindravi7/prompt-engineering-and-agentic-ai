# Pre-build check, 2026-10-28

A one-off check of CONTRACT.md v1's rules against the live Databricks board, made after the
contract was committed and before any agent code existed. **This is not the agent and not
one of the two watch runs.** Claude wrote and ran `check_rule2.py`; the numbers in
`output.txt` are its actual output.

| File | What it is |
|---|---|
| `check_rule2.py` | The check of CONTRACT.md v1's rules (Python 3, standard library only). Written by Claude. |
| `output.txt` | Its output, with the fetch time and SHA-256 fingerprints of both inputs. |
| `check_v2.py` | The same check for CONTRACT.md v2's three rules, on the same saved response. Written by Claude. |
| `output-v2.txt` | Its output, run two ways: **A.** v2 as written (2 of 897 relevant); **B.** only Databricks and Unity Catalog excluded, MLflow and Delta Lake counted again (4 of 897 relevant). |

**Inputs.**
- The board response: one request to `https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true` at 2026-10-28T20:22:07Z. HTTP 200, 9,816,168 bytes. **Not kept in this folder** because of its size. Its SHA-256 is in `output.txt`. A new fetch returns a different board, so it would not reproduce these numbers exactly.
- The résumé: Priya Nair, a fictional persona from The Reallocation Engine's `search/examples/priya-nair/resume.example.json`.

**Choices the check made that CONTRACT.md v1 does not state.**
- Skills: all five lists under `skills` (12 skills). The `agent_note` string was left out.
- Text: `content` HTML-unescaped, tags removed, then unescaped again.
- Matching: whole word, case-insensitive (`(?<!\w)skill(?!\w)`).
- Rule 3: "security clearance" searched in title and content.

**Rerun.**

```bash
python3 check_rule2.py <saved board response.json> <resume.json>
python3 check_v2.py    <saved board response.json> <resume.json>
python3 check_v2.py    <saved board response.json> <resume.json> --exclude "Databricks,Unity Catalog"
```
