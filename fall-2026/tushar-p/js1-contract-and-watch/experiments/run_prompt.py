"""Score one prompt file against my hand labels on one split (experiments/LABELING-RULE.md).

Run from the project folder:
    python -m experiments.run_prompt --prompt prompts/<file>.txt --split dev
    python -m experiments.run_prompt --prompt prompts/<file>.txt --split held-out --final

A pass is an exact match between Claude's verdict and my label; an invalid reply is a miss.
Held-out is refused without --final, and every held-out run, finished or stopped, gets a
row in experiments/results/HELDOUT-LOG.md.

Writes experiments/results/<prompt>-<split>-<timestamp>.json and .md, and saves each raw
reply under experiments/results/replies/<that name>/.
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

from .common import (LABELS_PATH, RAW_PATH, RESULTS_DIR, RUN_DATE, SELECTION_PATH, SPLIT_KEYS,
                     TEMPERATURE, ExperimentError, check_labels, judge_once, load_labels,
                     load_postings, prepare, split_ids, yes_no)

HELDOUT_LOG = "HELDOUT-LOG.md"
HELDOUT_LOG_HEADER = """\
# Held-out runs

Every run of `experiments/run_prompt.py` on the held-out split, appended by the script,
including runs that stopped early. LABELING-RULE.md: held-out is run last, once per prompt.

| Timestamp (America/New_York) | Prompt file | Prompt SHA-256 | Model | Outcome |
|---|---|---|---|---|
"""


def log_heldout(results_dir: Path, moment: datetime, prompt_display: str, prompt_sha256: str,
                model: str, outcome: str) -> Path:
    path = Path(results_dir) / HELDOUT_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(HELDOUT_LOG_HEADER, encoding="utf-8")
    row = (f"| {moment.astimezone(NEW_YORK).isoformat(timespec='seconds')} | `{prompt_display}` "
           f"| `{prompt_sha256}` | {model} | {outcome.replace('|', '/')} |\n")
    with path.open("a", encoding="utf-8") as f:
        f.write(row)
    return path


def markdown(summary: dict) -> str:
    lines = [
        f"# Prompt run — `{summary['prompt_file']}` on {summary['split']}",
        "",
        f"- Passes: **{summary['passes']} / {summary['total']}**",
        f"- Invalid replies: {summary['invalid_count']} (each counted as a miss)",
        f"- Model requested: {summary['model_requested']}; named in responses: "
        f"{', '.join(summary['models_in_responses']) or 'none'}",
        f"- Temperature: {summary['temperature']}",
        f"- Prompt file: `{summary['prompt_file']}`",
        f"- Prompt SHA-256: `{summary['prompt_sha256']}`",
        f"- Run date for R2: {summary['run_date']} (the date the labels used)",
        f"- Postings from: `{summary['raw_source']}`; labels from `{summary['labels_source']}`",
        f"- Run at: {summary['timestamp']}",
        "",
        "Claude verdicts are **model judgment**. My labels are hand labels. A pass is an exact",
        "match; `cannot_tell` against `relevant` is a miss. With 10 cases, a difference of one",
        "or two may be noise.",
        "",
        "| Posting | My label | Claude verdict | Match | Valid |",
        "|---|---|---|---|---|",
    ]
    for row in summary["rows"]:
        lines.append(f"| {row['posting_id']} | {row['my_label']} | {row['claude_verdict'] or 'invalid'} "
                     f"| {row['match']} | {row['valid']} |")
    return "\n".join(lines) + "\n"


def run_experiment(prompt_path: Path, split: str, *, final: bool = False, env=None,
                   client_factory=claude_judge.make_client, now: datetime | None = None,
                   config: dict | None = None, results_dir: Path = RESULTS_DIR,
                   labels_path: Path = LABELS_PATH, selection_path: Path = SELECTION_PATH,
                   raw_path: Path = RAW_PATH) -> dict:
    if split not in SPLIT_KEYS:
        raise ExperimentError(f"split must be one of {sorted(SPLIT_KEYS)}, not {split!r}")
    if split == "held-out" and not final:
        raise ExperimentError("--split held-out is refused without --final: held-out is run last, "
                              "once per prompt, after the change was chosen on dev")
    now = now or datetime.now(NEW_YORK)
    ids = split_ids(split, selection_path)
    labels = load_labels(labels_path)
    check_labels(ids, split, labels)
    postings = load_postings(ids, raw_path)
    setup = prepare(Path(prompt_path), env=env, client_factory=client_factory, config=config)

    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    json_path = unique_path(results_dir / f"{Path(prompt_path).stem}-{split}-{stamp(now)}.json")
    run_name = json_path.stem
    model = setup.config["model"]

    if split == "held-out":
        log_path = results_dir / HELDOUT_LOG
        if log_path.exists() and setup.prompt_sha256 in log_path.read_text(encoding="utf-8"):
            print(f"note: this prompt's SHA-256 is already in {display_path(log_path)}; "
                  f"this held-out run is logged too", file=sys.stderr)

    outcome = "stopped before finishing"
    try:
        rows = []
        for pid in ids:
            result = judge_once(setup, postings[pid], results_dir / "replies" / run_name / f"{pid}.json")
            valid = bool(result["claude_valid"])
            rows.append({
                "posting_id": pid,
                "my_label": labels[pid]["label"],
                "claude_verdict": result["claude_verdict"],
                "match": yes_no(valid and result["claude_verdict"] == labels[pid]["label"]),
                "valid": yes_no(valid),
                "claude_model": result["claude_model"],
                "claude_invalid_reason": result["claude_invalid_reason"],
                "reply_path": result["claude_reply_path"],
            })

        summary = {
            "prompt_file": setup.prompt_display,
            "prompt_sha256": setup.prompt_sha256,
            "split": split,
            "final": final,
            "run_date": RUN_DATE.isoformat(),
            "timestamp": now.isoformat(timespec="seconds"),
            "model_requested": model,
            "models_in_responses": sorted({r["claude_model"] for r in rows if r["claude_model"]}),
            "temperature": TEMPERATURE,
            "raw_source": display_path(raw_path),
            "labels_source": display_path(labels_path),
            "scoring": "pass = Claude's verdict exactly equals my label; an invalid reply is a miss",
            "claude_label": claude_judge.CLAUDE_LABEL,
            "passes": sum(r["match"] == "yes" for r in rows),
            "total": len(rows),
            "invalid_count": sum(r["valid"] == "no" for r in rows),
            "rows": rows,
        }
        md_path = json_path.with_suffix(".md")
        json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        md_path.write_text(markdown(summary), encoding="utf-8")
        summary["output_json"] = display_path(json_path)
        summary["output_markdown"] = display_path(md_path)
        outcome = (f"{summary['passes']}/{summary['total']} passes, {summary['invalid_count']} invalid; "
                   f"`{summary['output_json']}`")
        return summary
    except BaseException as err:
        outcome = f"stopped: {type(err).__name__}: {err}"
        raise
    finally:
        if split == "held-out":
            log_heldout(results_dir, now, setup.prompt_display, setup.prompt_sha256, model, outcome)


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m experiments.run_prompt",
                                     description="Score one prompt file against the hand labels.")
    parser.add_argument("--prompt", type=Path, required=True, metavar="FILE", help="system prompt file")
    parser.add_argument("--split", required=True, choices=sorted(SPLIT_KEYS))
    parser.add_argument("--final", action="store_true", help="required for --split held-out")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        summary = run_experiment(args.prompt, args.split, final=args.final)
    except AgentError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(f"{summary['prompt_file']} on {summary['split']}: {summary['passes']}/{summary['total']} passes, "
          f"{summary['invalid_count']} invalid (model {summary['model_requested']})")
    print(f"prompt SHA-256: {summary['prompt_sha256']}")
    print(f"output: {summary['output_json']}, {summary['output_markdown']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
