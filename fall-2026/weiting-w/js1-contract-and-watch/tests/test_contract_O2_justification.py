"""CONTRACT.md O2 and wrong versions W2 / W2b."""

from __future__ import annotations

import pytest

from jobagent.errors import ValidatorRejected
from jobagent.validator import check_citation
from tests import wrong_versions as wrong


def check_justifications(entries, postings, resume):
    by_id = {p["id"]: p for p in postings}
    for entry in entries:
        justification = entry["rule_verdict"]["justification"]
        assert justification, f"O2: posting {entry['posting_id']} justified nothing"
        posting = by_id[entry["posting_id"]]
        for i, cite in enumerate(justification):
            check_citation(cite, posting, resume, where=f"entry[{entry['posting_id']}][{i}]")


def test_real_implementation_justifies_every_verdict(constructed, persona):
    check_justifications(wrong.build_entries_correct(constructed, persona), constructed, persona)


def test_relevant_verdict_cites_all_four_gates(constructed, persona):
    entries = wrong.build_entries_correct(constructed, persona)
    relevant = [e for e in entries if e["rule_verdict"]["verdict"] == "relevant"]
    assert relevant, "the constructed fixtures must include at least one relevant posting"
    for entry in relevant:
        assert len(entry["rule_verdict"]["justification"]) == 4


def test_catches_W2_empty_justification(constructed, persona):
    entries = wrong.build_entries_W2(constructed, persona)
    with pytest.raises(AssertionError):
        check_justifications(entries, constructed, persona)


def test_catches_W2b_citing_a_field_that_is_not_there(constructed, persona):
    entries = wrong.build_entries_W2b(constructed, persona)
    with pytest.raises(ValidatorRejected):
        check_justifications(entries, constructed, persona)


def test_W2_verdicts_are_all_correct_so_verdict_tests_cannot_catch_it(constructed, persona):
    right = wrong.build_entries_correct(constructed, persona)
    bad = wrong.build_entries_W2(constructed, persona)
    assert [e["rule_verdict"]["verdict"] for e in right] == [
        e["rule_verdict"]["verdict"] for e in bad
    ]
