#!/usr/bin/env python3
"""Make the inputs for the three action surfaces from saved data. Offline; asks nobody.

All three surfaces do the same task: judge posting 8546367002 for Priya under prompts/judgment-v1.md.
  a-paste-into-chat.txt   the prompt and the same JSON message the judge sends, to paste into a chat
  inputs/job_posting.json the posting exactly as the judge shows it (id, title, location, text)
  inputs/resume.json      Priya's six allowed résumé fields, exactly as the judge shows them
  c-task.txt              the instructions for the agent surface, which fetches the board itself

usage (from the js1-contract-and-watch folder):
  python3 action-surface/make_inputs.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER / "experiment"))
import harness as h  # noqa: E402

POSTING_ID = 8546367002          # development hard case: AI Engineer – Forward Deployed Engineering (AI FDE)
PROMPT = FOLDER / "prompts" / "judgment-v1.md"
C_TASK = f"""Do these steps in order. Use only the host boards-api.greenhouse.io.

1. Fetch https://boards-api.greenhouse.io/v1/boards/databricks/jobs and write every job posting id you find there, as a JSON list of integers, to the file state.json in the current folder.
2. Fetch https://boards-api.greenhouse.io/v1/boards/databricks/jobs/{POSTING_ID} and read resume.json in the current folder. resume.json is Priya's résumé.
3. Judge posting {POSTING_ID} for Priya and give your answer.
"""


def main():
    sel = h.load_selection()
    posting = h.load_postings(sel)[POSTING_ID]
    view = h.judge.claude_view(posting, h.load_resume())
    out = HERE / "inputs"
    out.mkdir(parents=True, exist_ok=True)
    (out / "job_posting.json").write_text(json.dumps(view["job_posting"], indent=2, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    (out / "resume.json").write_text(json.dumps(view["resume"], indent=2, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
    message = json.dumps(view, indent=2, ensure_ascii=False)
    (HERE / "a-paste-into-chat.txt").write_text(PROMPT.read_text(encoding="utf-8") + "\n\n---\n\n" + message + "\n",
                                                encoding="utf-8")
    (HERE / "c-task.txt").write_text(C_TASK, encoding="utf-8")
    print(f"posting {POSTING_ID}: {view['job_posting']['title']} ({view['job_posting']['location']})")
    print(f"wrote {out / 'job_posting.json'}, {out / 'resume.json'}, {HERE / 'a-paste-into-chat.txt'}, {HERE / 'c-task.txt'}")


if __name__ == "__main__":
    main()
