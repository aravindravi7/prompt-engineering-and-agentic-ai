"""Action-surface comparison (Chapter 3): one task, three surfaces.

    python3 -m experiments.action_surface

Task: judge posting 6865698002 ("Software Engineer - New Grad (2027 Start)")
for Priya under prompts/revision.md's rule and output format.

  1. paste  - posting and résumé pasted into the prompt; no tools at all.
  2. file   - posting and résumé saved as files; Claude may only Read.
  3. agent  - Claude fetches the posting itself (WebFetch, allowed only for
              boards-api.greenhouse.io) and writes its own state file.

Each surface runs in its own empty temporary folder. Replies, the folder's
files afterwards, and the CLI's permission denials are saved to
evidence/action-surface/.
"""

import json
import os
import shutil
import subprocess
import tempfile

from agent import claude_judge
from experiments.common import load_set

POSTING_ID = 6865698002
PROMPT = "prompts/revision.md"
OUT = "evidence/action-surface"


def call(prompt, cwd, tools, allowed):
    cmd = ["claude", "-p", prompt, "--output-format", "json",
           "--no-session-persistence", "--model", claude_judge.MODEL,
           "--tools", tools]
    if allowed:
        cmd += ["--allowedTools", *allowed]
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=600)
    try:
        return cmd, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return cmd, {"is_error": True, "result": proc.stdout[-2000:],
                     "stderr": proc.stderr[-2000:]}


def files_in(folder):
    out = {}
    for root, _, names in os.walk(folder):
        for n in names:
            p = os.path.join(root, n)
            with open(p, encoding="utf-8", errors="replace") as f:
                out[os.path.relpath(p, folder)] = f.read()[:4000]
    return out


def main():
    resume, postings, _ = load_set()
    posting = postings[POSTING_ID]
    with open(PROMPT, encoding="utf-8") as f:
        template = f.read()
    full = claude_judge.build_prompt(template, posting, resume)
    pointer = {"resume_json": "(read resume.json in the current folder)",
               "description": "(read the posting's content field)"}

    def pointed(where):
        return template.format(
            resume_json=pointer["resume_json"], posting_id=POSTING_ID,
            title=f"(read {where})", location=f"(read {where})",
            description=f"(read {where}: its content field)")

    surfaces = {
        "1-paste": dict(prompt=full, tools="", allowed=[], setup=None),
        "2-file": dict(
            prompt=pointed("posting.json in the current folder"),
            tools="Read", allowed=["Read"], setup="files"),
        "3-agent": dict(
            prompt=pointed(
                "the posting by fetching https://boards-api.greenhouse.io/v1/"
                f"boards/databricks/jobs/{POSTING_ID}")
            + "\n\nAfter answering, also write state.json in the current "
              "folder containing {\"seen_ids\": [" + str(POSTING_ID) + "]}. "
              "Your final message must still be only the JSON object.",
            tools="WebFetch,Read,Write",
            allowed=["WebFetch(domain:boards-api.greenhouse.io)", "Read",
                     "Write"],
            setup="resume"),
    }
    os.makedirs(OUT, exist_ok=True)
    summary = []
    for name, s in surfaces.items():
        folder = tempfile.mkdtemp(prefix=f"js1-{name}-")
        lean = claude_judge.resume_for_prompt(resume)
        if s["setup"] in ("files", "resume"):
            with open(os.path.join(folder, "resume.json"), "w") as f:
                json.dump(lean, f, indent=2)
        if s["setup"] == "files":
            with open(os.path.join(folder, "posting.json"), "w") as f:
                json.dump(posting, f, indent=2)
        before = sorted(files_in(folder))
        cmd, env = call(s["prompt"], folder, s["tools"], s["allowed"])
        after = files_in(folder)
        shutil.rmtree(folder)
        text = env.get("result") or ""
        parsed, errors = claude_judge.validate(text, POSTING_ID, resume)
        rec = {"surface": name, "command": cmd[:1] + cmd[3:],
               "files_before": before, "files_after": after,
               "num_turns": env.get("num_turns"),
               "permission_denials": env.get("permission_denials"),
               "models_used": sorted((env.get("modelUsage") or {}).keys()),
               "raw_reply": text, "verdict": parsed["verdict"] if parsed
               else "INVALID", "errors": errors}
        with open(os.path.join(OUT, name + ".json"), "w") as f:
            json.dump(rec, f, indent=2, ensure_ascii=False)
            f.write("\n")
        summary.append((name, rec["verdict"], rec["num_turns"],
                        len(rec["permission_denials"] or []),
                        sorted(set(after) - set(before)), errors))
    for row in summary:
        print(row)


if __name__ == "__main__":
    main()
