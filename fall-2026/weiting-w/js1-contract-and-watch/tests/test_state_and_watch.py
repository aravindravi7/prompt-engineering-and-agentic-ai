"""The watch: baseline first, new-since-last by id, and wrong version W3.

These tests replay a constructed response through the real CLI, so the state
transitions they check are the ones the agent performs, not a re-implementation
of them.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jobagent import cli, state as state_mod
from tests import wrong_versions as wrong
from tests.conftest import ROOT


def _write_response(path, postings):
    Path(path).write_text(json.dumps({"jobs": postings}), encoding="utf-8")


@pytest.fixture
def workspace(tmp_path, constructed):
    board = {
        "host": "boards-api.greenhouse.io",
        "board_token": "reddit",
        "path_template": "/v1/boards/{board_token}/jobs",
    }
    (tmp_path / "board.json").write_text(json.dumps(board), encoding="utf-8")
    earlier = constructed[:4]
    _write_response(tmp_path / "earlier.json", earlier)
    _write_response(tmp_path / "later.json", constructed)
    return tmp_path, earlier, constructed


def _watch(tmp_path, raw, label, extra=()):
    argv = [
        "watch",
        "--board", str(tmp_path / "board.json"),
        "--resume", str(ROOT / "data" / "resume.persona.json"),
        "--state", str(tmp_path / "seen.json"),
        "--raw-dir", str(tmp_path / "raw"),
        "--runs-dir", str(tmp_path / "runs"),
        "--from-raw", str(raw),
        "--source-label", label,
        *extra,
    ]
    before = set((tmp_path / "runs").glob("run-*.json"))
    assert cli.main(argv) == 0
    new = set((tmp_path / "runs").glob("run-*.json")) - before
    assert len(new) == 1, f"expected exactly one new run report, got {new}"
    return json.loads(new.pop().read_text(encoding="utf-8"))


def test_first_run_is_a_baseline_and_reports_nothing_as_new(workspace):
    tmp_path, earlier, _ = workspace
    run = _watch(tmp_path, tmp_path / "earlier.json", "CONSTRUCTED: earlier snapshot")
    assert run["is_baseline"] is True
    assert run["counts"]["new"] == 0
    assert run["entries"] == []
    assert run["counts"]["postings_in_response"] == len(earlier)
    seen = json.loads((tmp_path / "seen.json").read_text(encoding="utf-8"))
    assert sorted(seen["seen_ids"]) == sorted(p["id"] for p in earlier)


def test_second_run_reports_exactly_the_ids_that_are_new(workspace):
    tmp_path, earlier, full = workspace
    _watch(tmp_path, tmp_path / "earlier.json", "CONSTRUCTED: earlier snapshot")
    run = _watch(tmp_path, tmp_path / "later.json", "CONSTRUCTED: later snapshot")
    assert run["is_baseline"] is False
    expected = [p["id"] for p in full if p["id"] not in {e["id"] for e in earlier}]
    assert [e["posting_id"] for e in run["entries"]] == expected
    assert run["counts"]["new"] == len(expected)
    assert run["state"]["sha256_before"] != run["state"]["sha256_after"]


def test_a_third_run_on_the_same_response_reports_nothing(workspace):
    tmp_path, _, _ = workspace
    _watch(tmp_path, tmp_path / "earlier.json", "CONSTRUCTED: earlier")
    _watch(tmp_path, tmp_path / "later.json", "CONSTRUCTED: later")
    run = _watch(tmp_path, tmp_path / "later.json", "CONSTRUCTED: later again")
    assert run["counts"]["new"] == 0
    assert run["entries"] == []


def test_identity_is_the_id_not_the_title(workspace):
    """A retitled posting with the same id is not new."""
    tmp_path, _, full = workspace
    _watch(tmp_path, tmp_path / "later.json", "CONSTRUCTED: later")
    retitled = json.loads(json.dumps(full))
    for p in retitled:
        p["title"] = p["title"] + " (updated)"
        p["updated_at"] = "2026-10-21T09:00:00-04:00"
    _write_response(tmp_path / "retitled.json", retitled)
    run = _watch(tmp_path, tmp_path / "retitled.json", "CONSTRUCTED: retitled")
    assert run["counts"]["new"] == 0


def test_run_report_names_the_raw_file_it_was_computed_from(workspace):
    tmp_path, _, _ = workspace
    run = _watch(tmp_path, tmp_path / "earlier.json", "CONSTRUCTED: earlier")
    assert run["raw_response"]["source"] == "replay"
    assert run["raw_response"]["source_label"] == "CONSTRUCTED: earlier"
    assert Path(run["raw_response"]["path"]).exists()


def test_state_unchanged_when_reporting_raises(tmp_path, constructed):
    """W3: the real order leaves the state alone when the reporter fails."""
    state_path = tmp_path / "seen.json"
    state_mod.save(state_path, state_mod.empty_state("reddit", "boards-api.greenhouse.io"), [])

    def boom(_postings):
        raise RuntimeError("reporter failed")

    before = state_path.read_text(encoding="utf-8")
    with pytest.raises(RuntimeError):
        wrong.watch_correct_state_last(
            state_path, "reddit", "boards-api.greenhouse.io", constructed, boom
        )
    assert state_path.read_text(encoding="utf-8") == before, "state must be untouched"

    with pytest.raises(RuntimeError):
        wrong.watch_W3_eager_state(
            state_path, "reddit", "boards-api.greenhouse.io", constructed, boom
        )
    after = json.loads(state_path.read_text(encoding="utf-8"))
    assert after["seen_ids"], "W3 has already swallowed the postings - this is the bug"


def test_two_runs_in_the_same_second_do_not_overwrite_each_other(workspace):
    """A real bug, found by running the CLI twice quickly on 2026-10-21.

    Both reports were named from a whole-second timestamp, so the second run
    overwrote the first and the baseline evidence disappeared.
    """
    tmp_path, _, _ = workspace
    _watch(tmp_path, tmp_path / "earlier.json", "CONSTRUCTED: earlier")
    _watch(tmp_path, tmp_path / "later.json", "CONSTRUCTED: later")
    reports = sorted((tmp_path / "runs").glob("run-*.json"))
    assert len(reports) == 2, f"a run report was overwritten: {reports}"
    baselines = [
        json.loads(p.read_text(encoding="utf-8"))["is_baseline"] for p in reports
    ]
    assert sorted(baselines) == [False, True]


def test_state_file_from_another_board_is_refused(workspace):
    tmp_path, _, _ = workspace
    _watch(tmp_path, tmp_path / "earlier.json", "CONSTRUCTED: earlier")
    with pytest.raises(ValueError):
        state_mod.load(tmp_path / "seen.json", "lyft", "boards-api.greenhouse.io")
