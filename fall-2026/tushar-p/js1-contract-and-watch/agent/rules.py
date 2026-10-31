"""The rule judge: checks R1–R6 and the verdict, exactly as CONTRACT.md v0.2 states them.

Each check returns one justification entry:
{"check", "resume_field", "posting_field", "value_found", "result"}.
"""

import re
from datetime import date

from .text import contains_word, normalize, strip_html, word_pattern
from .timeutil import parse_calendar_date
from .validator import R2_RESUME_FIELD, validate_rule_justification

RULE_LABEL = "record"

PASS, FAIL, UNKNOWN = "pass", "fail", "unknown"

EXCLUDED_TITLE_WORDS = ("Senior", "Staff", "Principal", "Lead", "Manager", "Intern")

FRESHNESS_DAYS = 21
MAX_MIN_YEARS = 3

SPONSORSHIP_REFUSALS = (
    "unable to sponsor",
    "will not sponsor",
    "does not sponsor",
    "no sponsorship",
    "without sponsorship",
    "without the need for sponsorship",
)

# R3 lists, from the contract (built from the real Stripe location values on 2026-10-27).
US_MARKERS = ("United States", "USA", "U.S.")  # case-insensitive
US_MARKER_UPPERCASE_ONLY = "US"
US_CITIES = (
    "San Francisco", "South San Francisco", "New York", "New York City", "New-York",
    "Seattle", "Chicago", "Atlanta",
)
US_CITY_SHORT_FORMS = ("SF", "NYC", "NY", "SEA", "CHI", "ATL", "DC")
US_STATE_NAMES = (
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming",
)
# "CA" is excluded: on this board "Toronto, CA" means Canada.
US_STATE_ABBREVIATIONS = (
    "AL", "AK", "AZ", "AR", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX",
    "UT", "VT", "VA", "WA", "WV", "WI", "WY",
)
LOCATION_UNKNOWN_VALUES = ("remote", "n/a", "na", "location", "")

# Uppercase only, and only directly after a comma or semicolon (", WA", "; IL").
_STATE_ABBREVIATION_AFTER_SEPARATOR = re.compile(
    r"[,;]\s*(" + "|".join(US_STATE_ABBREVIATIONS) + r")(?![A-Za-z0-9])"
)

# "N+ years", "N–M years", "N-M years", "N to M years". The minimum of each match is N.
_YEARS = re.compile(
    r"(?<![A-Za-z0-9.])(\d+)"
    r"(?:\s*\+|\s*[-–]\s*\d+\s*\+?|\s+to\s+\d+\s*\+?)"
    r"\s*years(?![A-Za-z0-9])",
    re.IGNORECASE,
)


def _entry(check, resume_field, posting_field, value_found, result) -> dict:
    return {
        "check": check,
        "resume_field": resume_field,
        "posting_field": posting_field,
        "value_found": value_found,
        "result": result,
    }


def check_r1_title(title: str, target_titles: list[str]) -> dict:
    excluded = [w for w in EXCLUDED_TITLE_WORDS if contains_word(title, w)]
    targets = [t for t in target_titles if contains_word(title, t)]
    if excluded:
        found, result = f"title {title!r}; excluded word(s): {', '.join(excluded)}", FAIL
    elif targets:
        found, result = f"title {title!r}; target title(s): {', '.join(targets)}", PASS
    else:
        found, result = f"title {title!r}; no target title", FAIL
    return _entry("R1", "job_search.target_titles", "title", found, result)


def date_used(posting: dict) -> dict | None:
    """{"field", "value", "calendar_date"} for first_published, else updated_at, else None.

    An unparseable first_published falls through to updated_at, as a missing one does.
    """
    for field in ("first_published", "updated_at"):
        calendar_date = parse_calendar_date(posting.get(field))
        if calendar_date is not None:
            return {"field": field, "value": posting[field], "calendar_date": calendar_date}
    return None


def check_r2_freshness(posting: dict, run_date: date) -> dict:
    used = date_used(posting)
    if used is None:
        return _entry(
            "R2", R2_RESUME_FIELD, "first_published",
            "first_published and updated_at both missing or unparseable", UNKNOWN,
        )
    days = (run_date - used["calendar_date"]).days
    result = PASS if days <= FRESHNESS_DAYS else FAIL
    found = (
        f"{used['field']} = {used['value']} → {used['calendar_date'].isoformat()} "
        f"(New York); {days} day(s) before run date {run_date.isoformat()}"
    )
    return _entry("R2", R2_RESUME_FIELD, used["field"], found, result)


def us_location_matches(location: str) -> list[str]:
    matches = [m for m in US_MARKERS if contains_word(location, m)]
    if contains_word(location, US_MARKER_UPPERCASE_ONLY, ignore_case=False):
        matches.append(US_MARKER_UPPERCASE_ONLY)
    matches += [c for c in US_CITIES if contains_word(location, c)]
    matches += [s for s in US_CITY_SHORT_FORMS if contains_word(location, s)]
    matches += [s for s in US_STATE_NAMES if contains_word(location, s)]
    matches += [f", {a}" for a in _STATE_ABBREVIATION_AFTER_SEPARATOR.findall(location)]
    return matches


def check_r3_location(location: str) -> dict:
    if location.lower() in LOCATION_UNKNOWN_VALUES:
        found, result = f"location.name {location!r}; only 'Remote' or a placeholder", UNKNOWN
    else:
        matches = us_location_matches(location)
        if matches:
            found, result = f"location.name {location!r}; US match: {', '.join(matches)}", PASS
        else:
            found, result = f"location.name {location!r}; no US match", FAIL
    return _entry("R3", "job_search.work_country", "location.name", found, result)


def check_r4_experience(content_text: str) -> dict:
    minimums = [int(n) for n in _YEARS.findall(content_text)]
    if not minimums:
        found, result = "no 'N+ years' or 'N–M years' found", UNKNOWN
    else:
        largest = max(minimums)
        result = PASS if largest <= MAX_MIN_YEARS else FAIL
        found = f"minimum years found: {minimums}; largest {largest}"
    return _entry("R4", "job_search.years_experience", "content", found, result)


def check_r5_sponsorship(content_text: str, needs_sponsorship: bool) -> dict:
    if not needs_sponsorship:
        found, result = "not applicable: needs_sponsorship is false", PASS
    else:
        phrases = [p for p in SPONSORSHIP_REFUSALS if contains_word(content_text, p)]
        if phrases:
            found, result = f"refusal phrase(s): {', '.join(phrases)}", FAIL
        else:
            found, result = "no listed refusal phrase", PASS
    return _entry("R5", "job_search.needs_sponsorship", "content", found, result)


def check_r6_skills(content_text: str, skills: list[str]) -> dict:
    found_skills = [s for s in skills if word_pattern(s).search(content_text)]
    if found_skills:
        found, result = f"skills found: {', '.join(found_skills)}", PASS
    else:
        found, result = "no listed skill found", FAIL
    return _entry("R6", "skills", "content", found, result)


def verdict(justification: list[dict]) -> str:
    results = [entry["result"] for entry in justification]
    if FAIL in results:
        return "not_relevant"
    if UNKNOWN in results:
        return "cannot_tell"
    return "relevant"


def judge(posting: dict, fields: dict, run_date: date) -> dict:
    """Rule verdict and R1–R6 justification for one posting."""
    title = normalize(posting.get("title") or "")
    location = normalize((posting.get("location") or {}).get("name") or "")
    content_text = strip_html(posting.get("content"))
    justification = [
        check_r1_title(title, fields["job_search.target_titles"]),
        check_r2_freshness(posting, run_date),
        check_r3_location(location),
        check_r4_experience(content_text),
        check_r5_sponsorship(content_text, fields["job_search.needs_sponsorship"]),
        check_r6_skills(content_text, fields["skills"]),
    ]
    validate_rule_justification(justification)
    return {"rule_verdict": verdict(justification), "rule_justification": justification}
