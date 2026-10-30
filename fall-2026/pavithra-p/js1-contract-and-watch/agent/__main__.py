"""Command line: `python3 -m agent watch` (live) or `python3 -m agent watch --from-file PATH` (SEEDED)."""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config, fetch, resume, watch


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m agent")
    commands = parser.add_subparsers(dest="command", required=True)
    w = commands.add_parser("watch", help="fetch the board, save the raw response, report new jobs")
    w.add_argument("--resume", default=str(config.RESUME), help="fictional résumé JSON")
    w.add_argument("--from-file", help="use a saved earlier response instead of fetching; the run is labelled SEEDED")
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        resume.load(args.resume)  # refuse a non-fictional résumé before any network call
        if args.from_file:
            raw = Path(args.from_file).read_bytes()
            source = f"saved response `{watch.rel(Path(args.from_file))}` (SEEDED, no fetch)"
            state_path, seeded = config.SEEDED_STATE, True
        else:
            raw = fetch.fetch(config.BOARD_URL)
            source = f"GET {config.BOARD_URL}"
            state_path, seeded = config.STATE, False
        result = watch.run_watch(raw, raw_dir=config.RAW_DIR, state_path=state_path, now=now, seeded=seeded)
    except (fetch.RefusedHost, resume.ResumeRefused) as e:
        print(e, file=sys.stderr)
        return 2
    except (watch.NotAJobList, OSError) as e:
        print(f"error: {e}; the state file was not changed", file=sys.stderr)
        return 1

    report = watch.format_report(result, source)
    config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = config.RUNS_DIR / f"run-{watch.stamp(now)}{'-SEEDED' if seeded else ''}.md"
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"(report saved to {watch.rel(report_path)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
