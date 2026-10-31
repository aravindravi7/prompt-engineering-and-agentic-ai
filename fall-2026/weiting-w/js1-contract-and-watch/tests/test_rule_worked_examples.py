"""The worked-examples table in CONTRACT.md §4.1, as a test.

If this test and the table ever disagree, one of them is wrong and the contract
is the specification.
"""

from __future__ import annotations

import pytest

from jobagent import rule as rule_judge
from jobagent.fieldpath import whole_word
from tests.conftest import EXPECTED, posting


@pytest.mark.parametrize("pid", sorted(EXPECTED))
def test_contract_table(pid, constructed, persona):
    match = [p for p in constructed if p["id"] == pid][0]
    verdict = rule_judge.judge(match, persona)
    assert (verdict["verdict"], verdict["gate_failed"]) == EXPECTED[pid]


def test_gate_order_is_first_failure_wins(persona):
    """A posting that fails G1 and G3 must report G1."""
    both = posting(2001, "Senior Client Partner", "Client Partner", "Dublin, Ireland")
    verdict = rule_judge.judge(both, persona)
    assert verdict["gate_failed"] == "G1_title_block"


def test_relevant_implies_gate_failed_is_none(constructed, persona):
    for p in constructed:
        verdict = rule_judge.judge(p, persona)
        assert (verdict["gate_failed"] is None) == (verdict["verdict"] == "relevant")


def test_rule_is_a_record_not_a_judgment(constructed, persona):
    for p in constructed:
        a = rule_judge.judge(p, persona)
        b = rule_judge.judge(p, persona)
        assert a == b
        assert a["kind"] == "record"


def test_whole_word_boundaries_from_the_contract():
    assert not whole_word("sr", "sre, platform")
    assert whole_word("sr", "sr. software engineer")
    assert not whole_word("lead", "engineering leadership program")
    assert whole_word("lead", "tech lead, core")
    assert not whole_word("head", "headcount analyst")


def test_known_false_positive_remote_netherlands_is_admitted(persona):
    """CONTRACT.md §4.2 item 3, pre-registered as a known false positive.

    This test exists to pin the behaviour the contract admits to, so that a
    later version changing it is a deliberate rule bump and not a silent fix.
    """
    p = posting(2002, "Software Engineer, Core", "Software Engineering", "Remote - The Netherlands")
    assert rule_judge.judge(p, persona)["verdict"] == "relevant"


def test_substring_job_family_admits_the_specialized_families(persona):
    """CONTRACT.md §4.2 item 2, pinned as behaviour rather than left implicit."""
    p = posting(2003, "Software Engineer, Demos", "Specialized Software Engineering",
                "New York City, NY")
    verdict = rule_judge.judge(p, persona)
    assert verdict["verdict"] == "relevant"
    assert verdict["justification"][2]["resume_field"].startswith("target_job_families")


def test_a_null_job_family_fails_G3(persona):
    """10 of the 161 real postings carry a null Job Family value."""
    p = posting(2004, "Software Engineer, Core", None, "Remote - United States")
    verdict = rule_judge.judge(p, persona)
    assert verdict["gate_failed"] == "G3_job_family"
    assert verdict["justification"][0]["evidence"] == "job family"


def test_seniority_is_judged_from_the_title_not_management_level(persona):
    """CONTRACT.md §4.2 item 4, left standing in R-v2 and pinned here.

    The board carries an explicit Management Level, and R-v2 ignores it. A
    plain-titled IC6 posting passes G1. This test records that, so a later
    version changing it is a deliberate bump.
    """
    p = posting(2005, "Software Engineer, Core", "Software Engineering",
                "Remote - United States")
    p["metadata"][2]["value"] = "IC6"
    assert rule_judge.judge(p, persona)["verdict"] == "relevant"
