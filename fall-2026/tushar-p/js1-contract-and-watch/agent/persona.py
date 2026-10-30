"""Reads only the five résumé fields the rule uses. Contact fields are never read."""

import json
from pathlib import Path

from .errors import PersonaError, RuleUndefinedError

RULE_FIELDS = (
    "job_search.target_titles",
    "skills",
    "job_search.years_experience",
    "job_search.work_country",
    "job_search.needs_sponsorship",
)


def _non_empty_string_list(value) -> bool:
    return (
        isinstance(value, list)
        and len(value) > 0
        and all(isinstance(item, str) and item.strip() for item in value)
    )


_TYPE_CHECKS = {
    "job_search.target_titles": (_non_empty_string_list, "a non-empty list of strings"),
    "skills": (_non_empty_string_list, "a non-empty list of strings"),
    # bool is a subclass of int in Python; True is not a number of years.
    "job_search.years_experience": (
        lambda v: isinstance(v, int) and not isinstance(v, bool),
        "an integer",
    ),
    "job_search.work_country": (lambda v: isinstance(v, str), "a string"),
    "job_search.needs_sponsorship": (lambda v: isinstance(v, bool), "a boolean"),
}


def _lookup(data: dict, dotted: str):
    current = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            raise PersonaError(f"missing required résumé field: {dotted}")
        current = current[part]
    return current


def load_rule_fields(path: Path) -> dict:
    """Return {dotted key: value} for the five rule fields, or raise before any fetch."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise PersonaError(f"cannot read persona file {path}: {err}") from None
    if not isinstance(data, dict):
        raise PersonaError(f"persona file {path} must hold a JSON object")

    fields = {}
    for key in RULE_FIELDS:
        value = _lookup(data, key)
        is_valid, expected = _TYPE_CHECKS[key]
        if not is_valid(value):
            raise PersonaError(f"résumé field {key} must be {expected}")
        fields[key] = value

    if fields["job_search.years_experience"] != 0:
        raise RuleUndefinedError(
            f"rule undefined for this value: job_search.years_experience = "
            f"{fields['job_search.years_experience']} (the contract covers 0)"
        )
    if fields["job_search.work_country"] != "US":
        raise RuleUndefinedError(
            f"rule undefined for this value: job_search.work_country = "
            f"{fields['job_search.work_country']!r} (the contract covers 'US')"
        )
    return fields
