"""One agent run: persona check, fetch or seed, diff, judge new postings, write outputs, then state."""

import json
import os
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from . import PROJECT_DIR, claude_judge, report, rules, state
from .allowlist import check_url
from .errors import ConfigError, RawInputError
from .fetch import fetch_board
from .persona import load_rule_fields
from .text import strip_html
from .timeutil import NEW_YORK, stamp


@dataclass
class RunOptions:
    config: dict
    run_date: date
    from_raw: Path | None = None
    no_claude: bool = False


def display_path(path: Path) -> str:
    """Path relative to the project folder when possible, so outputs carry no home directory."""
    path = Path(path).resolve()
    try:
        return str(path.relative_to(PROJECT_DIR))
    except ValueError:
        return str(path)


def parse_board(body: bytes, source: str) -> list[dict]:
    """The jobs list, refusing a response that cannot drive R4–R6."""
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        raise RawInputError(f"{source} is not JSON: {err}") from None
    jobs = data.get("jobs") if isinstance(data, dict) else None
    if not isinstance(jobs, list):
        raise RawInputError(f"{source} has no 'jobs' list")
    for job in jobs:
        if not isinstance(job, dict) or not isinstance(job.get("id"), int) or isinstance(job.get("id"), bool):
            raise RawInputError(f"{source} has a posting without an integer id")
        if not isinstance(job.get("content"), str):
            raise RawInputError(
                f"{source} has no posting content (posting {job['id']}); it was probably fetched "
                f"without content=true, so R4–R6 cannot be applied"
            )
    return jobs


def _skipped_claude() -> dict:
    return {
        "claude_verdict": None,
        "claude_justification": None,
        "claude_valid": None,
        "claude_model": None,
        "claude_invalid_reason": None,
        "claude_reply_path": None,
        "claude_label": claude_judge.CLAUDE_LABEL,
    }


def run(options: RunOptions, *, env=None, opener=None,
        client_factory=claude_judge.make_client, now: datetime | None = None) -> dict:
    """Run once and return the summary that was written to out/."""
    config = options.config
    env = os.environ if env is None else env
    now = now or datetime.now(NEW_YORK)

    # Everything that can stop the run happens before any network call.
    fields = load_rule_fields(config["persona_path"])
    api_key = system_prompt = None
    if not options.no_claude:
        api_key = env.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ConfigError("ANTHROPIC_API_KEY is not set; export it in your shell or pass --no-claude")
        check_url(config["claude_base_url"])
        system_prompt, _ = claude_judge.load_prompt()
    seen = state.load_seen(config["state_path"])

    if options.from_raw:
        mode = "seeded"
        raw_path = Path(options.from_raw)
        try:
            body = raw_path.read_bytes()
        except OSError as err:
            raise RawInputError(f"cannot read {raw_path}: {err}") from None
    else:
        mode = "live"
        body, raw_path = fetch_board(config["board_url"], Path(config["raw_dir"]), opener=opener, now=now)
    jobs = parse_board(body, display_path(raw_path))

    board_ids = [job["id"] for job in jobs]
    fresh = set(state.new_ids(board_ids, seen))
    out_dir = Path(config["out_dir"])
    run_id = f"run-{stamp(now)}"
    n = 2
    while (out_dir / f"{run_id}.json").exists():
        run_id = f"run-{stamp(now)}-{n}"
        n += 1

    client = None
    if fresh and not options.no_claude:
        client = client_factory(api_key, config["claude_base_url"])

    records, reported = [], set()
    for job in jobs:
        if job["id"] not in fresh or job["id"] in reported:
            continue
        reported.add(job["id"])
        used = rules.date_used(job)
        record = {
            "posting_id": job["id"],
            "title": job.get("title"),
            "url": job.get("absolute_url"),
            "location": (job.get("location") or {}).get("name"),
            "date_used": {"field": used["field"], "value": used["value"]} if used else None,
            **rules.judge(job, fields, options.run_date),
            "rule_label": rules.RULE_LABEL,
        }
        if client is None:
            record.update(_skipped_claude())
        else:
            request = claude_judge.build_request(
                job, strip_html(job.get("content")), fields, options.run_date,
                config["model"], config["max_tokens"], system_prompt,
            )
            reply_path = out_dir / "claude-replies" / run_id / f"{job['id']}.json"
            # A 401 raises ClaudeAuthError here: no out/ files and no state are written.
            record.update(claude_judge.judge(client, request, job["id"], reply_path))
            record["claude_reply_path"] = display_path(reply_path)
        records.append(record)

    summary = {
        "run_id": run_id,
        "run_date": options.run_date.isoformat(),
        "mode": mode,
        "baseline": seen is None,
        "postings_fetched": len(jobs),
        "new_count": len(records),
        "raw_path": display_path(raw_path),
        "state_path": display_path(config["state_path"]),
        "claude": "off (--no-claude)" if options.no_claude else f"on, model {config['model']}",
        "labels": {"rule_verdict": rules.RULE_LABEL, "claude_verdict": claude_judge.CLAUDE_LABEL},
        "records": records,
    }
    json_path, md_path = report.write(out_dir, run_id, summary)
    summary["output_json"] = display_path(json_path)
    summary["output_markdown"] = display_path(md_path)

    # State last: if anything above failed, these postings stay new for the next run.
    state.save_seen(config["state_path"], seen, board_ids)
    return summary
