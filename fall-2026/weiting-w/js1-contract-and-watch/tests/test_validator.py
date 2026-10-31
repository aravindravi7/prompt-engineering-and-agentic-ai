"""The prompt contract's validator (CONTRACT.md R3, assignment Step 3).

Every rejection below is a shape a model output really can take, and every one
of them is a rejection rather than something the agent repairs.
"""

from __future__ import annotations

import json

import pytest

from jobagent.errors import ValidatorRejected
from jobagent.validator import validate


def good(posting):
    return {
        "posting_id": posting["id"],
        "verdict": "not_relevant",
        "gate_failed": "G1_title_block",
        "justification": [
            {
                "resume_field": "title_block[0]",
                "posting_field": "title",
                "evidence": "senior",
            }
        ],
        "confidence": "high",
    }


@pytest.fixture
def blocked(constructed):
    return [p for p in constructed if p["id"] == 1002][0]


def test_accepts_a_response_that_meets_the_contract(blocked, persona):
    parsed = validate(json.dumps(good(blocked)), blocked, persona)
    assert parsed["verdict"] == "not_relevant"


def test_rejects_a_code_fence(blocked, persona):
    body = "```json\n" + json.dumps(good(blocked)) + "\n```"
    with pytest.raises(ValidatorRejected):
        validate(body, blocked, persona)


def test_rejects_a_preamble(blocked, persona):
    with pytest.raises(ValidatorRejected):
        validate("Here is the verdict:\n" + json.dumps(good(blocked)), blocked, persona)


def test_rejects_a_trailing_sentence(blocked, persona):
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(good(blocked)) + "\nHope that helps!", blocked, persona)


def test_rejects_an_extra_key(blocked, persona):
    payload = {**good(blocked), "reasoning": "..."}
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_rejects_a_missing_key(blocked, persona):
    payload = good(blocked)
    del payload["confidence"]
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_rejects_an_answer_about_a_different_posting(blocked, persona):
    payload = {**good(blocked), "posting_id": 999999}
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_rejects_a_gate_that_is_not_a_gate(blocked, persona):
    payload = {**good(blocked), "gate_failed": "G5_vibes"}
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_rejects_relevant_with_a_gate_named(blocked, persona):
    payload = {**good(blocked), "verdict": "relevant"}
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_rejects_not_relevant_with_a_null_gate(blocked, persona):
    payload = {**good(blocked), "gate_failed": None}
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_rejects_an_empty_justification(blocked, persona):
    payload = {**good(blocked), "justification": []}
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_rejects_a_resume_field_that_does_not_resolve(blocked, persona):
    payload = good(blocked)
    payload["justification"][0]["resume_field"] = "skills[0]"
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_rejects_a_posting_field_that_does_not_resolve(blocked, persona):
    payload = good(blocked)
    payload["justification"][0]["posting_field"] = "content"
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_rejects_evidence_that_is_not_in_the_field_it_names(blocked, persona):
    payload = good(blocked)
    payload["justification"][0]["evidence"] = "principal"
    with pytest.raises(ValidatorRejected):
        validate(json.dumps(payload), blocked, persona)


def test_accepts_evidence_quoted_from_a_null_job_family_entry(persona):
    posting = {
        "id": 3001,
        "title": "Software Engineer",
        "metadata": [{"id": 944675, "name": "Job Family", "value": None}],
        "location": {"name": "New York City, NY"},
    }
    payload = {
        "posting_id": 3001,
        "verdict": "not_relevant",
        "gate_failed": "G3_job_family",
        "justification": [
            {"resume_field": "target_job_families",
             "posting_field": "metadata[0].name", "evidence": "job family"}
        ],
        "confidence": "high",
    }
    assert validate(json.dumps(payload), posting, persona)["gate_failed"] == "G3_job_family"
