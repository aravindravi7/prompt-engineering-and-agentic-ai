"""The written rule, R-v1 (CONTRACT.md §4).

This judge is a record, not a judgment: given the same resume and the same
posting it returns the same verdict, and anybody with the contract in front of
them can recompute it by hand. That is the whole point of having it next to the
model's answer.
"""

from __future__ import annotations

from .fieldpath import whole_word

RULE_VERSION = "R-v2"

GATE_ORDER = ("G1_title_block", "G2_discipline", "G3_job_family", "G4_location")

JOB_FAMILY_KEY = "Job Family"


def _cite(resume_field, resume_value, posting_field, evidence):
    return {
        "resume_field": resume_field,
        "resume_value": resume_value,
        "posting_field": posting_field,
        "evidence": evidence,
    }


def job_family(posting):
    """The posting's Job Family metadata entry, as ``(index, value)``.

    Returns ``None`` when the entry is absent or its value is empty. The index
    is part of the answer because the justification has to name the field path
    that it read, and that path is ``metadata[<index>].value``.
    """
    metadata = posting.get("metadata")
    if not isinstance(metadata, list):
        return None
    for i, entry in enumerate(metadata):
        if isinstance(entry, dict) and entry.get("name") == JOB_FAMILY_KEY:
            value = entry.get("value")
            if isinstance(value, str) and value.strip():
                return i, value
            return i, None
    return None


def judge(posting: dict, resume: dict) -> dict:
    """Return the rule verdict for one posting.

    Gates are evaluated in the order G1 to G4 and the first failure decides,
    which is what makes ``gate_failed`` meaningful (CONTRACT.md O4).
    """
    title = (posting.get("title") or "")
    title_cf = title.casefold()
    location = ""
    loc = posting.get("location")
    if isinstance(loc, dict) and isinstance(loc.get("name"), str):
        location = loc["name"]
    location_cf = location.casefold()
    family = job_family(posting)

    passed = []

    # --- G1 title_block: whole-word blocked tokens in the title ---------------
    for i, token in enumerate(resume["title_block"]):
        if whole_word(token, title_cf):
            return _verdict(
                "not_relevant",
                "G1_title_block",
                [_cite(f"title_block[{i}]", token, "title", token)],
            )
    passed.append(
        _cite("title_block", "no blocked token matched", "title", title_cf)
    )

    # --- G2 discipline: title must contain a target phrase --------------------
    hit = None
    for i, phrase in enumerate(resume["target_title_phrases"]):
        if phrase in title_cf:
            hit = (i, phrase)
            break
    if hit is None:
        return _verdict(
            "not_relevant",
            "G2_discipline",
            [
                _cite(
                    "target_title_phrases",
                    "no target phrase occurs in this title",
                    "title",
                    title_cf,
                )
            ],
        )
    passed.append(
        _cite(f"target_title_phrases[{hit[0]}]", hit[1], "title", hit[1])
    )

    # --- G3 job_family: the Job Family value must contain a target phrase -----
    if family is None or family[1] is None:
        # On the real board the Job Family entry is always present and 10 of
        # 161 postings carry a null value. Either way there is no value to
        # quote, so the citation names the entry that was read and says the
        # value was empty, rather than inventing evidence.
        citation = (
            _cite(
                "target_job_families",
                "the posting's Job Family entry has an empty value",
                f"metadata[{family[0]}].name",
                "job family",
            )
            if family is not None
            else _cite(
                "target_job_families",
                "the posting carries no Job Family entry at all",
                "id",
                str(posting["id"]),
            )
        )
        return _verdict("not_relevant", "G3_job_family", [citation])
    family_index, family_value = family
    family_cf = family_value.casefold()
    family_hit = None
    for j, phrase in enumerate(resume["target_job_families"]):
        if phrase in family_cf:
            family_hit = (j, phrase)
            break
    if family_hit is None:
        return _verdict(
            "not_relevant",
            "G3_job_family",
            [
                _cite(
                    "target_job_families",
                    "no target job family occurs in this posting's Job Family",
                    f"metadata[{family_index}].value",
                    family_cf,
                )
            ],
        )
    passed.append(
        _cite(
            f"target_job_families[{family_hit[0]}]",
            family_hit[1],
            f"metadata[{family_index}].value",
            family_hit[1],
        )
    )

    # --- G4 location: an allowed location phrase, or remote if remote_ok ------
    loc_hit = None
    for i, phrase in enumerate(resume["locations_ok"]):
        if phrase in location_cf:
            loc_hit = _cite(f"locations_ok[{i}]", phrase, "location.name", phrase)
            break
    if loc_hit is None and resume["remote_ok"] and "remote" in location_cf:
        loc_hit = _cite("remote_ok", True, "location.name", "remote")
    if loc_hit is None:
        return _verdict(
            "not_relevant",
            "G4_location",
            [
                _cite(
                    "locations_ok",
                    "no allowed location phrase occurs, and the posting is not remote",
                    "location.name",
                    location_cf,
                )
            ],
        )
    passed.append(loc_hit)

    return _verdict("relevant", None, passed)


def _verdict(verdict, gate_failed, justification):
    return {
        "kind": "record",
        "rule_version": RULE_VERSION,
        "verdict": verdict,
        "gate_failed": gate_failed,
        "justification": justification,
    }
