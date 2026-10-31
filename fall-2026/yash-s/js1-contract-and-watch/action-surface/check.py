#!/usr/bin/env python3
"""Check what the three action surfaces returned. Offline; asks nobody.

Each answer goes through the same validator and pass definition as the judge. For the agent
surface (c), the state file it wrote is compared with the ids in the watcher's latest saved
response. That response was fetched at a different time, so small differences may be real
board changes.

usage (from the js1-contract-and-watch folder), after running the three surfaces:
  python3 action-surface/check.py
writes action-surface/CHECK.md
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER / "experiment"))
import harness as h  # noqa: E402
from make_inputs import POSTING_ID  # noqa: E402

WATCHER_RAW = FOLDER / "runs" / "raw-databricks-2026-10-31T061834Z.json"


def judged(text, view, label):
    if text is None:
        return "not run", []
    answer, errors = h.judge.validate(text, {"id": POSTING_ID}, view)
    if errors:
        return "invalid (fail)", errors
    return f"{answer['verdict']} ({'pass' if answer['verdict'] == label else 'FAIL'})", []


def envelope(path):
    if not path.exists():
        return None, {}
    out = json.loads(path.read_text(encoding="utf-8"))
    return out.get("result"), {"num_turns": out.get("num_turns"), "models": sorted((out.get("modelUsage") or {})),
                               "permission_denials": out.get("permission_denials"), "is_error": out.get("is_error"),
                               "web_fetch_requests": (out.get("usage") or {}).get("server_tool_use")}


def main():
    sel = h.load_selection()
    view = h.judge.claude_view(h.load_postings(sel)[POSTING_ID], h.load_resume())
    label = h.load_labels()[POSTING_ID]["label"]
    a_path = HERE / "a-chat-reply.txt"
    a_text = a_path.read_text(encoding="utf-8").strip() if a_path.exists() else None
    b_text, b_meta = envelope(HERE / "b-file-read.json")
    c_text, c_meta = envelope(HERE / "c-agent.json")
    lines = [f"# Action-surface check: posting {POSTING_ID}", "",
             f"My label: **{label}**. {h.PASS_DEFINITION}.", "",
             "| surface | answer under the validator | details |", "|---|---|---|"]
    for name, text, meta in (("a. pasted into a chat", a_text, {}), ("b. Claude reads a file", b_text, b_meta),
                             ("c. agent fetches and writes", c_text, c_meta)):
        verdict, errors = judged(text, view, label)
        detail = "; ".join(errors) if errors else ", ".join(f"{k}: {v}" for k, v in meta.items()) or "-"
        lines.append(f"| {name} | {verdict} | {detail} |")
    state_path = HERE / "c-agent-state.json"
    lines += ["", "## The agent's state file", ""]
    if not state_path.exists():
        lines.append("The agent wrote no `state.json`.")
    else:
        try:
            ids = json.loads(state_path.read_text(encoding="utf-8"))
            ok = isinstance(ids, list) and all(type(i) is int for i in ids)
        except ValueError:
            ids, ok = None, False
        if not ok:
            lines.append("`state.json` is not a JSON list of integer ids.")
        else:
            watcher = {j["id"] for j in json.loads(WATCHER_RAW.read_bytes())["jobs"]}
            agent = set(ids)
            lines += [f"- Ids in the agent's file: {len(ids)} ({len(agent)} unique)",
                      f"- Ids in the watcher's saved response `{WATCHER_RAW.name}`: {len(watcher)}",
                      f"- In both: {len(agent & watcher)}; only in the agent's file: {len(agent - watcher)}; "
                      f"only in the watcher's response: {len(watcher - agent)}"]
    path = HERE / "CHECK.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
