"""The validator for the prompt contract's output format.

CONTRACT.md R3 and Step 3 of the assignment both want the same thing: the
model's answer is only usable if it arrives in a shape the agent can check.
This module rejects anything else, and it rejects it loudly, because a
validator that quietly repairs output is a validator that hides how often the
contract was not met.

Deliberately strict, and each strictness is a thing the prompt experiment can
measure:

* the whole response must be one JSON object and nothing else — a code fence,
  a preamble, or a trailing sentence is a rejection, not something to strip;
* the key set is exact;
* ``posting_id`` must be the posting that was asked about, so a model that
  answers about a different job is caught rather than filed;
* ``gate_failed`` is null exactly when the verdict is ``relevant`` (O4);
* every justification must name fields that resolve and quote evidence that
  really occurs in the posting field it names (O2).
"""

from __future__ import annotations

import json

from .errors import ValidatorRejected
from .fieldpath import MISSING, field_text, resolve
from .rule import GATE_ORDER

VERDICTS = ("relevant", "not_relevant")
CONFIDENCES = ("high", "medium", "low")

TOP_KEYS = {"posting_id", "verdict", "gate_failed", "justification", "confidence"}
CITE_REQUIRED = {"resume_field", "posting_field", "evidence"}
CITE_OPTIONAL = {"resume_value"}


def validate(raw: str, posting: dict, resume: dict) -> dict:
    """Return the parsed verdict, or raise :class:`ValidatorRejected`."""
    text = raw.strip()
    if not text:
        raise ValidatorRejected("empty response")
    if not (text.startswith("{") and text.endswith("}")):
        raise ValidatorRejected(
            "response is not exactly one JSON object; it begins "
            f"{text[:24]!r} and ends {text[-24:]!r}"
        )
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidatorRejected(f"not parseable as JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValidatorRejected("top level is not an object")

    keys = set(obj)
    if keys != TOP_KEYS:
        raise ValidatorRejected(
            f"key set is {sorted(keys)}; the contract requires exactly {sorted(TOP_KEYS)}"
        )

    if obj["posting_id"] != posting["id"]:
        raise ValidatorRejected(
            f"posting_id {obj['posting_id']!r} is not the posting that was asked "
            f"about ({posting['id']!r})"
        )

    if obj["verdict"] not in VERDICTS:
        raise ValidatorRejected(f"verdict {obj['verdict']!r} not in {VERDICTS}")

    gate = obj["gate_failed"]
    if gate is not None and gate not in GATE_ORDER:
        raise ValidatorRejected(f"gate_failed {gate!r} not in {GATE_ORDER} or null")
    if (gate is None) != (obj["verdict"] == "relevant"):
        raise ValidatorRejected(
            "gate_failed must be null exactly when the verdict is relevant "
            f"(got verdict={obj['verdict']!r}, gate_failed={gate!r})"
        )

    if obj["confidence"] not in CONFIDENCES:
        raise ValidatorRejected(f"confidence {obj['confidence']!r} not in {CONFIDENCES}")

    justification = obj["justification"]
    if not isinstance(justification, list) or not justification:
        raise ValidatorRejected("justification must be a non-empty list")
    for i, cite in enumerate(justification):
        check_citation(cite, posting, resume, where=f"justification[{i}]")

    return obj


def check_citation(cite, posting: dict, resume: dict, where: str = "justification") -> None:
    """CONTRACT.md O2, as one function so the rule and the model face one test."""
    if not isinstance(cite, dict):
        raise ValidatorRejected(f"{where} is not an object")
    keys = set(cite)
    if not CITE_REQUIRED <= keys or not keys <= (CITE_REQUIRED | CITE_OPTIONAL):
        raise ValidatorRejected(
            f"{where} keys are {sorted(keys)}; required {sorted(CITE_REQUIRED)}, "
            f"optional {sorted(CITE_OPTIONAL)}"
        )
    for key in ("resume_field", "posting_field", "evidence"):
        if not isinstance(cite[key], str) or not cite[key]:
            raise ValidatorRejected(f"{where}.{key} must be a non-empty string")

    if resolve(resume, cite["resume_field"]) is MISSING:
        raise ValidatorRejected(
            f"{where}.resume_field {cite['resume_field']!r} does not resolve in the "
            "resume that was loaded"
        )
    value = resolve(posting, cite["posting_field"])
    if value is MISSING:
        raise ValidatorRejected(
            f"{where}.posting_field {cite['posting_field']!r} does not resolve in "
            f"posting {posting.get('id')!r}"
        )
    haystack = field_text(value)
    needle = cite["evidence"].casefold()
    if needle not in haystack:
        raise ValidatorRejected(
            f"{where}.evidence {cite['evidence']!r} does not occur in "
            f"{cite['posting_field']} of posting {posting.get('id')!r}"
        )
