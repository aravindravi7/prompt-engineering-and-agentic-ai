"""Baseline, new-postings diff (wrong version 2), seeded runs, outputs, and the no-key stop."""

import json
import shutil

import pytest

from agent import report
from agent.__main__ import main
from agent.errors import ConfigError, RawInputError, StateError
from agent.run import RunOptions, run
from support import BOARD_NO_CONTENT, BOARD_SMALL, RUN_DATE, FakeFactory, FakeOpener

ALL_IDS = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]


def seeded(config, **kwargs):
    return run(RunOptions(config=config, run_date=RUN_DATE, from_raw=BOARD_SMALL, no_claude=True), **kwargs)


def write_state(config, ids):
    config["state_path"].parent.mkdir(parents=True, exist_ok=True)
    config["state_path"].write_text(json.dumps(ids))


def read_state(config):
    return json.loads(config["state_path"].read_text())


# ---------- Baseline ----------

def test_missing_state_file_is_a_baseline(make_config):
    config = make_config()
    summary = seeded(config)
    assert summary["baseline"] is True
    assert summary["new_count"] == 0 and summary["records"] == []
    assert summary["postings_fetched"] == 8
    assert read_state(config) == ALL_IDS


def test_empty_state_list_makes_every_posting_new(make_config):
    config = make_config()
    write_state(config, [])
    summary = seeded(config)
    assert summary["baseline"] is False
    assert [r["posting_id"] for r in summary["records"]] == ALL_IDS


# ---------- Wrong version 2 ----------

def test_v01_two_runs_on_same_raw_second_reports_zero(make_config):
    config = make_config()
    assert seeded(config)["new_count"] == 0     # baseline
    assert seeded(config)["new_count"] == 0


def test_seen_subset_then_rerun_reports_only_remaining_then_zero(make_config):
    config = make_config()
    write_state(config, [1001, 1003, 1005])
    first = seeded(config)
    assert [r["posting_id"] for r in first["records"]] == [1002, 1004, 1006, 1007, 1008]
    second = seeded(config)
    assert second["new_count"] == 0 and second["records"] == []


def test_ids_are_never_removed(make_config):
    config = make_config()
    write_state(config, [999, 1001])
    seeded(config)
    assert read_state(config) == sorted([999] + ALL_IDS)


def test_duplicate_id_on_board_is_reported_once(tmp_path, make_config):
    board = json.loads(BOARD_SMALL.read_text())
    board["jobs"].append(dict(board["jobs"][0]))
    raw = tmp_path / "dup.json"
    raw.write_text(json.dumps(board))
    config = make_config()
    write_state(config, [])
    summary = run(RunOptions(config=config, run_date=RUN_DATE, from_raw=raw, no_claude=True))
    assert [r["posting_id"] for r in summary["records"]] == ALL_IDS


def test_state_is_written_only_after_outputs(make_config, monkeypatch):
    config = make_config()
    write_state(config, [1001])

    def broken_write(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(report, "write", broken_write)
    with pytest.raises(OSError):
        seeded(config)
    assert read_state(config) == [1001]


def test_corrupt_state_file_stops_before_fetch(make_config):
    config = make_config()
    config["state_path"].parent.mkdir(parents=True)
    config["state_path"].write_text('{"ids": [1]}')
    opener = FakeOpener(BOARD_SMALL.read_bytes())
    with pytest.raises(StateError):
        run(RunOptions(config=config, run_date=RUN_DATE, no_claude=True), opener=opener)
    assert opener.urls == []


# ---------- Seeded vs live ----------

def test_seeded_run_is_labeled_and_saves_no_raw(tmp_path, make_config):
    config = make_config()
    opener = FakeOpener(b"should never be read")
    summary = seeded(config, opener=opener)
    assert summary["mode"] == "seeded"
    assert summary["raw_path"].endswith("board_small.json")
    assert opener.urls == []
    assert not (tmp_path / "raw").exists()


def test_live_run_saves_raw_and_reports_its_path(tmp_path, make_config):
    config = make_config()
    summary = run(RunOptions(config=config, run_date=RUN_DATE, no_claude=True),
                  opener=FakeOpener(BOARD_SMALL.read_bytes()))
    assert summary["mode"] == "live"
    saved = list((tmp_path / "raw").iterdir())
    assert len(saved) == 1 and saved[0].read_bytes() == BOARD_SMALL.read_bytes()
    assert summary["raw_path"] == str(saved[0].resolve())  # outside the project folder in tests


def test_raw_file_without_content_stops_with_no_output(tmp_path, make_config):
    config = make_config()
    write_state(config, [])
    with pytest.raises(RawInputError, match="content"):
        run(RunOptions(config=config, run_date=RUN_DATE, from_raw=BOARD_NO_CONTENT, no_claude=True))
    assert not (tmp_path / "out").exists()
    assert read_state(config) == []


def test_live_response_without_content_is_saved_then_stops(tmp_path, make_config):
    config = make_config()
    with pytest.raises(RawInputError):
        run(RunOptions(config=config, run_date=RUN_DATE, no_claude=True),
            opener=FakeOpener(BOARD_NO_CONTENT.read_bytes()))
    assert len(list((tmp_path / "raw").iterdir())) == 1
    assert not (tmp_path / "out").exists()


# ---------- Claude on/off and the API key ----------

def test_no_api_key_without_no_claude_stops_before_fetch(make_config):
    opener = FakeOpener(BOARD_SMALL.read_bytes())
    with pytest.raises(ConfigError, match="ANTHROPIC_API_KEY"):
        run(RunOptions(config=make_config(), run_date=RUN_DATE), env={}, opener=opener)
    assert opener.urls == []


def test_no_claude_never_builds_a_client(make_config):
    config = make_config()
    write_state(config, [])
    factory = FakeFactory()
    summary = seeded(config, client_factory=factory, env={"ANTHROPIC_API_KEY": "k"})
    assert factory.calls == []
    assert summary["claude"] == "off (--no-claude)"
    assert all(r["claude_valid"] is None and r["claude_verdict"] is None for r in summary["records"])


def test_baseline_makes_no_claude_calls(make_config):
    factory = FakeFactory()
    run(RunOptions(config=make_config(), run_date=RUN_DATE, from_raw=BOARD_SMALL),
        env={"ANTHROPIC_API_KEY": "k"}, client_factory=factory)
    assert factory.calls == []


# ---------- Outputs ----------

def test_outputs_have_contract_fields(tmp_path, make_config):
    config = make_config()
    write_state(config, [])
    summary = seeded(config)
    out_json = sorted((tmp_path / "out").glob("*.json"))
    out_md = sorted((tmp_path / "out").glob("*.md"))
    assert len(out_json) == 1 and len(out_md) == 1
    written = json.loads(out_json[0].read_text())
    for key in ("run_date", "mode", "postings_fetched", "new_count", "raw_path", "records"):
        assert key in written
    record = written["records"][0]
    for key in ("posting_id", "title", "url", "location", "date_used", "rule_verdict", "rule_justification",
                "claude_verdict", "claude_justification", "claude_valid", "claude_model"):
        assert key in record
    assert record["date_used"] == {"field": "first_published", "value": "2026-10-20T10:00:00-04:00"}
    by_id = {r["posting_id"]: r for r in written["records"]}
    assert by_id[1008]["date_used"]["field"] == "updated_at"
    md = out_md[0].read_text()
    assert "seeded" in md and "**record**" in md and "**model judgment**" in md
    assert "Cole" not in md and "example.com" not in md and "555" not in md


def test_two_runs_in_same_second_keep_both_outputs(tmp_path, make_config):
    config = make_config()
    write_state(config, [])
    seeded(config)
    seeded(config)
    assert len(list((tmp_path / "out").glob("*.json"))) == 2


# ---------- CLI ----------

def test_cli_seeded_run_with_injected_date(tmp_path, capsys):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({
        "state_path": str(tmp_path / "state" / "seen_ids.json"),
        "raw_dir": str(tmp_path / "raw"),
        "out_dir": str(tmp_path / "out"),
    }))
    shutil.copy(BOARD_SMALL, tmp_path / "board.json")
    args = ["--config", str(config_path), "--from-raw", str(tmp_path / "board.json"),
            "--no-claude", "--run-date", "2026-10-27"]
    assert main(args) == 0
    assert "seeded run, run date 2026-10-27 (baseline)" in capsys.readouterr().out


def test_cli_error_exits_2_without_traceback(tmp_path, capsys):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"state_path": str(tmp_path / "s.json"), "out_dir": str(tmp_path / "out")}))
    assert main(["--config", str(config_path), "--from-raw", str(BOARD_NO_CONTENT), "--no-claude"]) == 2
    assert "error:" in capsys.readouterr().err
