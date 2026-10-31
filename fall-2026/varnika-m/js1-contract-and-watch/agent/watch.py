"""The watch (CONTRACT.md section 2): fetch one board, save the raw response first, report postings new by id.

    python3 -m agent.watch                      # live run against the board
    python3 -m agent.watch --fixture FILE       # seeded run from a saved response
    python3 -m agent.watch --claude             # also ask Claude for a judgment on each new posting
"""

import argparse
import gzip
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import claude_judge
from agent.fetch import BOARD_URL, fetch
from agent.resume import load_resume
from agent.rule import judge

CONTRACT = "CONTRACT.md of 2026-10-31, with its 2026-10-31 Changes addition"


def read_state(path):
    """None before the first run. A state file that exists but cannot be read stops the run."""
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(state.get("seen_ids"), list):
            raise ValueError("no seen_ids list")
    except ValueError as error:
        raise ValueError("refused: state file %s cannot be read (%s); not starting over" % (path, error))
    return state


def write_atomically(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)


def free_name(out_dir, board, stamp):
    base, n = "%s-%s" % (board, stamp), 1
    while any(p.exists() for p in (out_dir / "evidence" / "raw" / (base + ".json.gz"),
                                    out_dir / "runs" / (base + ".json"))):
        n += 1
        base = "%s-%s-%d" % (board, stamp, n)
    return base


def run(board, resume_path, state_path, out_dir, fixture=None, fetcher=None, ask_claude=None, now=None):
    resume = load_resume(resume_path)  # refuses a non-fictional résumé before any fetch
    state_path, out_dir = Path(state_path), Path(out_dir)
    state = read_state(state_path)
    now = now or datetime.now(timezone.utc)
    url = BOARD_URL % board

    if fixture:
        raw, source = Path(fixture).read_bytes(), "seeded"
    else:
        raw, source = (fetcher or fetch)(url), "live"  # a failed fetch raises here; nothing is written

    base = free_name(out_dir, board, now.strftime("%Y-%m-%dT%H%M%SZ"))
    raw_path = out_dir / "evidence" / "raw" / (base + ".json.gz")
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(gzip.compress(raw, mtime=0))  # saved before anything parses it

    jobs, ids_now = [], set()
    for job in json.loads(raw.decode("utf-8"))["jobs"]:
        if job["id"] not in ids_now:
            ids_now.add(job["id"])
            jobs.append(job)

    seen = set(state["seen_ids"]) if state else set()
    new_jobs = [job for job in jobs if job["id"] not in seen] if state else []
    new_postings = []
    for job in new_jobs:
        new_postings.append({
            "job_id": job["id"], "title": job.get("title"), "company_name": job.get("company_name"),
            "location": (job.get("location") or {}).get("name"), "absolute_url": job.get("absolute_url"),
            "rule_verdict": judge(job, resume),
            "claude_judgment": claude_judge.judgment(job, resume, ask_claude) if ask_claude else None,
        })

    runs = (state or {}).get("runs", [])
    record = {
        "contract": CONTRACT, "board": board, "url": url, "run_number": len(runs) + 1,
        "run_kind": "watch" if state else "baseline", "source": source,
        "fixture": str(fixture) if fixture else None,
        "started_at": now.isoformat(timespec="seconds"),
        "raw_file": raw_path.relative_to(out_dir).as_posix(), "raw_bytes": len(raw),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "counts": {"in_response": len(jobs), "seen_before": len(seen), "new": len(new_postings),
                   "missing_since_last_run": len(seen - ids_now)},
        "claude_asked": bool(ask_claude), "new_postings": new_postings,
        "run_file": "runs/%s.json" % base, "report_file": "runs/%s.md" % base,
    }
    write_atomically(out_dir / record["run_file"], json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    write_atomically(out_dir / record["report_file"], report(record))

    runs.append({"run_number": record["run_number"], "started_at": record["started_at"], "source": source,
                 "run_file": record["run_file"], "raw_file": record["raw_file"], "new": len(new_postings)})
    write_atomically(state_path, json.dumps({"board": board, "url": url, "seen_ids": sorted(seen | ids_now),
                                             "runs": runs}, indent=2) + "\n")
    return record


def report(record):
    source = ("SEEDED from saved response `%s`" % record["fixture"]) if record["source"] == "seeded" \
        else "LIVE fetch of `%s`" % record["url"]
    counts = record["counts"]
    lines = [
        "# Run %d: %s board (%s)" % (record["run_number"], record["board"], record["run_kind"]),
        "",
        "- **When:** %s" % record["started_at"],
        "- **Source:** %s" % source,
        "- **Raw response:** `%s` (%d bytes, SHA-256 `%s`)" % (record["raw_file"], record["raw_bytes"],
                                                            record["raw_sha256"]),
        "- **Postings in response:** %d. **Seen before:** %d. **New:** %d. **Gone since last run:** %d."
        % (counts["in_response"], counts["seen_before"], counts["new"], counts["missing_since_last_run"]),
        "- **Contract:** %s" % record["contract"],
        "",
    ]
    if record["run_kind"] == "baseline":
        lines += ["Baseline run: every posting id is recorded as seen, and none is reported as new.", ""]
    elif not record["new_postings"]:
        lines += ["No new postings since the last run.", ""]
    for p in record["new_postings"]:
        verdict = p["rule_verdict"]
        lines += ["## %s (id %s)" % (p["title"], p["job_id"]), "",
                  "%s · %s · %s" % (p["company_name"], p["location"], p["absolute_url"]), "",
                  "**Record (the rule, recomputable): %s**" % verdict["verdict"], ""]
        for c in verdict["checks"]:
            lines.append("- %s %s %s: %s. Posting `%s`; résumé `%s` = %s."
                         % ("PASS" if c["passed"] else "FAIL", c["rule"], c["name"], c["explanation"],
                            c["posting_field"], c["resume_field"], json.dumps(c["resume_value"], ensure_ascii=False)))
        j = p["claude_judgment"]
        lines.append("")
        if j is None:
            lines.append("**%s:** not asked in this run." % claude_judge.LABEL)
        elif j["status"] == "accepted":
            lines.append("**%s: %s.** %s" % (j["label"], j["verdict"], j["reason"]))
        else:
            lines.append("**%s:** %s, so no verdict is counted (%s)." % (j["label"], j["status"], j["rejected_because"]))
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Job-Search Agent 1: the watch.")
    parser.add_argument("--board", default="anthropic")
    parser.add_argument("--resume", default=here / "persona" / "aarav-patel.resume.example.json", type=Path)
    parser.add_argument("--state", default=here / "state" / "anthropic.state.json", type=Path)
    parser.add_argument("--out", default=here, type=Path, help="folder for evidence/raw/ and runs/")
    parser.add_argument("--fixture", type=Path, help="saved response to use instead of fetching (a seeded run)")
    parser.add_argument("--claude", action="store_true", help="ask Claude (Claude Code CLI) about each new posting")
    args = parser.parse_args(argv)

    record = run(args.board, args.resume, args.state, args.out, fixture=args.fixture,
                 ask_claude=claude_judge.ask_claude_cli if args.claude else None)
    counts = record["counts"]
    print("Run %d (%s, %s): %d postings, %d new, %d gone since last run."
          % (record["run_number"], record["run_kind"], record["source"], counts["in_response"],
             counts["new"], counts["missing_since_last_run"]))
    for p in record["new_postings"]:
        j = p["claude_judgment"]
        print("  %s  record=%s  claude=%s  %s" % (p["job_id"], p["rule_verdict"]["verdict"],
                                                (j["verdict"] or j["status"]) if j else "not asked", p["title"]))
    print("Raw response: %s\nRun record:   %s\nReport:       %s" % (record["raw_file"], record["run_file"],
                                                                 record["report_file"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
