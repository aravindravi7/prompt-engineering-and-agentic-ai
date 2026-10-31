"""Build the CONSTRUCTED earlier response for the seeded pair (run 2 without waiting for a second day).

It is run 1's saved live response with every posting first published on or after 2026-10-30 removed:
an approximation of the board before those postings appeared. It is not a response anyone received.
Postings that were on the board earlier and closed before run 1 cannot be reconstructed, so they are missing.

    python3 tools/make_seeded_fixture.py
"""

import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RUN1_RAW = HERE / "evidence" / "raw" / "anthropic-2026-10-31T074011Z.json.gz"
CUTOFF = "2026-10-30"
OUT = HERE / "seeded" / "fixtures" / ("anthropic-CONSTRUCTED-before-%s.json.gz" % CUTOFF)


def main():
    board = json.loads(gzip.decompress(RUN1_RAW.read_bytes()))
    kept = [job for job in board["jobs"] if job["first_published"][:10] < CUTOFF]
    removed = [job for job in board["jobs"] if job["first_published"][:10] >= CUTOFF]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(gzip.compress(json.dumps({"jobs": kept, "meta": {"total": len(kept)}}).encode("utf-8"), mtime=0))
    print("kept %d, removed %d (first published on or after %s) -> %s" % (len(kept), len(removed), CUTOFF,
                                                                         OUT.relative_to(HERE)))
    for job in removed:
        print("  removed", job["id"], job["first_published"], job["title"])


if __name__ == "__main__":
    main()
