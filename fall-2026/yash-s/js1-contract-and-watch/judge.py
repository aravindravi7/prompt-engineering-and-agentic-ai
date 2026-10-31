#!/usr/bin/env python3
"""Job-Search Agent 1: the two judges (CONTRACT.md v3, sections 2 and 4).

RECORD    my written rule (section 4). Anyone can recompute it by hand.
JUDGMENT  Claude under the prompt contract in prompts/. An opinion, labeled as one.

A JUDGMENT never replaces a RECORD. Claude's answer is checked by validate() and is
either valid, invalid (rejected, never fixed), or unavailable.

Claude is called through the Claude Code CLI with every tool turned off, no MCP
servers, no saved session, the prompt file as the whole system prompt, and an empty
temporary folder as the working directory, so no CLAUDE.md or project file is loaded.
Python 3 standard library only.
"""
import hashlib
import html
import json
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# RECORD rule, CONTRACT.md v3 section 4
TITLE_PHRASES = ("AI Engineer", "ML Engineer", "Machine Learning Engineer",
                 "Applied AI Engineer", "Data Engineer", "GenAI Engineer")
SWE_PHRASE = "Software Engineer"
SWE_WORDS = ("AI", "ML", "GenAI", "Machine Learning")
SKILL_GROUPS = ("languages", "data_bi", "backend_automation", "database_cloud")
EXCLUDED_SKILLS = ("Databricks", "Unity Catalog")       # the company's own product names
MIN_SKILLS = 2
BLOCKER = "security clearance"

# JUDGMENT contract, CONTRACT.md v3 section 2 (location added by the v3 note of 2026-10-31)
RESUME_FIELDS = ("skills.languages", "skills.data_bi", "skills.backend_automation",
                 "skills.database_cloud", "experience", "projects")
POSTING_FIELDS = ("title", "content", "location")
ANSWER_KEYS = ("posting_id", "verdict", "resume_fields", "posting_fields", "matched_terms", "reason")
VERDICTS = ("relevant", "not relevant")
DEFAULT_MODEL = "claude-sonnet-5-5"
JUDGMENT_LABEL = "JUDGMENT: Claude's opinion under the prompt contract, not a fact"


def clean_text(content):
    """Greenhouse sends entity-escaped HTML: unescape, drop tags, unescape again."""
    t = html.unescape(content or "")
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def has_phrase(phrase, text):
    """Whole word or whole phrase, ignoring capital letters."""
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text or "", re.I) is not None


def counted_skills(resume):
    """(résumé field path, skill) for every skill Rule 2 counts, each skill once."""
    excluded = {s.lower() for s in EXCLUDED_SKILLS}
    out, seen = [], set()
    for g in SKILL_GROUPS:
        for s in resume["skills"].get(g, []):
            if s.lower() not in excluded and s.lower() not in seen:
                seen.add(s.lower())
                out.append((f"skills.{g}", s))
    return out


def record_verdict(posting, resume):
    title = posting.get("title") or ""
    text = clean_text(posting.get("content"))

    phrases = [p for p in TITLE_PHRASES if has_phrase(p, title)]
    swe_words = [w for w in SWE_WORDS if has_phrase(w, title)] if has_phrase(SWE_PHRASE, title) else []
    rule1 = bool(phrases) or bool(swe_words)

    skills = counted_skills(resume)
    hits = [{"skill": s, "resume_field": f} for f, s in skills if has_phrase(s, text)]
    rule2 = len(hits) >= MIN_SKILLS

    found_in = [name for name, t in (("title", title), ("content", text)) if has_phrase(BLOCKER, t)]
    rule3 = not found_in

    verdict = "relevant" if rule1 and rule2 and rule3 else "not relevant"
    t = title.strip()
    if phrases:
        r1 = f"title {t!r} contains {', '.join(repr(p) for p in phrases)} (rule 1 passed)"
    elif swe_words:
        r1 = f"title {t!r} contains 'Software Engineer' with {', '.join(repr(w) for w in swe_words)} (rule 1 passed)"
    else:
        r1 = f"title {t!r} contains none of the rule 1 phrases (rule 1 failed)"
    if hits:
        found = ", ".join(f"{h['skill']} ({h['resume_field']})" for h in hits)
        r2 = f"content contains {len(hits)} of {len(skills)} counted résumé skills: {found}"
    else:
        r2 = f"content contains 0 of {len(skills)} counted résumé skills from {', '.join(f'skills.{g}' for g in SKILL_GROUPS)}"
    r2 += f" (rule 2 {'passed' if rule2 else 'failed'}, needs {MIN_SKILLS})"
    r3 = (f"{BLOCKER!r} not found in title or content (rule 3 passed)" if rule3
          else f"{BLOCKER!r} found in {' and '.join(found_in)} (rule 3 failed)")

    return {
        "judge": "RECORD",
        "posting_id": posting["id"],
        "verdict": verdict,
        "checks": {
            "rule1_title": {"posting_field": "title", "passed": rule1,
                            "matched_phrases": phrases, "software_engineer_with": swe_words},
            "rule2_skills": {"posting_field": "content", "passed": rule2, "needed": MIN_SKILLS,
                             "matched": hits, "excluded": list(EXCLUDED_SKILLS)},
            "rule3_blocker": {"posting_fields": ["title", "content"], "passed": rule3,
                              "phrase": BLOCKER, "found_in": found_in},
        },
        "reason": "; ".join([r1, r2, r3]),
    }


def location_name(posting):
    return ((posting.get("location") or {}).get("name") or "").strip()


def claude_view(posting, resume):
    """Everything Claude is shown: one posting and the six allowed résumé fields. No contact details."""
    return {
        "job_posting": {"posting_id": posting["id"], "title": (posting.get("title") or "").strip(),
                        "location": location_name(posting), "content": clean_text(posting.get("content"))},
        "resume": {
            "skills": {g: resume["skills"].get(g, []) for g in SKILL_GROUPS},
            "experience": resume.get("experience", []),
            "projects": resume.get("projects", []),
        },
    }


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v)


def field_text(view, side, path):
    """The text of one named field, as Claude was shown it."""
    if side == "posting":
        return view["job_posting"][path]
    node = view["resume"]
    for part in path.split("."):
        node = node[part]
    return " | ".join(_strings(node))


def validate(answer_text, posting, view):
    """(answer, errors). A non-empty errors list means invalid: the answer is rejected, not fixed."""
    try:
        a = json.loads(answer_text)
    except (TypeError, ValueError):
        return None, ["not a single JSON object (extra text, code fences, or broken JSON)"]
    if not isinstance(a, dict):
        return None, ["the answer is JSON but not an object"]
    errors = []
    missing = [k for k in ANSWER_KEYS if k not in a]
    extra = [k for k in a if k not in ANSWER_KEYS]
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"extra fields: {extra}")
    if missing:
        return None, errors

    if type(a["posting_id"]) is not int or a["posting_id"] != posting["id"]:
        errors.append(f"posting_id {a['posting_id']!r} is not the id being checked ({posting['id']})")
    if a["verdict"] not in VERDICTS:
        errors.append(f"verdict {a['verdict']!r} is not 'relevant' or 'not relevant'")
    for key, allowed in (("resume_fields", RESUME_FIELDS), ("posting_fields", POSTING_FIELDS)):
        v = a[key]
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            errors.append(f"{key} is not a list of strings")
        else:
            bad = [x for x in v if x not in allowed]
            if bad:
                errors.append(f"{key} not allowed: {bad}")
    terms = a["matched_terms"]
    if not isinstance(terms, list) or not all(isinstance(x, str) and x.strip() for x in terms):
        errors.append("matched_terms is not a list of non-empty strings")
    elif not errors:
        for term in terms:
            in_resume = [f for f in a["resume_fields"] if has_phrase(term, field_text(view, "resume", f))]
            in_posting = [f for f in a["posting_fields"] if has_phrase(term, field_text(view, "posting", f))]
            if not in_resume:
                errors.append(f"matched term {term!r} is not in any named résumé field {a['resume_fields']}")
            if not in_posting:
                errors.append(f"matched term {term!r} is not in any named posting field {a['posting_fields']}")
    if a["verdict"] == "relevant" and isinstance(terms, list) and not terms:
        errors.append("a 'relevant' verdict has no matched terms")
    if not isinstance(a["reason"], str) or not a["reason"].strip():
        errors.append("reason is empty")
    return (None, errors) if errors else (a, [])


class ClaudeUnavailable(Exception):
    pass


def claude_command(prompt_text, model):
    return ["claude", "-p",
            "--model", model,
            "--tools", "",                     # every built-in tool off: no web, no files, no shell
            "--strict-mcp-config",             # no MCP servers either
            "--no-session-persistence",        # nothing saved; every call is a fresh conversation
            "--system-prompt", prompt_text,    # the prompt contract replaces Claude Code's own system prompt
            "--output-format", "json"]


def call_claude(prompt_text, message, model, timeout=300):
    """Returns (answer text, models Claude Code reported). Raises ClaudeUnavailable."""
    with tempfile.TemporaryDirectory(prefix="js1-judge-") as empty_dir:   # no CLAUDE.md, no project files
        try:
            p = subprocess.run(claude_command(prompt_text, model), input=message, capture_output=True,
                               text=True, cwd=empty_dir, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise ClaudeUnavailable(f"claude CLI could not run: {e}") from e
    if p.returncode != 0:
        raise ClaudeUnavailable(f"claude exited {p.returncode}: {(p.stderr or p.stdout).strip()[:300]}")
    try:
        out = json.loads(p.stdout)
    except ValueError as e:
        raise ClaudeUnavailable(f"claude CLI output was not its JSON envelope: {p.stdout[:200]!r}") from e
    if out.get("is_error") or not isinstance(out.get("result"), str):
        raise ClaudeUnavailable(f"claude CLI reported an error: {str(out)[:300]}")
    return out["result"], sorted((out.get("modelUsage") or {}).keys())


def judgment(posting, resume, prompt_path, model=DEFAULT_MODEL, ask=None):
    ask = ask or call_claude
    prompt_text = Path(prompt_path).read_text(encoding="utf-8")
    view = claude_view(posting, resume)
    message = json.dumps(view, indent=2, ensure_ascii=False)
    j = {
        "judge": "JUDGMENT",
        "label": JUDGMENT_LABEL,
        "posting_id": posting["id"],
        "status": None,
        "verdict": None,
        "answer": None,
        "errors": [],
        "raw_answer": None,
        "prompt_file": Path(prompt_path).name,
        "prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
        "model_requested": model,
        "models_reported": [],
        "asked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seconds": None,
    }
    start = time.monotonic()
    try:
        raw, models = ask(prompt_text, message, model)
    except ClaudeUnavailable as e:
        j.update(status="unavailable", errors=[str(e)], seconds=round(time.monotonic() - start, 1))
        return j
    j.update(raw_answer=raw, models_reported=models, seconds=round(time.monotonic() - start, 1))
    answer, errors = validate(raw, posting, view)
    if errors:
        j.update(status="invalid", errors=errors)          # no verdict is taken from an invalid answer
    else:
        j.update(status="valid", verdict=answer["verdict"], answer=answer)
    return j
