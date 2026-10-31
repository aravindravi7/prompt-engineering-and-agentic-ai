"""Missing field → stop before any fetch, with no output. Rule undefined → stop."""

import copy
import json

import pytest

from agent.errors import PersonaError, RuleUndefinedError
from agent.persona import RULE_FIELDS, load_rule_fields
from agent.run import RunOptions, run
from support import BOARD_SMALL, PERSONA, RUN_DATE, FakeOpener


def write_persona(tmp_path, data) -> str:
    path = tmp_path / "persona.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def without(data, dotted):
    data = copy.deepcopy(data)
    parent = data
    *parents, leaf = dotted.split(".")
    for part in parents:
        parent = parent[part]
    del parent[leaf]
    return data


def with_value(data, dotted, value):
    data = copy.deepcopy(data)
    parent = data
    *parents, leaf = dotted.split(".")
    for part in parents:
        parent = parent[part]
    parent[leaf] = value
    return data


def test_example_persona_yields_exactly_the_five_rule_fields():
    fields = load_rule_fields(PERSONA)
    assert set(fields) == set(RULE_FIELDS)
    assert fields["job_search.years_experience"] == 0
    assert fields["job_search.needs_sponsorship"] is True


@pytest.mark.parametrize("key", RULE_FIELDS)
def test_absent_field_stops(tmp_path, persona_data, key):
    with pytest.raises(PersonaError, match="missing"):
        load_rule_fields(write_persona(tmp_path, without(persona_data, key)))


def test_absent_job_search_block_stops(tmp_path, persona_data):
    with pytest.raises(PersonaError):
        load_rule_fields(write_persona(tmp_path, without(persona_data, "job_search")))


@pytest.mark.parametrize("key, bad", [
    ("job_search.target_titles", []),
    ("job_search.target_titles", "Software Engineer"),
    ("job_search.target_titles", ["Software Engineer", 7]),
    ("skills", []),
    ("skills", None),
    ("skills", ["Python", "  "]),
    ("job_search.years_experience", "0"),
    ("job_search.years_experience", 0.0),
    ("job_search.years_experience", False),
    ("job_search.work_country", ["US"]),
    ("job_search.needs_sponsorship", "true"),
    ("job_search.needs_sponsorship", 1),
])
def test_wrong_type_or_empty_list_stops(tmp_path, persona_data, key, bad):
    with pytest.raises(PersonaError, match=key.replace(".", r"\.")):
        load_rule_fields(write_persona(tmp_path, with_value(persona_data, key, bad)))


@pytest.mark.parametrize("key, value", [
    ("job_search.years_experience", 2),
    ("job_search.work_country", "CA"),
    ("job_search.work_country", "us"),
])
def test_values_outside_the_contract_stop(tmp_path, persona_data, key, value):
    with pytest.raises(RuleUndefinedError, match="rule undefined for this value"):
        load_rule_fields(write_persona(tmp_path, with_value(persona_data, key, value)))


def test_missing_field_stops_run_before_fetch_with_no_output(tmp_path, persona_data, make_config):
    config = make_config(persona_path=write_persona(tmp_path, without(persona_data, "skills")))
    opener = FakeOpener(BOARD_SMALL.read_bytes())
    with pytest.raises(PersonaError):
        run(RunOptions(config=config, run_date=RUN_DATE, no_claude=True), opener=opener)
    assert opener.urls == []
    for name in ("raw", "out", "state"):
        assert not (tmp_path / name).exists()


def test_contact_fields_are_not_needed(tmp_path, persona_data):
    stripped = {k: v for k, v in persona_data.items() if k not in ("personal", "education", "experience")}
    assert set(load_rule_fields(write_persona(tmp_path, stripped))) == set(RULE_FIELDS)
