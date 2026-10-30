"""R1–R6 and the verdict, with boundary cases from CONTRACT.md v0.2."""

import html
import json

import pytest

from agent import rules
from agent.persona import load_rule_fields
from agent.text import strip_html
from support import BOARD_SMALL, PERSONA, RUN_DATE, posting

FIELDS = load_rule_fields(PERSONA)
TARGETS = FIELDS["job_search.target_titles"]
SKILLS = FIELDS["skills"]


def escaped(text: str) -> str:
    """Posting content as Greenhouse sends it: escaped HTML."""
    return html.escape(text)


def result_of(entry):
    return entry["result"]


# ---------- HTML stripping ----------

def test_strip_html_unescapes_then_drops_tags():
    raw = escaped("<p>Build in <strong>Python</strong>&nbsp;and Go.</p><ul><li>Java</li><li>SQL</li></ul>")
    text = strip_html(raw)
    assert "<" not in text and "&" not in text
    assert "Python" in text and "Java SQL" in text


def test_r4_reads_years_written_with_double_escaped_nbsp():
    # Real-shaped Greenhouse content: the HTML is escaped, and so is the &nbsp; inside it.
    p = posting(content="&lt;p&gt;5+&amp;nbsp;years of experience&lt;/p&gt;")
    entry = rules.judge(p, FIELDS, RUN_DATE)["rule_justification"][3]
    assert entry["result"] == "fail", entry["value_found"]


def test_skill_only_in_tag_attribute_is_not_found():
    content = escaped('<p><a href="https://python.org/react">Apply here</a></p>')
    assert result_of(rules.check_r6_skills(strip_html(content), SKILLS)) == "fail"


# ---------- R1 Title ----------

@pytest.mark.parametrize("title, expected", [
    ("Software Engineer", "pass"),
    ("Software Engineer, New Grad", "pass"),
    ("software engineer, backend", "pass"),
    ("AI Engineer", "pass"),
    ("Backend Engineer, Link", "pass"),
    ("Software Engineer, Internal Identity", "pass"),          # "Internal" is not "Intern"
    ("Senior Software Engineer", "fail"),
    ("Staff Backend Engineer", "fail"),
    ("Software Engineer, Intern", "fail"),
    ("Software Engineer, Intern (Summer or Winter)", "fail"),
    ("Engineering Manager, Software Engineer", "fail"),
    ("Tech Lead, Backend Engineer", "fail"),
    ("High School Internship, Software Engineering", "fail"),  # neither word matches
    ("Software Engineering Lead", "fail"),
    ("Abuse Investigator", "fail"),
    ("Frontend Engineer", "fail"),
])
def test_r1_title(title, expected):
    entry = rules.check_r1_title(title, TARGETS)
    assert entry["result"] == expected
    assert entry["resume_field"] == "job_search.target_titles" and entry["posting_field"] == "title"


def test_r1_excluded_word_wins_over_target():
    entry = rules.check_r1_title("Principal AI Engineer", TARGETS)
    assert entry["result"] == "fail" and "Principal" in entry["value_found"]


# ---------- R2 Freshness ----------

@pytest.mark.parametrize("first_published, expected", [
    ("2026-10-06T10:00:00-04:00", "pass"),   # exactly 21 days
    ("2026-10-05T23:59:59-04:00", "fail"),   # 22 days
    ("2026-10-27T08:00:00-04:00", "pass"),   # same day
    ("2026-11-03T08:00:00-05:00", "pass"),   # future
    ("2026-10-06T02:00:00Z", "fail"),        # 2026-10-05 22:00 in New York → 22 days
    ("2026-10-06T03:59:59+00:00", "fail"),
    ("2026-10-06T04:00:00+00:00", "pass"),   # midnight 2026-10-06 in New York → 21 days
])
def test_r2_boundaries_in_new_york_calendar_days(first_published, expected):
    entry = rules.check_r2_freshness(posting(first_published=first_published), RUN_DATE)
    assert entry["result"] == expected
    assert entry["posting_field"] == "first_published"


def test_r2_falls_back_to_updated_at_when_first_published_missing():
    p = posting(first_published=None, updated_at="2026-09-01T10:00:00-04:00")
    entry = rules.check_r2_freshness(p, RUN_DATE)
    assert entry["result"] == "fail" and entry["posting_field"] == "updated_at"
    assert rules.date_used(p)["field"] == "updated_at"


def test_r2_falls_back_when_first_published_unparseable():
    p = posting(first_published="last Tuesday", updated_at="2026-10-26T10:00:00-04:00")
    assert rules.check_r2_freshness(p, RUN_DATE)["posting_field"] == "updated_at"


@pytest.mark.parametrize("fp, ua", [(None, None), ("", "garbage"), ("soon", None)])
def test_r2_unknown_when_both_dates_missing_or_unparseable(fp, ua):
    p = posting(first_published=fp, updated_at=ua)
    assert rules.check_r2_freshness(p, RUN_DATE)["result"] == "unknown"
    assert rules.date_used(p) is None


# ---------- R3 Location ----------

@pytest.mark.parametrize("location, expected", [
    # Cases required by the user, from real Stripe values.
    ("Toronto, CA", "fail"),
    ("London OR Dublin", "fail"),
    ("IN-Bengaluru", "fail"),
    ("Seattle, WA OR New York, NY", "pass"),
    ("US / Canada", "pass"),
    ("N/A", "unknown"),
    ("Remote", "unknown"),
    ("Dublin", "fail"),
    # More boundaries.
    ("CA-Toronto", "fail"),
    ("Sydney, Australia", "fail"),       # "us" inside Australia is not the word US
    ("AMER", "fail"),
    ("CDMX", "fail"),
    ("Poland - Remote OR Romania - Remote", "fail"),
    ("Sydney Or Melbourne", "fail"),
    ("Remote in the us", "fail"),         # lowercase "us" does not count
    ("Remote in the US", "pass"),
    ("US-Remote", "pass"),
    ("US-SF-HQ", "pass"),
    ("United States", "pass"),
    ("U.S. Remote", "pass"),
    ("San Francisco", "pass"),
    ("South San Francisco, CA", "pass"),  # CA excluded, city still matches
    ("Chicago", "pass"),
    ("sf, nyc", "pass"),
    ("NYC, Sea, SF, Tor", "pass"),
    ("Chicago, Illinois", "pass"),
    ("Portland, OR", "pass"),             # abbreviation after a comma
    ("Portland OR", "fail"),              # same letters without a comma
    ("Austin; TX", "pass"),
    ("Austin, tx", "fail"),               # abbreviations are uppercase only
    ("Remote North America", "fail"),
    ("na", "unknown"),
    ("LOCATION", "unknown"),
    ("", "unknown"),
    ("Remote ", "unknown"),               # trimmed by judge(); see test below
])
def test_r3_location(location, expected):
    entry = rules.check_r3_location(location.strip())
    assert entry["result"] == expected, entry["value_found"]
    assert entry["resume_field"] == "job_search.work_country" and entry["posting_field"] == "location.name"


def test_r3_trims_spaces_and_handles_missing_location():
    p = posting(location={"name": "  Remote  "})
    assert rules.judge(p, FIELDS, RUN_DATE)["rule_justification"][2]["result"] == "unknown"
    p = posting(location=None)
    assert rules.judge(p, FIELDS, RUN_DATE)["rule_justification"][2]["result"] == "unknown"


def test_r3_state_abbreviation_list_excludes_only_ca():
    assert len(rules.US_STATE_ABBREVIATIONS) == 49
    assert "CA" not in rules.US_STATE_ABBREVIATIONS
    assert len(rules.US_STATE_NAMES) == 50


# ---------- R4 Experience ----------

@pytest.mark.parametrize("text, expected", [
    ("3+ years of experience", "pass"),
    ("4+ years of experience", "fail"),
    ("0+ years", "pass"),
    ("10+ years", "fail"),
    ("2–5 years", "pass"),
    ("2-5 years", "pass"),
    ("2 to 5 years", "pass"),
    ("4–6 years", "fail"),
    ("3-5+ years", "pass"),
    ("5 + years", "fail"),
    ("5+ years backend, 2+ years Go", "fail"),   # largest minimum wins (user-required case)
    ("2+ years backend, 1+ years Go", "pass"),
    ("3 years of experience", "unknown"),        # plain "N years" does not count
    ("three+ years", "unknown"),                 # spelled-out numbers are not parsed
    ("no experience requirement stated", "unknown"),
    ("2.5+ years", "unknown"),                   # not a whole number N; known gap
])
def test_r4_experience(text, expected):
    entry = rules.check_r4_experience(text)
    assert entry["result"] == expected, entry["value_found"]
    assert entry["resume_field"] == "job_search.years_experience" and entry["posting_field"] == "content"


# ---------- R5 Sponsorship ----------

@pytest.mark.parametrize("phrase", rules.SPONSORSHIP_REFUSALS)
def test_r5_each_listed_phrase_fails(phrase):
    entry = rules.check_r5_sponsorship(f"Note: we are {phrase.upper()} for this role.", True)
    assert entry["result"] == "fail"


@pytest.mark.parametrize("text", [
    "We sponsor visas.",
    "Sponsorship is available.",
    "Candidates must be authorized to work in the US.",   # not on the closed list
    "",
])
def test_r5_pass_when_no_listed_phrase(text):
    assert rules.check_r5_sponsorship(text, True)["result"] == "pass"


def test_r5_not_applicable_when_sponsorship_not_needed():
    entry = rules.check_r5_sponsorship("We are unable to sponsor.", False)
    assert entry["result"] == "pass" and "not applicable" in entry["value_found"]


# ---------- R6 Skills ----------

@pytest.mark.parametrize("text, expected", [
    ("We use JavaScript.", "fail"),         # "Java" does not match "JavaScript"
    ("We use Java, Kotlin.", "pass"),
    ("PostgreSQL only.", "pass"),
    ("Spring Boot services.", "pass"),
    ("spring   boot", "pass"),
    ("Springboot", "fail"),
    ("Rust and Kubernetes.", "fail"),
    ("aws lambda", "pass"),
])
def test_r6_skills(text, expected):
    assert rules.check_r6_skills(text, SKILLS)["result"] == expected


def test_r6_sql_is_not_found_inside_postgresql():
    entry = rules.check_r6_skills("PostgreSQL only.", SKILLS)
    assert "PostgreSQL" in entry["value_found"] and "SQL," not in entry["value_found"]
    assert entry["value_found"] == "skills found: PostgreSQL"


# ---------- Verdict ----------

def _entries(*results):
    return [{"result": r} for r in results]


def test_verdict_any_fail_beats_unknown():
    assert rules.verdict(_entries("pass", "unknown", "fail", "pass", "pass", "pass")) == "not_relevant"


def test_verdict_unknown_without_fail_is_cannot_tell():
    assert rules.verdict(_entries("pass", "pass", "unknown", "pass", "pass", "pass")) == "cannot_tell"


def test_verdict_all_pass_is_relevant():
    assert rules.verdict(_entries(*["pass"] * 6)) == "relevant"


def test_fixture_board_verdicts():
    jobs = json.loads(BOARD_SMALL.read_text())["jobs"]
    verdicts = {j["id"]: rules.judge(j, FIELDS, RUN_DATE)["rule_verdict"] for j in jobs}
    assert verdicts == {
        1001: "relevant",
        1002: "not_relevant",  # R1 Senior
        1003: "not_relevant",  # R3 Dublin
        1004: "cannot_tell",   # R3 Remote, R4 no years
        1005: "not_relevant",  # R2 56 days old
        1006: "not_relevant",  # R4 5+ years
        1007: "not_relevant",  # R5 unable to sponsor
        1008: "not_relevant",  # R6 no listed skill
    }


def test_every_justification_names_fields_value_and_result():
    for job in json.loads(BOARD_SMALL.read_text())["jobs"]:
        entries = rules.judge(job, FIELDS, RUN_DATE)["rule_justification"]
        assert [e["check"] for e in entries] == ["R1", "R2", "R3", "R4", "R5", "R6"]
        for e in entries:
            assert e["resume_field"] and e["posting_field"] and e["value_found"]
            assert e["result"] in ("pass", "fail", "unknown")


# ---------- What a failure looks like (CONTRACT.md) ----------

@pytest.mark.parametrize("label, overrides", [
    ("older than 21 days", {"first_published": "2026-10-05T10:00:00-04:00"}),
    ("more than 3 years", {"content": escaped("<p>Python. 4+ years of experience.</p>")}),
    ("outside the US", {"location": {"name": "Dublin"}}),
    ("will not sponsor", {"content": escaped("<p>Python. 2+ years. We will not sponsor visas.</p>")}),
])
def test_failure_cases_are_never_relevant(label, overrides):
    assert rules.judge(posting(), FIELDS, RUN_DATE)["rule_verdict"] == "relevant"  # control
    assert rules.judge(posting(**overrides), FIELDS, RUN_DATE)["rule_verdict"] == "not_relevant", label
