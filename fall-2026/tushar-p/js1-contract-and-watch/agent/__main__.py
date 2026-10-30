"""CLI: python -m agent [--from-raw FILE] [--no-claude] [--run-date YYYY-MM-DD] [--state FILE]"""

import argparse
import sys
from datetime import date
from pathlib import Path

from .config import load_config
from .errors import AgentError
from .run import RunOptions, run
from .timeutil import today


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m agent", description="Job-Search Agent 1 (see CONTRACT.md).")
    parser.add_argument("--from-raw", type=Path, metavar="FILE",
                        help="run against a saved board response, with no network call (a seeded run)")
    parser.add_argument("--no-claude", action="store_true", help="run the rule judge only")
    parser.add_argument("--run-date", type=date.fromisoformat, metavar="YYYY-MM-DD",
                        help="run date for R2 (default: today in America/New_York)")
    parser.add_argument("--state", type=Path, metavar="FILE",
                        help="state file of seen ids (default: state/seen_ids.json)")
    parser.add_argument("--config", type=Path, metavar="FILE", help="config file (default: config.json)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        if args.state:
            config["state_path"] = args.state.resolve()
        summary = run(RunOptions(
            config=config,
            run_date=args.run_date or today(),
            from_raw=args.from_raw,
            no_claude=args.no_claude,
        ))
    except AgentError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    print(f"{summary['mode']} run, run date {summary['run_date']}"
          f"{' (baseline)' if summary['baseline'] else ''}")
    print(f"postings fetched: {summary['postings_fetched']}, new: {summary['new_count']}")
    print(f"raw response: {summary['raw_path']}")
    print(f"output: {summary['output_json']}, {summary['output_markdown']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
