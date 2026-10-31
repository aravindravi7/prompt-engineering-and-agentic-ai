"""Shared fixtures.

The postings in this file are CONSTRUCTED EXAMPLES, written by hand to exercise
one gate each. They are not real postings and are not used in any report, any
count, or any experiment; the reports use the saved raw responses in
``evidence/raw/``. They are labelled here so that nothing in the test suite can
be mistaken for evidence about the real board.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobagent import resume as resume_mod  # noqa: E402


def posting(pid, title, job_family, location):
    """A constructed posting shaped like the real response.

    The real listing carries no ``departments`` key; the discipline signal is
    a ``metadata`` entry named "Job Family". ``job_family=None`` builds the
    null-value case that 10 of the 161 real postings have.
    """
    return {
        "id": pid,
        "title": title,
        "metadata": [
            {"id": 944668, "name": "Position ID", "value": f"P-{pid}"},
            {"id": 944675, "name": "Job Family", "value": job_family},
            {"id": 956351, "name": "Management Level", "value": "IC3"},
        ],
        "location": {"name": location},
        "absolute_url": f"https://job-boards.greenhouse.io/constructed/jobs/{pid}",
        "updated_at": "2026-10-01T12:00:00-04:00",
    }


# One constructed posting per row of CONTRACT.md §4.1.
CONSTRUCTED = [
    posting(1001, "Software Engineer, Ads Formats", "Software Engineering", "New York City, NY"),
    posting(1002, "Senior Software Engineer, Ads", "Software Engineering", "New York City, NY"),
    posting(1003, "Client Partner, Retail", "Client Partner", "New York City, NY"),
    posting(1004, "Software Engineer, Payroll Tax", "Payroll", "Remote - United States"),
    posting(1005, "Software Engineer, Core", "Software Engineering", "Dublin, Ireland"),
    posting(1006, "Site Reliability Engineer", "Software Engineering", "Remote - United States"),
    posting(1007, "Software Engineer, Data Platform", None, "Remote - United States"),
]

EXPECTED = {
    1001: ("relevant", None),
    1002: ("not_relevant", "G1_title_block"),
    1003: ("not_relevant", "G2_discipline"),
    1004: ("not_relevant", "G3_job_family"),
    1005: ("not_relevant", "G4_location"),
    1006: ("not_relevant", "G2_discipline"),
    1007: ("not_relevant", "G3_job_family"),
}


@pytest.fixture(scope="session")
def persona():
    return resume_mod.load(ROOT / "data" / "resume.persona.json")


@pytest.fixture
def constructed():
    return json.loads(json.dumps(CONSTRUCTED))


@pytest.fixture
def constructed_response(constructed):
    return json.dumps({"jobs": constructed}).encode("utf-8")
