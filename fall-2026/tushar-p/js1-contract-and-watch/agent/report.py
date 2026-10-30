"""Per-run output: one JSON file and one short Markdown summary in out/."""

import json
from pathlib import Path

from .fetch import unique_path


def _cell(value) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def _claude_cell(record: dict) -> str:
    if record.get("claude_valid") is None:
        return "skipped"
    if not record["claude_valid"]:
        return "invalid"
    return record["claude_verdict"]


def _checks_cell(record: dict) -> str:
    flagged = [f"{e['check']} {e['result']}" for e in record["rule_justification"] if e["result"] != "pass"]
    return ", ".join(flagged) or "all pass"


def markdown(summary: dict) -> str:
    lines = [
        f"# Job-Search Agent 1 — {summary['run_date']} ({summary['mode']})",
        "",
        f"- Run date: {summary['run_date']}",
        f"- Mode: {summary['mode']}",
        f"- Baseline: {'yes, every id recorded and 0 reported as new' if summary['baseline'] else 'no'}",
        f"- Postings fetched: {summary['postings_fetched']}",
        f"- New postings: {summary['new_count']}",
        f"- Raw response: `{summary['raw_path']}`",
        f"- State file: `{summary['state_path']}`",
        f"- Claude judge: {summary['claude']}",
        "",
        "Rule verdicts are a **record**: anyone can recompute them from the raw response.",
        "Claude verdicts are **model judgment**, not fact.",
    ]
    if summary["records"]:
        lines += [
            "",
            "| Posting | Title | Location | Rule verdict (record) | Not passed | Claude verdict (model judgment) |",
            "|---|---|---|---|---|---|",
        ]
        for r in summary["records"]:
            lines.append(
                f"| [{r['posting_id']}]({r['url']}) | {_cell(r['title'])} | {_cell(r['location'])} "
                f"| {r['rule_verdict']} | {_checks_cell(r)} | {_claude_cell(r)} |"
            )
    return "\n".join(lines) + "\n"


def write(out_dir: Path, run_id: str, summary: dict) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = unique_path(out_dir / f"{run_id}.json")
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(markdown(summary), encoding="utf-8")
    return json_path, md_path
