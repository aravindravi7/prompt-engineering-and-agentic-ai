"""Action-surface comparison: the same task three ways, on posting 5440427008 ("Software Engineer, Sandboxing").

    python3 -m tools.action_surface prepare   # writes way 1's paste text (a person pastes it into a chat)
    python3 -m tools.action_surface file      # way 2: Claude may only Read two files in an empty folder
    python3 -m tools.action_surface agent     # way 3: Claude may fetch from one host and Write its own state file

Ways 2 and 3 save the full stream-json transcript, so what Claude read, fetched and wrote is on record.
"""

import gzip
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agent import claude_judge
from agent.resume import load_resume
from agent.rule import description_text

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "action-surface"
JOB_ID = 5440427008
RUN1_RAW = HERE / "evidence" / "raw" / "anthropic-2026-10-31T074011Z.json.gz"
REPLY_FORMAT = ('Reply with exactly one JSON object and nothing else: '
                '{"label":"CLAUDE_JUDGMENT","verdict":"MATCH or NOT_MATCH","reason":"one sentence"}')
TASK = ("Decide whether the job posting is a MATCH for the candidate: the candidate is qualified for the role "
        "as described and it is a realistic next job for them, based only on the résumé and the posting. "
        "Otherwise it is NOT_MATCH. ")


def posting_and_resume():
    jobs = json.loads(gzip.decompress(RUN1_RAW.read_bytes()))["jobs"]
    job = next(j for j in jobs if j["id"] == JOB_ID)
    resume = load_resume(HERE / "persona" / "aarav-patel.resume.example.json")
    return job, resume


def run_claude(workdir, prompt, tools, allowed, name):
    command = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--model", claude_judge.MODEL,
               "--tools", tools, "--allowedTools", *allowed, "--no-session-persistence",
               "--setting-sources", "", "--system-prompt", claude_judge.SYSTEM]
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    done = subprocess.run(command, input=prompt, capture_output=True, text=True, cwd=workdir, timeout=600)
    folder = OUT / name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "transcript.jsonl").write_text(done.stdout, encoding="utf-8")
    events = [json.loads(line) for line in done.stdout.splitlines() if line.strip()]
    tool_calls = [{"tool": block["name"], "input": block["input"]}
                  for e in events if e.get("type") == "assistant"
                  for block in e["message"].get("content", []) if block.get("type") == "tool_use"]
    result = next((e for e in events if e.get("type") == "result"), {})
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    files_after = sorted(p.name for p in Path(workdir).iterdir())
    written = {p.name: p.read_text(encoding="utf-8") for p in Path(workdir).iterdir()
               if p.name not in ("posting.txt", "resume.json")}
    ok, value = claude_judge.validate(result.get("result") or "")
    summary = {"way": name, "asked_at": started, "command": command, "prompt": prompt,
               "tools_available": init.get("tools"), "tool_calls": tool_calls,
               "files_in_folder_after": files_after, "files_written_by_claude": written,
               "final_reply": result.get("result"), "validator": "accepted" if ok else "rejected: %s" % value,
               "models_used": sorted(result.get("modelUsage", {})), "total_cost_usd": result.get("total_cost_usd"),
               "exit_code": done.returncode, "stderr": done.stderr[-500:]}
    (folder / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("way", "tool_calls", "files_written_by_claude", "final_reply",
                                              "validator", "total_cost_usd")}, indent=2, ensure_ascii=False))


def main(step):
    job, resume = posting_and_resume()
    if step == "prepare":
        OUT.mkdir(exist_ok=True)
        (OUT / "way1-paste-this.txt").write_text(claude_judge.build_prompt(job, resume), encoding="utf-8")
        print("wrote action-surface/way1-paste-this.txt")
        return
    workdir = Path(tempfile.mkdtemp(prefix="js1-%s-" % step))
    try:
        (workdir / "resume.json").write_text(json.dumps(claude_judge.resume_for_prompt(resume), indent=2,
                                                        ensure_ascii=False), encoding="utf-8")
        if step == "file":
            (workdir / "posting.txt").write_text("Title: %s\nLocation: %s\n\n%s\n" % (
                job["title"], job["location"]["name"], description_text(job["content"])), encoding="utf-8")
            prompt = ("Read posting.txt and resume.json in the current folder. " + TASK + REPLY_FORMAT)
            run_claude(workdir, prompt, "Read", ["Read"], "way2-file")
        else:
            url = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs/%d" % JOB_ID
            prompt = ("Fetch the job posting at %s (that host only). Read resume.json in the current folder. "
                      % url + TASK + "Then write a file state.json in the current folder recording the posting "
                      "id you checked as seen and your verdict. Finally, " + REPLY_FORMAT[0].lower() + REPLY_FORMAT[1:])
            run_claude(workdir, prompt, "WebFetch,Read,Write",
                       ["WebFetch(domain:boards-api.greenhouse.io)", "Read", "Write"], "way3-agent")
    finally:
        shutil.rmtree(workdir)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "prepare")
