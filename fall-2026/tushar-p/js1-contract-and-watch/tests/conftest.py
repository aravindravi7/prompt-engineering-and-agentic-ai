"""Shared test setup. Every test runs offline: any socket use fails the test."""

import json
import socket

import pytest

from agent.config import DEFAULTS
from support import PERSONA


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("network access attempted in an offline test")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)


@pytest.fixture
def persona_data() -> dict:
    return json.loads(PERSONA.read_text(encoding="utf-8"))


@pytest.fixture
def make_config(tmp_path):
    """Config pointing every path into tmp_path, so tests never touch state/, raw/ or out/."""

    def build(**overrides) -> dict:
        config = dict(DEFAULTS)
        config.update(
            persona_path=PERSONA,
            state_path=tmp_path / "state" / "seen_ids.json",
            raw_dir=tmp_path / "raw",
            out_dir=tmp_path / "out",
        )
        config.update(overrides)
        return config

    return build
