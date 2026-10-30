"""The Claude judge, with a fake client: what Claude receives, labels, invalid replies."""

import hashlib
import json

import pytest

from agent.claude_judge import DEFAULT_PROMPT_PATH, build_request, judge, load_prompt
from agent.errors import ClaudeAuthError, ConfigError
from agent.persona import RULE_FIELDS, load_rule_fields
from agent.run import RunOptions, run
from agent.text import strip_html
from support import (BOARD_SMALL, PERSONA, PROJECT_DIR, RUN_DATE, FakeAPIStatusError, FakeClient,
                     FakeFactory, FakeOpener, FakeResponse, posting, valid_reply)

FIELDS = load_rule_fields(PERSONA)


def request_for(p):
    return build_request(p, strip_html(p["content"]), FIELDS, RUN_DATE, "claude-sonnet-5-5", 16000)


def test_request_carries_only_rule_fields_and_no_contact_data(persona_data):
    request = request_for(posting())
    serialized = json.dumps(request, ensure_ascii=False)
    for secret in (persona_data["personal"]["name"], persona_data["personal"]["email"],
                   persona_data["personal"]["phone"], persona_data["personal"]["location"],
                   "Northeastern", "Example Logistics"):
        assert secret not in serialized
    payload = json.loads(request["messages"][0]["content"])
    assert set(payload) == {"run_date", "resume_rule_fields", "posting"}
    assert set(payload["resume_rule_fields"]) == set(RULE_FIELDS)
    assert set(payload["posting"]) == {"posting_id", "title", "location.name", "first_published",
                                       "updated_at", "content"}
    assert "<" not in payload["posting"]["content"] and "&lt;" not in payload["posting"]["content"]


def test_request_uses_configured_model_and_no_fallback():
    request = request_for(posting())
    assert request["model"] == "claude-sonnet-5-5"
    assert "fallbacks" not in request and "betas" not in request
    assert request["output_config"]["format"]["type"] == "json_schema"
    for rule in ("R1", "R2", "R3", "R4", "R5", "R6"):
        assert rule in request["system"]


def test_default_prompt_is_baseline_file_sent_byte_for_byte():
    path = PROJECT_DIR / "prompts" / "baseline.txt"
    assert DEFAULT_PROMPT_PATH == path
    text, sha = load_prompt()
    assert text == path.read_bytes().decode("utf-8")
    assert sha == hashlib.sha256(path.read_bytes()).hexdigest()
    assert request_for(posting())["system"] == text
    for field in RULE_FIELDS:
        assert field in text


def test_request_sends_the_given_prompt_text_unchanged():
    p = posting()
    request = build_request(p, strip_html(p["content"]), FIELDS, RUN_DATE, "claude-sonnet-5-5", 16000,
                            "  One changed prompt.\n")
    assert request["system"] == "  One changed prompt.\n"


@pytest.mark.parametrize("content", [None, b"", b"  \n", b"\xff\xfe not utf-8"])
def test_missing_empty_or_non_utf8_prompt_file_stops(tmp_path, content):
    path = tmp_path / "prompt.txt"
    if content is not None:
        path.write_bytes(content)
    with pytest.raises(ConfigError):
        load_prompt(path)


def test_valid_reply_is_labeled_model_judgment(tmp_path):
    reply_path = tmp_path / "42.json"
    result = judge(FakeClient(), request_for(posting()), 42, reply_path)
    assert result["claude_valid"] is True
    assert result["claude_verdict"] == "relevant"
    assert result["claude_label"] == "model judgment"
    assert result["claude_model"] == "claude-sonnet-5-5"
    assert reply_path.exists()


@pytest.mark.parametrize("response", [
    FakeResponse("```json\n" + valid_reply(42) + "\n```"),
    FakeResponse(json.dumps({**json.loads(valid_reply(42)), "extra": 1})),
    FakeResponse(valid_reply(42, verdict="maybe")),
    FakeResponse(valid_reply(43)),
    FakeResponse("I think this posting is relevant."),
    FakeResponse('{"posting_id": "42", "verdict": "relev'),            # truncated
    FakeResponse(None),                                                 # no text block
    FakeResponse(valid_reply(42), stop_reason="refusal"),               # refusal counts as invalid
])
def test_invalid_reply_is_saved_unrepaired_and_marked_invalid(tmp_path, response):
    reply_path = tmp_path / "42.json"
    result = judge(FakeClient(lambda pid: response), request_for(posting()), 42, reply_path)
    assert result["claude_valid"] is False
    assert result["claude_verdict"] is None and result["claude_justification"] is None
    assert result["claude_label"] == "model judgment"
    assert result["claude_invalid_reason"]
    saved = json.loads(reply_path.read_text())
    assert saved["content"] == [{"type": b.type, "text": b.text} for b in response.content]


def test_api_error_is_marked_invalid(tmp_path):
    result = judge(FakeClient(lambda pid: RuntimeError("connection reset")), request_for(posting()),
                   42, tmp_path / "42.json")
    assert result["claude_valid"] is False and "RuntimeError" in result["claude_invalid_reason"]


def test_http_401_raises_instead_of_marking_invalid(tmp_path):
    reply_path = tmp_path / "replies" / "42.json"
    with pytest.raises(ClaudeAuthError, match="401"):
        judge(FakeClient(lambda pid: FakeAPIStatusError(401)), request_for(posting()), 42, reply_path)
    assert not reply_path.parent.exists()


@pytest.mark.parametrize("status", [400, 403, 429, 500])
def test_other_http_errors_are_still_marked_invalid(tmp_path, status):
    result = judge(FakeClient(lambda pid: FakeAPIStatusError(status)), request_for(posting()),
                   42, tmp_path / "42.json")
    assert result["claude_valid"] is False
    assert result["claude_invalid_reason"] == f"API call failed: FakeAPIStatusError (HTTP {status})"


def test_run_stops_at_first_401_with_no_output_and_state_unchanged(tmp_path, make_config):
    config = make_config()
    config["state_path"].parent.mkdir(parents=True)
    config["state_path"].write_text("[]")
    client = FakeClient(lambda pid: FakeAPIStatusError(401))
    with pytest.raises(ClaudeAuthError):
        run(RunOptions(config=config, run_date=RUN_DATE, from_raw=BOARD_SMALL),
            env={"ANTHROPIC_API_KEY": "bad-key"}, client_factory=FakeFactory(client))
    assert len(client.messages.calls) == 1
    assert not config["out_dir"].exists()
    assert config["state_path"].read_text() == "[]"


def test_cli_reports_401_and_exits_2(make_config, monkeypatch, capsys):
    import agent.__main__ as cli
    config = make_config()
    config["state_path"].parent.mkdir(parents=True)
    config["state_path"].write_text("[]")
    monkeypatch.setattr(cli, "load_config", lambda path=None: config)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "bad-key")
    factory = FakeFactory(FakeClient(lambda pid: FakeAPIStatusError(401)))
    monkeypatch.setattr(cli, "run", lambda options: run(options, client_factory=factory))
    assert cli.main(["--from-raw", str(BOARD_SMALL), "--run-date", "2026-10-27"]) == 2
    assert "HTTP 401" in capsys.readouterr().err


def test_run_labels_both_judges_and_never_writes_the_api_key(tmp_path, make_config):
    secret = "sk-ant-test-SECRET-do-not-write"
    config = make_config()
    config["state_path"].parent.mkdir(parents=True)
    config["state_path"].write_text("[]")
    factory = FakeFactory()
    summary = run(RunOptions(config=config, run_date=RUN_DATE),
                  env={"ANTHROPIC_API_KEY": secret}, opener=FakeOpener(BOARD_SMALL.read_bytes()),
                  client_factory=factory)
    assert factory.calls == [(secret, "https://api.anthropic.com")]
    assert summary["new_count"] == 8
    for record in summary["records"]:
        assert record["rule_label"] == "record"
        assert record["claude_label"] == "model judgment"
        assert record["claude_valid"] is True
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert secret not in path.read_text(encoding="utf-8", errors="replace"), path


def test_one_invalid_reply_does_not_block_the_others(tmp_path, make_config):
    config = make_config()
    config["state_path"].parent.mkdir(parents=True)
    config["state_path"].write_text("[]")
    client = FakeClient(lambda pid: FakeResponse("oops") if pid == "1003" else FakeResponse(valid_reply(pid)))
    summary = run(RunOptions(config=config, run_date=RUN_DATE), env={"ANTHROPIC_API_KEY": "k"},
                  opener=FakeOpener(BOARD_SMALL.read_bytes()), client_factory=FakeFactory(client))
    valid = {r["posting_id"]: r["claude_valid"] for r in summary["records"]}
    assert valid[1003] is False
    assert all(v for pid, v in valid.items() if pid != 1003)
