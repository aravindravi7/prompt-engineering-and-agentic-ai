"""Prompt experiment and sampling scripts, with a fake client: scoring, held-out guard, 401 stop."""

import hashlib
import itertools
import json

import pytest

from agent.claude_judge import load_prompt
from agent.errors import ClaudeAuthError
from experiments import run_prompt, sample
from experiments.common import ExperimentError, load_labels, split_ids
from experiments.run_prompt import run_experiment
from experiments.sample import SAMPLE_IDS, run_sampling
from support import PROJECT_DIR, FakeAPIStatusError, FakeClient, FakeFactory, FakeResponse, valid_reply

BASELINE = PROJECT_DIR / "prompts" / "baseline.txt"
LABELS = load_labels()


def label_of(pid) -> str:
    return LABELS[int(pid)]["label"]


def agreeing_client(overrides=None) -> FakeClient:
    """Replies with my label, except where `overrides` maps a posting id to another response."""
    overrides = overrides or {}
    return FakeClient(lambda pid: overrides.get(int(pid)) or FakeResponse(valid_reply(pid, label_of(pid))))


def experiment(tmp_path, make_config, client, split="dev", **kwargs):
    return run_experiment(kwargs.pop("prompt", BASELINE), split, env={"ANTHROPIC_API_KEY": "k"},
                          client_factory=FakeFactory(client), config=make_config(),
                          results_dir=tmp_path / "results", **kwargs)


def test_heldout_is_refused_without_final_before_any_call(tmp_path, make_config):
    factory = FakeFactory()
    with pytest.raises(ExperimentError, match="--final"):
        run_experiment(BASELINE, "held-out", env={"ANTHROPIC_API_KEY": "k"}, client_factory=factory,
                       config=make_config(), results_dir=tmp_path / "results")
    assert factory.calls == []
    assert not (tmp_path / "results").exists()


def test_cli_refuses_heldout_without_final(capsys):
    assert run_prompt.main(["--prompt", str(BASELINE), "--split", "held-out"]) == 2
    assert "--final" in capsys.readouterr().err


def test_dev_run_sends_the_prompt_file_and_fixed_inputs(tmp_path, make_config):
    prompt = tmp_path / "revised.txt"
    prompt.write_text("A revised prompt.\n", encoding="utf-8")
    client = agreeing_client()
    summary = experiment(tmp_path, make_config, client, prompt=prompt)
    calls = client.messages.calls
    dev = split_ids("dev")
    assert [json.loads(c["messages"][0]["content"])["posting"]["posting_id"] for c in calls] == [str(i) for i in dev]
    for call in calls:
        payload = json.loads(call["messages"][0]["content"])
        assert call["system"] == "A revised prompt.\n"
        assert len(call["messages"]) == 1
        assert payload["run_date"] == "2026-10-27"
        assert payload["posting"]["content"]  # read from the raw file, not empty
        assert call["output_config"]["format"]["type"] == "json_schema"
    assert summary["prompt_sha256"] == hashlib.sha256(b"A revised prompt.\n").hexdigest()
    assert summary["passes"] == 10 and summary["invalid_count"] == 0
    name = summary["output_json"].rsplit("/", 1)[-1]
    assert name.startswith("revised-dev-2026-") and name.endswith(".json")
    assert summary["output_markdown"] == summary["output_json"][:-5] + ".md"


def test_pass_is_exact_match_and_invalid_is_a_miss(tmp_path, make_config):
    client = agreeing_client({
        8314283: FakeResponse(valid_reply(8314283, "cannot_tell")),   # labeled relevant: a miss
        8257892: FakeResponse("oops"),                               # invalid: a miss
        8209307: FakeResponse(valid_reply(8209307, "relevant")),      # labeled not_relevant: a miss
    })
    summary = experiment(tmp_path, make_config, client)
    rows = {r["posting_id"]: r for r in summary["rows"]}
    assert summary["passes"] == 7 and summary["total"] == 10 and summary["invalid_count"] == 1
    assert rows[8314283] | {"reply_path": None} == {
        "posting_id": 8314283, "my_label": "relevant", "claude_verdict": "cannot_tell", "match": "no",
        "valid": "yes", "claude_model": "claude-sonnet-5-5", "claude_invalid_reason": None, "reply_path": None,
    }
    assert rows[8257892]["valid"] == "no" and rows[8257892]["match"] == "no"
    assert rows[8257892]["claude_verdict"] is None
    assert rows[8160776]["match"] == "yes"

    written = json.loads(open(summary["output_json"]).read())
    assert written["passes"] == 7 and written["rows"] == summary["rows"]
    md = open(summary["output_markdown"]).read()
    _, sha = load_prompt(BASELINE)
    for text in ("**7 / 10**", "Invalid replies: 1", "claude-sonnet-5-5", sha, "API default"):
        assert text in md


def test_heldout_final_runs_are_each_logged(tmp_path, make_config):
    first = experiment(tmp_path, make_config, agreeing_client(), split="held-out", final=True)
    second = experiment(tmp_path, make_config, agreeing_client(), split="held-out", final=True)
    log = (tmp_path / "results" / "HELDOUT-LOG.md").read_text()
    rows = [line for line in log.splitlines() if "prompts/baseline.txt" in line]
    assert len(rows) == 2
    for row, summary in zip(rows, (first, second)):
        assert summary["prompt_sha256"] in row
        assert summary["timestamp"][:19] in row
        assert "10/10 passes" in row
    assert first["output_json"] != second["output_json"]


def test_401_at_first_call_stops_with_no_results_and_logs_heldout(tmp_path, make_config):
    client = FakeClient(lambda pid: FakeAPIStatusError(401))
    with pytest.raises(ClaudeAuthError):
        experiment(tmp_path, make_config, client, split="held-out", final=True)
    assert len(client.messages.calls) == 1
    assert list((tmp_path / "results").glob("*.json")) == []
    assert "stopped: ClaudeAuthError" in (tmp_path / "results" / "HELDOUT-LOG.md").read_text()


def test_missing_api_key_stops_before_any_call(tmp_path, make_config):
    factory = FakeFactory()
    with pytest.raises(Exception, match="ANTHROPIC_API_KEY"):
        run_experiment(BASELINE, "dev", env={}, client_factory=factory, config=make_config(),
                       results_dir=tmp_path / "results")
    assert factory.calls == []


def test_later_label_row_is_a_correction_and_wins(tmp_path):
    path = tmp_path / "labels.csv"
    path.write_text("posting_id,split,title,label\n1,dev,A,relevant\n2,dev,B,not_relevant\n"
                    "1,dev,A,cannot_tell\n", encoding="utf-8")
    assert load_labels(path) == {1: {"label": "cannot_tell", "split": "dev"},
                                 2: {"label": "not_relevant", "split": "dev"}}
    path.write_text("posting_id,split,title,label\n1,dev,A,\n", encoding="utf-8")
    with pytest.raises(ExperimentError):
        load_labels(path)


def sampling(tmp_path, make_config, client, **kwargs):
    return run_sampling(BASELINE, env={"ANTHROPIC_API_KEY": "k"}, client_factory=FakeFactory(client),
                        config=make_config(), results_dir=tmp_path / "results", **kwargs)


def test_sampling_postings_are_the_five_dev_ids():
    assert SAMPLE_IDS == (8314283, 8160776, 8257892, 8128745, 7947546)
    assert set(SAMPLE_IDS) <= set(split_ids("dev"))


def test_sampling_makes_fresh_calls_and_counts_verdicts(tmp_path, make_config):
    flip = itertools.cycle(["relevant", "cannot_tell"])
    client = FakeClient(lambda pid: FakeResponse(valid_reply(pid, next(flip))) if pid == "8314283"
                        else FakeResponse("oops") if pid == "8128745"
                        else FakeResponse(valid_reply(pid, label_of(pid))))
    summary = sampling(tmp_path, make_config, client, repeats=4)

    calls = client.messages.calls
    assert len(calls) == 20 and len(summary["calls"]) == 20
    for call in calls:
        assert [m["role"] for m in call["messages"]] == ["user"]
        assert "temperature" not in call
    assert len({id(c["messages"]) for c in calls}) == 20  # no message list is reused

    by_id = {p["posting_id"]: p for p in summary["postings"]}
    assert by_id[8314283]["counts"] == {"relevant": 2, "not_relevant": 0, "cannot_tell": 2, "invalid": 0}
    assert by_id[8314283]["all_agree"] == "no" and by_id[8314283]["matches_label"] == 2
    assert by_id[8128745]["counts"]["invalid"] == 4 and by_id[8128745]["all_agree"] == "no"
    assert by_id[8160776]["all_agree"] == "yes" and by_id[8160776]["my_label"] == "not_relevant"
    assert summary["temperature"] == "not set in the request (API default)"
    assert summary["model_requested"] == "claude-sonnet-5-5"
    assert summary["models_in_responses"] == ["claude-sonnet-5-5"]
    assert [(c["posting_id"], c["repeat"]) for c in summary["calls"][:5]] == [
        (8314283, 1), (8314283, 2), (8314283, 3), (8314283, 4), (8160776, 1)]
    md = open(summary["output_markdown"]).read()
    assert "API default" in md and "claude-sonnet-5-5" in md and summary["prompt_sha256"] in md


def test_sampling_stops_at_first_401(tmp_path, make_config):
    client = FakeClient(lambda pid: FakeAPIStatusError(401))
    with pytest.raises(ClaudeAuthError):
        sampling(tmp_path, make_config, client)
    assert len(client.messages.calls) == 1
    assert list((tmp_path / "results").glob("sampling-*")) == []


def test_sampling_refuses_non_dev_postings_and_zero_repeats(tmp_path, make_config):
    with pytest.raises(ExperimentError, match="dev"):
        sampling(tmp_path, make_config, agreeing_client(), ids=(7982720,))
    with pytest.raises(ExperimentError, match="repeats"):
        sampling(tmp_path, make_config, agreeing_client(), repeats=0)


def test_sample_cli_reports_401_and_exits_2(tmp_path, monkeypatch, capsys):
    factory = FakeFactory(FakeClient(lambda pid: FakeAPIStatusError(401)))
    original = sample.run_sampling
    monkeypatch.setenv("ANTHROPIC_API_KEY", "bad-key")
    monkeypatch.setattr(sample, "run_sampling",
                        lambda prompt, repeats: original(prompt, repeats, client_factory=factory,
                                                         results_dir=tmp_path / "results"))
    assert sample.main(["--prompt", str(BASELINE), "--repeats", "4"]) == 2
    assert "HTTP 401" in capsys.readouterr().err
