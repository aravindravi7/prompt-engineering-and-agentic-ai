"""CONTRACT.md O1 and wrong version W1.

The property under test is not "the verdicts are correct" - W1's verdicts are
all correct. It is "each verdict is attached to the posting it is about", and
the only way to check that from the output alone is to require that the
evidence a verdict quotes really occurs in the posting the verdict is keyed to.
"""

from __future__ import annotations

import pytest

from jobagent.errors import ValidatorRejected
from jobagent.validator import check_citation
from tests import wrong_versions as wrong


def check_pairing(entries, postings, resume):
    by_id = {p["id"]: p for p in postings}
    assert len(entries) == len(postings), "O1: one entry per posting"
    assert [e["posting_id"] for e in entries] == [p["id"] for p in postings]
    for entry in entries:
        posting = by_id[entry["posting_id"]]
        for i, cite in enumerate(entry["rule_verdict"]["justification"]):
            check_citation(cite, posting, resume, where=f"entry[{entry['posting_id']}][{i}]")


def test_real_implementation_pairs_each_verdict_with_its_own_posting(constructed, persona):
    entries = wrong.build_entries_correct(constructed, persona)
    check_pairing(entries, constructed, persona)


def test_the_same_check_catches_W1(constructed, persona):
    entries = wrong.build_entries_W1(constructed, persona)
    with pytest.raises((ValidatorRejected, AssertionError)):
        check_pairing(entries, constructed, persona)


def test_W1_verdict_counts_are_identical_so_counts_cannot_catch_it(constructed, persona):
    """Why a count-based test would not have caught W1."""
    right = wrong.build_entries_correct(constructed, persona)
    bad = wrong.build_entries_W1(constructed, persona)
    tally = lambda entries: sorted(e["rule_verdict"]["verdict"] for e in entries)
    assert tally(right) == tally(bad)
    assert [e["rule_verdict"]["verdict"] for e in right] != [
        e["rule_verdict"]["verdict"] for e in bad
    ], "if this ever becomes equal, the constructed fixtures no longer exercise W1"
