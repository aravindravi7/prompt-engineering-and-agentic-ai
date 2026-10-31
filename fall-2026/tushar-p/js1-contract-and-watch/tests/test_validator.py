"""Wrong version 1: a justification that cites no fields is rejected, for both judges."""

import copy
import json

import pytest

from agent import rules
from agent.errors import ValidationError
from agent.persona import load_rule_fields
from agent.validator import validate_claude_reply, validate_rule_justification
from support import PERSONA, RUN_DATE, posting, valid_reply

FIELDS = load_rule_fields(PERSONA)


def good_rule_entries():
    return rules.judge(posting(), FIELDS, RUN_DATE)["rule_justification"]


# ---------- Rule judge ----------

def test_real_rule_justification_is_accepted():
    validate_rule_justification(good_rule_entries())


@pytest.mark.parametrize("part", ["resume_field", "posting_field", "value_found", "result"])
@pytest.mark.parametrize("how", ["absent", "empty", "none"])
def test_rule_entry_missing_any_part_is_rejected(part, how):
    entries = good_rule_entries()
    if how == "absent":
        del entries[3][part]
    else:
        entries[3][part] = "" if how == "empty" else None
    with pytest.raises(ValidationError, match=part):
        validate_rule_justification(entries)


@pytest.mark.parametrize("part, value", [
    ("resume_field", "personal.email"),
    ("resume_field", "education"),
    ("posting_field", "company_name"),
    ("result", "maybe"),
])
def test_rule_entry_with_unlisted_value_is_rejected(part, value):
    entries = good_rule_entries()
    entries[0][part] = value
    with pytest.raises(ValidationError):
        validate_rule_justification(entries)


def test_rule_justification_must_cover_r1_to_r6_once_in_order():
    entries = good_rule_entries()
    with pytest.raises(ValidationError):
        validate_rule_justification(entries[:5])
    with pytest.raises(ValidationError):
        validate_rule_justification(list(reversed(entries)))
    with pytest.raises(ValidationError):
        validate_rule_justification(entries + [copy.deepcopy(entries[0])])


# ---------- Claude judge ----------

def reply_dict(**overrides):
    data = json.loads(valid_reply(42))
    data.update(overrides)
    return data


def entry_dict(**overrides):
    entry = {"resume_field": "skills", "posting_field": "content", "evidence": "Python"}
    entry.update(overrides)
    return entry


def test_valid_claude_reply_is_accepted():
    data = validate_claude_reply(valid_reply(42), 42)
    assert data["verdict"] == "relevant"


@pytest.mark.parametrize("entry", [
    {"posting_field": "content", "evidence": "Python"},                        # no resume_field
    {"resume_field": "skills", "evidence": "Python"},                          # no posting_field
    entry_dict(resume_field=""),
    entry_dict(posting_field=""),
    entry_dict(resume_field=None),
    entry_dict(resume_field="personal.name"),
    entry_dict(resume_field="Skills"),
    entry_dict(posting_field="company_name"),
    entry_dict(posting_field="location"),
])
def test_claude_entry_citing_no_listed_field_is_rejected(entry):
    with pytest.raises(ValidationError):
        validate_claude_reply(json.dumps(reply_dict(justification=[entry])), 42)


@pytest.mark.parametrize("text", [
    "```json\n" + valid_reply(42) + "\n```",                                    # fenced: not repaired
    "Here is my answer: " + valid_reply(42),
    "not json at all",
    "",
    "[]",
    json.dumps(reply_dict(confidence=0.9)),                                     # extra top-level key
    json.dumps(reply_dict(justification=[entry_dict(note="x")])),               # extra entry key
    json.dumps({k: v for k, v in reply_dict().items() if k != "verdict"}),      # missing key
    json.dumps(reply_dict(verdict="maybe")),
    json.dumps(reply_dict(verdict="Relevant")),
    json.dumps(reply_dict(posting_id="43")),
    json.dumps(reply_dict(posting_id=42)),                                      # must be a string
    json.dumps(reply_dict(justification=[])),
    json.dumps(reply_dict(justification="title matches")),
    json.dumps(reply_dict(justification=[entry_dict(evidence=5)])),
    '{"posting_id": "42", "posting_id": "42", "verdict": "relevant", "justification": []}',
])
def test_claude_reply_not_matching_format_is_rejected(text):
    with pytest.raises(ValidationError):
        validate_claude_reply(text, 42)


def test_claude_reply_none_is_rejected():
    with pytest.raises(ValidationError):
        validate_claude_reply(None, 42)
