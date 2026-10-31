"""Command line for the watch.

Every command either fetches live from the one allow-listed host, or replays a
response that is already on disk. Replay is a first-class mode rather than a
test hook, because CONTRACT.md O5 promises that any verdict in this repository
can be recomputed from evidence without a network.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from . import claude_judge, fetch, report, resume as resume_mod, rule as rule_judge, state as state_mod
from .errors import Refusal

DEFAULT_BOARD = "config/board.json"
DEFAULT_RESUME = "data/resume.persona.json"
DEFAULT_STATE = "evidence/state/seen.json"
DEFAULT_RAW_DIR = "evidence/raw"
DEFAULT_RUNS_DIR = "evidence/runs"


def _load_board(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _raw_info_for_replay(path, label):
    raw = Path(path).read_bytes()
    return raw, {
        "path": str(path),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "source": "replay",
        "source_label": label,
    }


def cmd_watch(args) -> int:
    board = _load_board(args.board)
    resume = resume_mod.load(args.resume)
    url = fetch.board_url(board["host"], board["board_token"], board["path_template"])

    if args.from_raw:
        raw, raw_info = _raw_info_for_replay(args.from_raw, args.source_label)
        status = None
    else:
        raw, status = fetch.fetch_raw(url)
        raw_info = fetch.save_raw(raw, args.raw_dir, board["board_token"])
        raw_info["source"] = "live"
        raw_info["source_label"] = args.source_label or "live fetch"

    postings = fetch.parse_postings(raw)

    state, is_baseline = state_mod.load(args.state, board["board_token"], board["host"])
    state_before_sha = fetch.sha256_of_file(args.state)
    new = state_mod.new_postings(postings, state)

    transcript = claude_judge.load_transcript(args.transcript) if args.transcript else None

    entries = []
    if not is_baseline:
        for posting in new:
            claude_verdict = None
            if transcript is not None:
                rows = transcript.get(str(posting["id"]))
                if rows:
                    claude_verdict = claude_judge.from_transcript(rows[0], posting, resume)
            elif args.ask_claude:
                prompt = claude_judge.render_prompt(args.prompt, posting, resume)
                raw_text = claude_judge.call_model(prompt, model=args.model)
                claude_verdict = claude_judge.wrap(
                    raw_text,
                    posting,
                    resume,
                    model=args.model,
                    retrieved_at=report.utc_now(),
                    prompt_contract=str(args.prompt),
                    transport="anthropic-messages-api",
                )
            entry = report.entry_for(posting, resume, claude_verdict)
            report.self_check(entry, posting, resume)
            entries.append(entry)

    # State is written only now, after every verdict exists and has passed the
    # contract self-check. See CONTRACT.md W3.
    if args.dry_run:
        state_after_sha = state_before_sha
    else:
        state_mod.save(args.state, state, postings)
        state_after_sha = fetch.sha256_of_file(args.state)

    run = report.build(
        url=url,
        status=status,
        raw_info=raw_info,
        postings=postings,
        new=new,
        state_before_sha=state_before_sha,
        state_after_sha=state_after_sha,
        state_path=args.state,
        is_baseline=is_baseline,
        resume=resume,
        entries=entries,
        board=board,
        resume_summary=resume_mod.public_summary(resume),
    )
    out = report.write(run, args.runs_dir)
    print(report.human_summary(run))
    print(f"\n  run report: {out}")
    return 0


def cmd_rule(args) -> int:
    """Rule verdicts for every posting in a saved response.

    Used to build the hand-labelling worksheets and the experiment inputs, and
    to let a TA recompute any verdict in this repository offline.
    """
    resume = resume_mod.load(args.resume)
    postings = fetch.parse_postings(Path(args.from_raw).read_bytes())
    if args.posting_id is not None:
        postings = [p for p in postings if p["id"] == args.posting_id]
        if not postings:
            print(f"no posting with id {args.posting_id}", file=sys.stderr)
            return 1
    rows = []
    for posting in postings:
        verdict = rule_judge.judge(posting, resume)
        rows.append(
            {
                "posting_id": posting["id"],
                "title": posting.get("title"),
                "location": (posting.get("location") or {}).get("name"),
                "departments": [d.get("name") for d in posting.get("departments") or []],
                "rule_verdict": verdict,
            }
        )
    print(json.dumps({"rule_version": rule_judge.RULE_VERSION, "rows": rows},
                     indent=2, ensure_ascii=False))
    return 0


def cmd_prompt(args) -> int:
    """Print the rendered prompt for one posting, so it can be pasted or logged."""
    resume = resume_mod.load(args.resume)
    postings = fetch.parse_postings(Path(args.from_raw).read_bytes())
    match = [p for p in postings if p["id"] == args.posting_id]
    if not match:
        print(f"no posting with id {args.posting_id}", file=sys.stderr)
        return 1
    print(claude_judge.render_prompt(args.prompt, match[0], resume), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m jobagent",
        description="Job-Search Agent 1: one board, one persona resume, new postings only.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--board", default=DEFAULT_BOARD)
        p.add_argument("--resume", default=DEFAULT_RESUME)

    watch = sub.add_parser("watch", help="fetch (or replay) the board and report new postings")
    common(watch)
    watch.add_argument("--state", default=DEFAULT_STATE)
    watch.add_argument("--raw-dir", default=DEFAULT_RAW_DIR)
    watch.add_argument("--runs-dir", default=DEFAULT_RUNS_DIR)
    watch.add_argument(
        "--from-raw",
        help="replay a saved raw response instead of fetching (no network)",
    )
    watch.add_argument(
        "--source-label",
        default=None,
        help="label recorded in the run report, e.g. 'SEEDED: earlier snapshot'",
    )
    watch.add_argument("--transcript", help="recorded Claude judgments to attach")
    watch.add_argument("--ask-claude", action="store_true", help="call the model API live")
    watch.add_argument("--prompt", default="experiments/prompts/baseline.txt")
    watch.add_argument("--model", default=claude_judge.DEFAULT_MODEL)
    watch.add_argument("--dry-run", action="store_true", help="do not write the state file")
    watch.set_defaults(func=cmd_watch)

    ruler = sub.add_parser("rule", help="rule verdicts for a saved response, offline")
    common(ruler)
    ruler.add_argument("--from-raw", required=True)
    ruler.add_argument("--posting-id", type=int)
    ruler.set_defaults(func=cmd_rule)

    prompter = sub.add_parser("prompt", help="print the rendered prompt for one posting")
    common(prompter)
    prompter.add_argument("--from-raw", required=True)
    prompter.add_argument("--posting-id", type=int, required=True)
    prompter.add_argument("--prompt", default="experiments/prompts/baseline.txt")
    prompter.set_defaults(func=cmd_prompt)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Refusal as exc:
        print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return exc.exit_code
