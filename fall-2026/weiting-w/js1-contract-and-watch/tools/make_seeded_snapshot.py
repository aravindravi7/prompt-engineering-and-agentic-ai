"""Build the SEEDED earlier snapshot from the real saved response.

The assignment allows a second run against a saved earlier response as long as
it is clearly labelled as seeded. This is the whole construction, in one file,
so a TA can rebuild it byte-for-byte and see exactly what was removed:

    python3 tools/make_seeded_snapshot.py \
        evidence/raw/20261026-reddit-browser-save.json \
        evidence/raw/SEEDED-20261026-reddit-earlier-than-2026-10-20.json \
        2026-10-20

Every posting whose ``first_published`` is on or after the cut date is removed.
Nothing is edited, reordered, or invented: the output is a subset of the real
postings, in their original order, with ``meta.total`` corrected to the subset
size and a ``seeded`` block added saying what was done.

``first_published`` is used here and nowhere in judging; CONTRACT.md §1.4 says
so.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__)
        return 2
    source, target, cut = Path(argv[1]), Path(argv[2]), argv[3]
    payload = json.loads(source.read_text(encoding="utf-8"))
    kept = [j for j in payload["jobs"] if j["first_published"] < cut]
    removed = [j["id"] for j in payload["jobs"] if j["first_published"] >= cut]
    out = {
        "jobs": kept,
        "meta": {"total": len(kept)},
        "seeded": {
            "label": "SEEDED - NOT A LIVE RESPONSE",
            "built_from": source.name,
            "built_by": "tools/make_seeded_snapshot.py",
            "rule": f"kept postings with first_published < {cut}",
            "removed_posting_ids": sorted(removed),
            "kept": len(kept),
            "removed": len(removed),
        },
    }
    target.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {target}: kept {len(kept)}, removed {len(removed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
