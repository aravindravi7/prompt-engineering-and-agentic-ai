"""The plausible-but-wrong implementations from CONTRACT.md §5.

These are real code, not descriptions of code. The contract tests are run
against them as well as against the real implementation, and a test that passes
on one of these is a test that proves nothing.
"""

from __future__ import annotations

from jobagent import rule as rule_judge
from jobagent import state as state_mod


def build_entries_correct(postings, resume):
    """What the agent actually does: the entry is built inside the loop."""
    entries = []
    for posting in postings:
        entries.append(
            {
                "posting_id": posting["id"],
                "title": posting.get("title"),
                "rule_verdict": rule_judge.judge(posting, resume),
            }
        )
    return entries


def build_entries_W1(postings, resume):
    """W1 - labels paired with the wrong postings.

    Plausible because sorting for a tidy report and then zipping the verdicts
    back onto the original list by index is the obvious way to write it. Every
    verdict here is correctly computed. Every count is right. Each one is
    attached to the wrong job.
    """
    ordered = sorted(postings, key=lambda p: (p.get("title") or ""))
    verdicts = [rule_judge.judge(p, resume) for p in ordered]
    entries = []
    for posting, verdict in zip(postings, verdicts):
        entries.append(
            {
                "posting_id": posting["id"],
                "title": posting.get("title"),
                "rule_verdict": verdict,
            }
        )
    return entries


def build_entries_W2(postings, resume):
    """W2 - a justification that cites nothing. The verdicts are all correct."""
    entries = build_entries_correct(postings, resume)
    for entry in entries:
        entry["rule_verdict"] = {**entry["rule_verdict"], "justification": []}
    return entries


def build_entries_W2b(postings, resume):
    """W2b - a justification that cites a field that is not in the documents.

    The field paths look right: ``skills[0]`` is the sort of thing a resume has,
    and ``content`` is the sort of thing a posting has. Neither is in the
    documents this agent actually loaded, which is the point.
    """
    entries = build_entries_correct(postings, resume)
    for entry in entries:
        entry["rule_verdict"] = {
            **entry["rule_verdict"],
            "justification": [
                {
                    "resume_field": "skills[0]",
                    "resume_value": "python",
                    "posting_field": "content",
                    "evidence": "python",
                }
            ],
        }
    return entries


def watch_W3_eager_state(state_path, board_token, host, postings, report_fn):
    """W3 - writes the seen-ids state before the verdicts exist.

    If ``report_fn`` raises, these postings are already recorded as seen and the
    next run reports nothing new. The postings are gone, quietly.
    """
    state, _ = state_mod.load(state_path, board_token, host)
    state_mod.save(state_path, state, postings)
    return report_fn(postings)


def watch_correct_state_last(state_path, board_token, host, postings, report_fn):
    """What the agent actually does: the state is written after the report."""
    state, _ = state_mod.load(state_path, board_token, host)
    result = report_fn(postings)
    state_mod.save(state_path, state, postings)
    return result
