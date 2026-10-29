#!/usr/bin/env python3
"""Job-Search Agent 1: the watch (CONTRACT.md v3).

One public Greenhouse board, one fictional résumé, new postings only. This file
fetches, saves the raw response, finds the posting ids that are new since the last
successful run, and gives each new posting two verdicts from judge.py: a RECORD
(my written rule) and a JUDGMENT (Claude's opinion, labeled as one).

usage (from this folder):
  python3 watch.py --board databricks \
                   --resume persona/priya-nair.resume.example.json \
                   --state  state/databricks.state.json \
                   --out    runs \
                   --prompt prompts/judgment-v1.md --model claude-sonnet-5-5
  --from-file <saved response.json>  run against a saved response; the run is labeled SEEDED
  --no-judgment                      do not ask Claude; every JUDGMENT is recorded as unavailable

exit codes: 0 ok, 2 refused input (host, résumé, state file, prompt), 3 fetch, parse or processing failure.
Python 3 standard library only.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import judge

ALLOWED_HOSTS = {"boards-api.greenhouse.io"}    # CONTRACT.md v2, section 3: one host, HTTPS only
KEPT_FIELDS = ("id", "title", "absolute_url", "location", "first_published", "updated_at", "requisition_id")


class InputError(Exception):
    """Refused input: exit 2, nothing written."""


class FetchError(Exception):
    """Fetch or parse failed: exit 3, state file untouched."""


def board_url(board):
    if not re.fullmatch(r"[a-z0-9-]+", board or ""):
        raise InputError(f"board name looks wrong: {board!r}")
    return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


def assert_allowed(url):
    p = urlparse(url)
    if p.scheme != "https":
        raise InputError(f"refusing {url!r}: HTTPS only")
    if p.hostname not in ALLOWED_HOSTS:
        raise InputError(f"refusing host {p.hostname!r}: not on the allow-list {sorted(ALLOWED_HOSTS)}")


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect could leave the allow-list, so every redirect is refused."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FetchError(f"refusing redirect ({code}) to {newurl!r}")


def fetch(url, timeout=60):
    assert_allowed(url)
    opener = urllib.request.build_opener(RefuseRedirects)
    req = urllib.request.Request(url, headers={"User-Agent": "js1-contract-and-watch (INFO 7375 coursework)"})
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.read()
    except FetchError:
        raise
    except Exception as e:
        raise FetchError(f"fetch failed: {e}") from e


def load_resume(path):
    """The persona check runs before anything else. Error messages never echo contact values."""
    try:
        r = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise InputError(f"cannot read résumé {path}: {e}") from e
    personal = r.get("personal") if isinstance(r, dict) else None
    if not isinstance(personal, dict):
        raise InputError("résumé has no 'personal' object")
    if not str(personal.get("email", "")).lower().endswith("@example.com"):
        raise InputError("résumé email does not end in @example.com; refusing a résumé that may be real")
    if not re.search(r"55501\d\d$", re.sub(r"\D", "", str(personal.get("phone", "")))):
        raise InputError("résumé phone is not in the fictional 555-01xx range; refusing a résumé that may be real")
    if not isinstance(r.get("skills"), dict):
        raise InputError("résumé 'skills' must be an object of skill groups")
    return r


def load_state(path, board):
    """None means no state file: this run is the baseline. A bad state file is refused, never overwritten."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        s = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise InputError(f"state file {p} is unreadable ({e}); refusing to overwrite it") from e
    ok = (isinstance(s, dict) and s.get("board") == board and isinstance(s.get("seen_ids"), list)
          and all(type(i) is int for i in s["seen_ids"]))
    if not ok:
        raise InputError(f"{p} is not a state file for board {board!r}; refusing to overwrite it")
    return s


def parse_jobs(raw):
    """Postings keyed by id. An id repeated within one response is kept once and counted."""
    try:
        payload = json.loads(raw)
    except ValueError as e:
        raise FetchError(f"response is not JSON: {e}") from e
    jobs = payload.get("jobs") if isinstance(payload, dict) else None
    if not isinstance(jobs, list):
        raise FetchError("response has no 'jobs' list")
    by_id, repeated = {}, 0
    for j in jobs:
        if not isinstance(j, dict) or type(j.get("id")) is not int:
            raise FetchError(f"posting without an integer id: {str(j)[:80]}")
        if j["id"] in by_id:
            repeated += 1
            continue
        by_id[j["id"]] = j
    return by_id, repeated


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json_atomic(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def run(board, resume_path, state_path, out_dir, from_file=None, now=None,
        prompt=None, model=judge.DEFAULT_MODEL, ask=None):
    """prompt=None means Claude is not asked: every JUDGMENT is recorded as unavailable."""
    ask = ask or judge.call_claude
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H%M%SZ")
    url = board_url(board)
    assert_allowed(url)
    resume = load_resume(resume_path)
    if prompt is not None and not Path(prompt).is_file():
        raise InputError(f"prompt file {prompt} not found")
    state = load_state(state_path, board)

    if from_file:
        try:
            raw = Path(from_file).read_bytes()
        except OSError as e:
            raise FetchError(f"cannot read saved response {from_file}: {e}") from e
        source = f"SEEDED: saved file {Path(from_file).name}, not a live fetch"
    else:
        raw = fetch(url)
        source = "live fetch"

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw_path = out / f"raw-{board}-{stamp}.json"
    raw_path.write_bytes(raw)                       # raw first, byte for byte, before anything parses it

    jobs, repeated = parse_jobs(raw)
    baseline = state is None
    seen_before = set() if baseline else set(state["seen_ids"])
    new_ids = [] if baseline else sorted(set(jobs) - seen_before)
    gone_ids = [] if baseline else sorted(seen_before - set(jobs))
    seen_after = seen_before | set(jobs)            # a posting that disappears stays seen

    new_postings = []
    for i in new_ids:                               # both judges look up the posting by its own id
        posting = jobs[i]
        if prompt is None:
            jud = not_asked(posting["id"], model)
        else:
            jud = judge.judgment(posting, resume, prompt, model=model, ask=ask)
        new_postings.append({"id": i, "original": {k: posting.get(k) for k in KEPT_FIELDS},
                             "record": judge.record_verdict(posting, resume), "judgment": jud})

    record = {
        "agent": "watch.py",
        "contract": "CONTRACT.md v3",
        "board": board,
        "url": url,
        "mode": "BASELINE" if baseline else "WATCH",
        "source": source,
        "run_at": iso(now),
        "fetched_at": None if from_file else iso(now),
        "raw_file": raw_path.name,
        "raw_bytes": len(raw),
        "raw_sha256": sha256(raw),
        "counts": {
            "postings_in_response": len(jobs) + repeated,
            "unique_ids": len(jobs),
            "ids_repeated_in_response": repeated,
            "unique_titles": len({(j.get("title") or "").strip() for j in jobs.values()}),
            "seen_before": len(seen_before),
            "new": len(new_ids),
            "no_longer_listed": len(gone_ids),
            "seen_after": len(seen_after),
        },
        "judges": {
            "RECORD": "my written rule, CONTRACT.md v3 section 4; anyone can recompute it",
            "JUDGMENT": judge.JUDGMENT_LABEL,
            "prompt_file": Path(prompt).name if prompt else None,
            "model_requested": model if prompt else None,
        },
        "verdict_counts": {
            "record_relevant": sum(p["record"]["verdict"] == "relevant" for p in new_postings),
            "judgment_relevant": sum(p["judgment"]["verdict"] == "relevant" for p in new_postings),
            "judgment_status": {s: sum(p["judgment"]["status"] == s for p in new_postings)
                                for s in ("valid", "invalid", "unavailable")},
        },
        "new_postings": new_postings,
        "no_longer_listed_ids": gone_ids,
    }
    run_path = out / f"run-{board}-{stamp}.json"
    write_json_atomic(run_path, record)
    report_path = out / f"report-{board}-{stamp}.md"
    report_path.write_text(report(record), encoding="utf-8")
    write_json_atomic(state_path, {                 # state last: only a run that got this far changes it
        "board": board,
        "updated_at": iso(now),
        "last_run_file": run_path.name,
        "seen_ids": sorted(seen_after),
    })
    return record, raw_path, run_path


def not_asked(posting_id, model):
    return {"judge": "JUDGMENT", "label": judge.JUDGMENT_LABEL, "posting_id": posting_id,
            "status": "unavailable", "verdict": None, "answer": None,
            "errors": ["Claude was not asked (--no-judgment)"], "raw_answer": None,
            "prompt_file": None, "prompt_sha256": None, "model_requested": None,
            "models_reported": [], "asked_at": None, "seconds": None}


def report(record):
    """The human reader's copy of the run record. Every number here comes from the run record."""
    c, v = record["counts"], record["verdict_counts"]
    lines = [
        f"# {record['mode']} run: {record['board']}, {record['run_at']}",
        "",
        f"- Source: {record['source']}",
        f"- Raw response: `{record['raw_file']}` ({record['raw_bytes']:,} bytes, sha256 `{record['raw_sha256']}`)",
        f"- Contract: {record['contract']}",
        f"- Postings {c['postings_in_response']}, unique ids {c['unique_ids']}, unique titles {c['unique_titles']}; "
        f"seen before {c['seen_before']}, **new {c['new']}**, no longer listed {c['no_longer_listed']}",
        f"- RECORD relevant: {v['record_relevant']} of {c['new']}. "
        f"JUDGMENT relevant: {v['judgment_relevant']} of {c['new']} "
        f"(valid {v['judgment_status']['valid']}, invalid {v['judgment_status']['invalid']}, "
        f"unavailable {v['judgment_status']['unavailable']})",
        "",
        "RECORD is my written rule; anyone can recompute it. "
        "JUDGMENT is Claude's opinion under the prompt contract, not a fact. The person decides.",
        "",
    ]
    if record["mode"] == "BASELINE":
        lines.append("Baseline: every id was recorded and none is reported as new.")
        return "\n".join(lines) + "\n"
    if not record["new_postings"]:
        lines.append("No new postings since the last run.")
        return "\n".join(lines) + "\n"
    lines += ["| id | title | RECORD | JUDGMENT (Claude's opinion) |", "|---|---|---|---|"]
    for p in record["new_postings"]:
        j = p["judgment"]
        jtext = j["verdict"] if j["status"] == "valid" else f"_{j['status']}_"
        lines.append(f"| {p['id']} | {(p['original']['title'] or '').strip()} | {p['record']['verdict']} | {jtext} |")
    for p in record["new_postings"]:
        j = p["judgment"]
        lines += ["", f"## {p['id']}: {(p['original']['title'] or '').strip()}", "",
                  f"- Posting: {p['original']['absolute_url']}",
                  f"- **RECORD: {p['record']['verdict']}.** {p['record']['reason']}"]
        if j["status"] == "valid":
            a = j["answer"]
            lines.append(f"- **JUDGMENT (Claude's opinion, {', '.join(j['models_reported']) or j['model_requested']}): "
                         f"{a['verdict']}.** {a['reason']} Matched terms: {a['matched_terms'] or 'none'} "
                         f"(résumé fields {a['resume_fields']}, posting fields {a['posting_fields']}).")
        else:
            lines.append(f"- **JUDGMENT: {j['status']}.** {'; '.join(j['errors'])}")
    return "\n".join(lines) + "\n"


def summary(record, raw_path, run_path, state_path):
    c = record["counts"]
    lines = [
        f"{record['mode']}  board {record['board']}  ({record['source']})",
        f"raw response: {raw_path}  ({record['raw_bytes']:,} bytes, sha256 {record['raw_sha256'][:12]}...)",
        f"postings {c['postings_in_response']}, unique ids {c['unique_ids']}, "
        f"ids repeated in response {c['ids_repeated_in_response']}, unique titles {c['unique_titles']}",
        f"seen before {c['seen_before']}, NEW {c['new']}, no longer listed {c['no_longer_listed']}, "
        f"seen after {c['seen_after']}",
    ]
    if record["mode"] == "BASELINE":
        lines.append("baseline: every id recorded, none reported as new")
    for p in record["new_postings"]:
        j = p["judgment"]
        jtext = j["verdict"] if j["status"] == "valid" else j["status"]
        lines.append(f"  NEW  {p['id']}  {(p['original']['title'] or '').strip()}"
                     f"  | RECORD: {p['record']['verdict']}  | JUDGMENT (Claude's opinion): {jtext}")
    lines += [f"run record: {run_path}", f"report: {str(run_path).replace('/run-', '/report-').replace('.json', '.md')}",
              f"state file: {state_path}"]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Watch one Greenhouse board for new posting ids.")
    ap.add_argument("--board", default="databricks")
    ap.add_argument("--resume", default="persona/priya-nair.resume.example.json")
    ap.add_argument("--state", default="state/databricks.state.json")
    ap.add_argument("--out", default="runs")
    ap.add_argument("--from-file", help="run against a saved response; the run is labeled SEEDED")
    ap.add_argument("--prompt", default="prompts/judgment-v1.md", help="the JUDGMENT prompt contract")
    ap.add_argument("--model", default=judge.DEFAULT_MODEL)
    ap.add_argument("--no-judgment", action="store_true", help="do not ask Claude; JUDGMENT is recorded as unavailable")
    a = ap.parse_args(argv)
    try:
        record, raw_path, run_path = run(a.board, a.resume, a.state, a.out, from_file=a.from_file,
                                         prompt=None if a.no_judgment else a.prompt, model=a.model)
    except InputError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    except FetchError as e:
        print(f"FAILED: {e} (state file unchanged)", file=sys.stderr)
        return 3
    except Exception as e:                          # any other processing failure also leaves state alone
        print(f"FAILED: {type(e).__name__}: {e} (state file unchanged)", file=sys.stderr)
        return 3
    print(summary(record, raw_path, run_path, a.state))
    return 0


if __name__ == "__main__":
    sys.exit(main())
