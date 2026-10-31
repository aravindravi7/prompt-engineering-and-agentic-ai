"""Sampling report: the same dev postings asked several times (experiments/LABELING-RULE.md).

Run from the project folder:
    python -m experiments.sample --prompt prompts/baseline.txt --repeats 4

Each call is a fresh messages.create request holding one user message, so no conversation
is shared between calls. No request sets temperature: the API default applies, and the
result files say so.

Writes experiments/results/sampling-<timestamp>.json and .md, and saves each raw reply
under experiments/results/replies/<that name>/<posting>-r<repeat>.json.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from agent import claude_judge
from agent.errors import AgentError
from agent.fetch import unique_path
from agent.run import display_path
from agent.timeutil import NEW_YORK, stamp
from agent.validator import VERDICTS

from .common import (LABELS_PATH, RAW_PATH, RESULTS_DIR, RUN_DATE, SELECTION_PATH, TEMPERATURE,
                     ExperimentError, check_labels, judge_once, load_labels, load_postings,
                     prepare, split_ids, yes_no)

SAMPLE_IDS = (8314283, 8160776, 8257892, 8128745, 7947546)
OUTCOMES = (*VERDICTS, "invalid")


def markdown(summary: dict) -> str:
    lines = [
        f"# Sampling report — `{summary['prompt_file']}`, {summary['repeats']} calls per posting",
        "",
        f"- Model requested: {summary['model_requested']}; named in responses: "
        f"{', '.join(summary['models_in_responses']) or 'none'}",
        f"- Temperature: {summary['temperature']}",
        f"- Prompt SHA-256: `{summary['prompt_sha256']}`",
        f"- Run date for R2: {summary['run_date']}; postings from `{summary['raw_source']}`",
        f"- Calls: {len(summary['calls'])}, each a fresh request with no shared conversation",
        f"- Run at: {summary['timestamp']}",
        "",
        "Claude verdicts are **model judgment**. \"All agree\" means every reply was valid and",
        "gave the same verdict.",
        "",
        "| Posting | My label | " + " | ".join(OUTCOMES) + " | All agree | Matches my label |",
        "|---|---|" + "---|" * len(OUTCOMES) + "---|---|",
    ]
    for p in summary["postings"]:
        counts = " | ".join(str(p["counts"][o]) for o in OUTCOMES)
        lines.append(f"| {p['posting_id']} | {p['my_label']} | {counts} | {p['all_agree']} "
                     f"| {p['matches_label']} / {summary['repeats']} |")
    lines += ["", "## Every call", "", "| Posting | Repeat | Verdict | Valid |", "|---|---|---|---|"]
    for c in summary["calls"]:
        lines.append(f"| {c['posting_id']} | {c['repeat']} | {c['claude_verdict'] or 'invalid'} | {c['valid']} |")
    return "\n".join(lines) + "\n"


def run_sampling(prompt_path: Path, repeats: int = 4, *, env=None,
                 client_factory=claude_judge.make_client, now: datetime | None = None,
                 config: dict | None = None, results_dir: Path = RESULTS_DIR,
                 labels_path: Path = LABELS_PATH, selection_path: Path = SELECTION_PATH,
                 raw_path: Path = RAW_PATH, ids=SAMPLE_IDS) -> dict:
    if repeats < 1:
        raise ExperimentError(f"--repeats must be at least 1, not {repeats}")
    now = now or datetime.now(NEW_YORK)
    dev = set(split_ids("dev", selection_path))
    if not set(ids) <= dev:
        raise ExperimentError(f"sampling postings must all be dev; not dev: {sorted(set(ids) - dev)}")
    labels = load_labels(labels_path)
    check_labels(ids, "dev", labels)
    postings = load_postings(ids, raw_path)
    setup = prepare(Path(prompt_path), env=env, client_factory=client_factory, config=config)

    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    json_path = unique_path(results_dir / f"sampling-{stamp(now)}.json")
    replies_dir = results_dir / "replies" / json_path.stem

    calls = []
    for pid in ids:
        for repeat in range(1, repeats + 1):
            result = judge_once(setup, postings[pid], replies_dir / f"{pid}-r{repeat}.json")
            calls.append({
                "posting_id": pid,
                "repeat": repeat,
                "claude_verdict": result["claude_verdict"],
                "valid": yes_no(result["claude_valid"]),
                "claude_model": result["claude_model"],
                "claude_invalid_reason": result["claude_invalid_reason"],
                "reply_path": result["claude_reply_path"],
            })

    per_posting = []
    for pid in ids:
        mine = [c for c in calls if c["posting_id"] == pid]
        outcomes = [c["claude_verdict"] if c["valid"] == "yes" else "invalid" for c in mine]
        per_posting.append({
            "posting_id": pid,
            "my_label": labels[pid]["label"],
            "counts": {o: outcomes.count(o) for o in OUTCOMES},
            "all_agree": yes_no(len(set(outcomes)) == 1 and outcomes[0] != "invalid"),
            "matches_label": outcomes.count(labels[pid]["label"]),
        })

    summary = {
        "prompt_file": setup.prompt_display,
        "prompt_sha256": setup.prompt_sha256,
        "repeats": repeats,
        "run_date": RUN_DATE.isoformat(),
        "timestamp": now.isoformat(timespec="seconds"),
        "model_requested": setup.config["model"],
        "models_in_responses": sorted({c["claude_model"] for c in calls if c["claude_model"]}),
        "temperature": TEMPERATURE,
        "raw_source": display_path(raw_path),
        "labels_source": display_path(labels_path),
        "all_agree_means": "every reply valid and the same verdict",
        "claude_label": claude_judge.CLAUDE_LABEL,
        "postings": per_posting,
        "calls": calls,
    }
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(markdown(summary), encoding="utf-8")
    summary["output_json"] = display_path(json_path)
    summary["output_markdown"] = display_path(md_path)
    return summary


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m experiments.sample",
                                     description="Ask the same dev postings several times in fresh calls.")
    parser.add_argument("--prompt", type=Path, required=True, metavar="FILE", help="system prompt file")
    parser.add_argument("--repeats", type=int, default=4, help="calls per posting (default 4)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        summary = run_sampling(args.prompt, args.repeats)
    except AgentError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    for p in summary["postings"]:
        print(f"{p['posting_id']}  label {p['my_label']:12s}  all agree: {p['all_agree']:3s}  "
              + ", ".join(f"{o} {n}" for o, n in p["counts"].items() if n))
    print(f"model {summary['model_requested']}, temperature {summary['temperature']}")
    print(f"output: {summary['output_json']}, {summary['output_markdown']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
