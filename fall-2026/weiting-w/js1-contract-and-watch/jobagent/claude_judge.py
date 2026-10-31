"""The second judge: Claude under a prompt contract.

Everything this module produces is labelled ``"kind": "judgment"``. It is not a
record: the same prompt and the same posting can come back differently, which
is what the sampling report measures. The agent never resolves a disagreement
between this judge and the rule judge; it reports both.

Two ways to get a judgment, and both end up in the same shape:

* ``call_model`` sends the rendered prompt to the Anthropic Messages API, for
  anybody with a key who wants to reproduce the runs;
* ``from_transcript`` reads a recorded response that was already obtained, so
  the reports in this repository can be rebuilt from evidence with no network
  and no key at all.

The transcripts in ``experiments/results/`` were produced by the second route.
``experiments/results/PROVENANCE.md`` says exactly how and when.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from .errors import FetchFailed, ValidatorRejected
from .validator import validate

# The board allow-list in allowlist.py covers the watch. The model is a second,
# separate action surface and gets its own single-host allow-list here, so that
# neither can be widened by editing the other. See CONTRACT.md §7, amendment
# 2026-10-21.
MODEL_HOSTS = frozenset({"api.anthropic.com"})
MODEL_ENDPOINT = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-5"

RESUME_FIELDS_IN_PROMPT = (
    "title_block",
    "target_title_phrases",
    "target_job_families",
    "locations_ok",
    "remote_ok",
)

POSTING_FIELDS_IN_PROMPT = ("id", "title", "location", "metadata")


def resume_block(resume: dict) -> str:
    lines = []
    for field in RESUME_FIELDS_IN_PROMPT:
        lines.append(f"{field} = {json.dumps(resume[field], ensure_ascii=False)}")
    return "\n".join(lines)


def posting_block(posting: dict) -> str:
    """The posting as the model sees it.

    `metadata` entries keep their **positions** and lose only their internal
    `id`, because the model is asked to cite a path like ``metadata[6].value``
    and the validator resolves that path against the full posting. Dropping or
    reordering entries here would shift the indices and turn correct citations
    into validator rejections — an artefact of the harness that would look like
    a model error.
    """
    trimmed = {}
    for key in POSTING_FIELDS_IN_PROMPT:
        if key not in posting:
            continue
        if key == "metadata" and isinstance(posting[key], list):
            trimmed[key] = [
                {"name": e.get("name"), "value": e.get("value")}
                for e in posting[key]
                if isinstance(e, dict)
            ]
        else:
            trimmed[key] = posting[key]
    return json.dumps(trimmed, indent=1, ensure_ascii=False, sort_keys=True)


def render_prompt(template_path: str | Path, posting: dict, resume: dict) -> str:
    template = Path(template_path).read_text(encoding="utf-8")
    return template.format(
        resume_block=resume_block(resume), posting_block=posting_block(posting)
    )


def _check_model_url(url: str) -> str:
    parts = urlsplit(url)
    host = (parts.hostname or "").casefold()
    if parts.scheme != "https" or host not in MODEL_HOSTS:
        raise FetchFailed(f"model host {host!r} is not allowed")
    return url


def call_model(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 700) -> str:
    """Send one prompt and return the model's text, byte-for-byte."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise FetchFailed(
            "ANTHROPIC_API_KEY is not set; use --transcript to replay recorded "
            "judgments instead"
        )
    _check_model_url(MODEL_ENDPOINT)
    body = json.dumps(
        {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 1,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        MODEL_ENDPOINT,
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - network dependent
        raise FetchFailed(f"HTTP {exc.code} from the model API") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network dependent
        raise FetchFailed(f"could not reach the model API: {exc.reason}") from exc
    parts = [b.get("text", "") for b in payload.get("content", []) if isinstance(b, dict)]
    return "".join(parts)


def wrap(raw_text: str, posting: dict, resume: dict, *, model: str,
         retrieved_at: str, prompt_contract: str, transport: str) -> dict:
    """Validate one model response and wrap it as a labelled judgment."""
    judgment = {
        "kind": "judgment",
        "model": model,
        "transport": transport,
        "retrieved_at": retrieved_at,
        "prompt_contract": prompt_contract,
        "raw": raw_text,
    }
    try:
        parsed = validate(raw_text, posting, resume)
    except ValidatorRejected as exc:
        judgment.update(
            validator="reject",
            validator_error=str(exc),
            verdict=None,
            gate_failed=None,
            justification=[],
            confidence=None,
        )
        return judgment
    judgment.update(
        validator="pass",
        validator_error=None,
        verdict=parsed["verdict"],
        gate_failed=parsed["gate_failed"],
        justification=parsed["justification"],
        confidence=parsed["confidence"],
    )
    return judgment


def from_transcript(entry: dict, posting: dict, resume: dict) -> dict:
    """Wrap one recorded response. ``entry`` is a row of a transcript file."""
    return wrap(
        entry["raw"],
        posting,
        resume,
        model=entry["model"],
        retrieved_at=entry["retrieved_at"],
        prompt_contract=entry["prompt_contract"],
        transport=entry.get("transport", "recorded"),
    )


def load_transcript(path: str | Path) -> dict[str, list[dict]]:
    """Index a transcript file by posting id (as a string)."""
    rows = json.loads(Path(path).read_text(encoding="utf-8"))["responses"]
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(str(row["posting_id"]), []).append(row)
    return out
