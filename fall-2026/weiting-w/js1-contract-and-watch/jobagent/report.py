"""Assembling the run report (CONTRACT.md §2).

One entry per new posting, each entry keyed to the posting it describes by id.
There is no index arithmetic between the posting list and the verdict list
anywhere in this module; that is the whole content of wrong version W1, and
building the entry inside the loop over postings is how it is avoided.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import rule as rule_judge
from .validator import check_citation


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def entry_for(posting: dict, resume: dict, claude_verdict: dict | None = None) -> dict:
    """One report entry for one posting."""
    entry = {
        "posting_id": posting["id"],
        "title": posting.get("title"),
        "absolute_url": posting.get("absolute_url"),
        "updated_at": posting.get("updated_at"),
        "rule_verdict": rule_judge.judge(posting, resume),
    }
    if claude_verdict is not None:
        entry["claude_verdict"] = claude_verdict
    return entry


def self_check(entry: dict, posting: dict, resume: dict) -> None:
    """Assert O1, O2, O3 and O4 on an entry before it is written out.

    The agent checks its own output against the contract on every run, so a
    contract violation is a failed run rather than a plausible-looking report.
    """
    if entry["posting_id"] != posting["id"]:
        raise AssertionError("O1: entry is not keyed to the posting it describes")
    for name in ("rule_verdict", "claude_verdict"):
        verdict = entry.get(name)
        if verdict is None:
            continue
        expected_kind = "record" if name == "rule_verdict" else "judgment"
        if verdict.get("kind") != expected_kind:
            raise AssertionError(f"O3: {name}.kind is not {expected_kind!r}")
        if verdict.get("validator") == "reject":
            continue
        if (verdict.get("gate_failed") is None) != (verdict.get("verdict") == "relevant"):
            raise AssertionError(f"O4: {name} gate_failed/verdict disagree")
        justification = verdict.get("justification") or []
        if not justification:
            raise AssertionError(f"O2: {name}.justification is empty")
        for i, cite in enumerate(justification):
            check_citation(cite, posting, resume, where=f"{name}.justification[{i}]")


def build(*, url, status, raw_info, postings, new, state_before_sha, state_after_sha,
          state_path, is_baseline, resume, entries, board, resume_summary) -> dict:
    return {
        "report_version": 1,
        "generated_at": utc_now(),
        "board": board,
        "url": url,
        "http_status": status,
        "raw_response": raw_info,
        "resume": resume_summary,
        "rule_version": rule_judge.RULE_VERSION,
        "is_baseline": is_baseline,
        "counts": {
            "postings_in_response": len(postings),
            "already_seen": len(postings) - len(new),
            "new": 0 if is_baseline else len(new),
        },
        "state": {
            "path": str(state_path),
            "sha256_before": state_before_sha,
            "sha256_after": state_after_sha,
        },
        "entries": entries,
    }


def write(report: dict, runs_dir: str | Path) -> Path:
    """Write the run report, never over an existing one.

    Two runs inside the same second collided on the filename and the second
    silently overwrote the first, which destroys exactly the evidence this
    directory exists to hold. The suffix is the fix; the test is
    ``test_two_runs_in_the_same_second_do_not_overwrite_each_other``.
    """
    runs_dir = Path(runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)
    stamp = report["generated_at"].replace(":", "").replace("-", "")
    path = runs_dir / f"run-{stamp}.json"
    suffix = 2
    while path.exists():
        path = runs_dir / f"run-{stamp}-{suffix}.json"
        suffix += 1
    report = {**report, "run_report_path": str(path)}
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def human_summary(report: dict) -> str:
    lines = []
    counts = report["counts"]
    kind = "BASELINE" if report["is_baseline"] else "WATCH"
    source = report["raw_response"]
    transport = (
        f"http={report['http_status']}"
        if source.get("source") == "live"
        else f"replay of {source.get('source_label')!r}"
    )
    lines.append(
        f"[{kind}] {report['url']}  {transport}  "
        f"postings={counts['postings_in_response']}  "
        f"already_seen={counts['already_seen']}  new={counts['new']}"
    )
    lines.append(f"  raw response: {report['raw_response']['path']}")
    lines.append(f"  sha256: {report['raw_response']['sha256']}")
    if report["is_baseline"]:
        lines.append(
            "  first run: every posting recorded as seen, none reported as new "
            "(CONTRACT.md R5)."
        )
        return "\n".join(lines)
    if not report["entries"]:
        lines.append("  nothing new since the last run.")
        return "\n".join(lines)
    for entry in report["entries"]:
        lines.append("")
        lines.append(f"  #{entry['posting_id']}  {entry['title']}")
        lines.append(f"    {entry['absolute_url']}")
        rule = entry["rule_verdict"]
        lines.append(
            f"    RECORD   (rule {rule['rule_version']}): {rule['verdict']}"
            + (f"  first failing gate: {rule['gate_failed']}" if rule["gate_failed"] else "")
        )
        for cite in rule["justification"]:
            lines.append(
                f"      because {cite['resume_field']} = {cite['resume_value']!r} "
                f"vs posting.{cite['posting_field']} containing {cite['evidence']!r}"
            )
        claude = entry.get("claude_verdict")
        if claude is None:
            lines.append("    JUDGMENT (Claude): not run for this report.")
            continue
        if claude["validator"] == "reject":
            lines.append(
                f"    JUDGMENT (Claude, {claude['model']}): rejected by the validator "
                f"- {claude['validator_error']}"
            )
            continue
        lines.append(
            f"    JUDGMENT (Claude, {claude['model']}, retrieved {claude['retrieved_at']}): "
            f"{claude['verdict']}"
            + (f"  gate: {claude['gate_failed']}" if claude["gate_failed"] else "")
            + f"  confidence: {claude['confidence']}"
        )
        for cite in claude["justification"]:
            lines.append(
                f"      because {cite['resume_field']} vs posting."
                f"{cite['posting_field']} containing {cite['evidence']!r}"
            )
        if claude["verdict"] != rule["verdict"]:
            lines.append(
                "    DISAGREEMENT on the verdict. The agent does not resolve this; "
                "a human decides."
            )
        elif claude["gate_failed"] != rule["gate_failed"]:
            lines.append(
                "    Same verdict, different gate named. The agent does not resolve "
                "this either."
            )
    return "\n".join(lines)
