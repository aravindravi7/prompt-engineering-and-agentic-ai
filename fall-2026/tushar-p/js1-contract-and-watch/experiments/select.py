"""Select the 20 postings for the prompt experiment (experiments/LABELING-RULE.md).

Run from the project folder: python -m experiments.select

Pool: postings in the fixed baseline raw file whose title contains "Engineer"
(case-insensitive substring), in the file's own order. Draw: random.Random(7375).sample
of 20; the first 10 drawn are dev, the next 10 held-out.

Posting files show the same words as agent.text.strip_html, laid out for reading: a blank
line between paragraphs and one "- " line per list item.

Writes posting files and selection.json every time (their content is deterministic).
Writes labels.csv only if it does not exist yet: labels are written by hand, once.
No rule verdicts are computed or written here.
"""

import csv
import html
import json
import random
import sys
from html.parser import HTMLParser
from pathlib import Path

from agent import PROJECT_DIR
from agent.text import normalize

SOURCE = PROJECT_DIR / "raw" / "greenhouse-stripe-2026-10-27T203128.json"
EXPERIMENTS_DIR = PROJECT_DIR / "experiments"
SEED = 7375
SAMPLE_SIZE = 20
DEV_SIZE = 10
TITLE_FILTER = "engineer"
LABEL_COLUMNS = ["posting_id", "split", "title", "label", "R1", "R2", "R3", "R4", "R5", "R6",
                 "note", "labeled_date"]


def load_pool(source: Path = SOURCE) -> list[dict]:
    jobs = json.loads(Path(source).read_text(encoding="utf-8"))["jobs"]
    return [job for job in jobs if TITLE_FILTER in (job.get("title") or "").lower()]


def select(source: Path = SOURCE, seed: int = SEED) -> tuple[int, list[tuple[str, dict]]]:
    """(pool size, [(split, posting), ...] in draw order)."""
    pool = load_pool(source)
    drawn = random.Random(seed).sample(pool, SAMPLE_SIZE)
    return len(pool), [("dev" if i < DEV_SIZE else "held-out", job) for i, job in enumerate(drawn)]


BLOCK_TAGS = {
    "p", "div", "li", "ul", "ol", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6",
    "table", "tr", "section", "article", "header", "footer", "blockquote", "pre",
}


class _BlockCollector(HTMLParser):
    """Same text as agent.text.strip_html, split into paragraph and list-item blocks.

    It decodes and skips exactly as strip_html does, so joining the block texts with spaces
    gives strip_html's output. Only the labeling files use it; Claude and the rule do not.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, str]] = []  # (kind, text), kind is "para" or "item"
        self._parts: list[str] = []
        self._list_item_depth = 0
        self._skipping = 0

    def _flush(self):
        text = normalize(" ".join(self._parts))
        self._parts = []
        if text:
            self.blocks.append(("item" if self._list_item_depth else "para", text))

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skipping += 1
        elif tag in BLOCK_TAGS:
            self._flush()
            if tag == "li":
                self._list_item_depth += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skipping:
            self._skipping -= 1
        elif tag in BLOCK_TAGS:
            self._flush()
            if tag == "li" and self._list_item_depth:
                self._list_item_depth -= 1

    def handle_data(self, data):
        if not self._skipping:
            self._parts.append(data)

    def close(self):
        super().close()
        self._flush()


def text_blocks(content: str | None) -> list[tuple[str, str]]:
    collector = _BlockCollector()
    collector.feed(html.unescape(content or ""))
    collector.close()
    return collector.blocks


def readable_text(content: str | None) -> str:
    """Posting text for human labeling: a blank line between paragraphs, one line per list item."""
    lines: list[str] = []
    previous = None
    for kind, text in text_blocks(content):
        if previous is not None and not (kind == "item" and previous == "item"):
            lines.append("")
        lines.append(f"- {text}" if kind == "item" else text)
        previous = kind
    return "\n".join(lines)


def posting_markdown(job: dict) -> str:
    location = (job.get("location") or {}).get("name")
    return "\n".join([
        f"# {job.get('title')}",
        "",
        f"- id: {job['id']}",
        f"- title: {job.get('title')}",
        f"- location.name: {location}",
        f"- first_published: {job.get('first_published')}",
        f"- updated_at: {job.get('updated_at')}",
        f"- url: {job.get('absolute_url')}",
        "",
        "## Posting text",
        "",
        readable_text(job.get("content")),
        "",
    ])


def write_outputs(pool_size: int, selection: list[tuple[str, dict]], out_dir: Path = EXPERIMENTS_DIR,
                  source: Path = SOURCE) -> bool:
    """Write posting files, selection.json, and (if absent) labels.csv. Returns True if labels.csv was written."""
    for split, job in selection:
        path = out_dir / "postings" / split / f"{job['id']}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(posting_markdown(job), encoding="utf-8")

    try:
        source_display = str(Path(source).resolve().relative_to(PROJECT_DIR))
    except ValueError:
        source_display = str(source)
    summary = {
        "source": source_display,
        "title_filter": "title contains 'Engineer' (case-insensitive substring)",
        "seed": SEED,
        "pool_size": pool_size,
        "ids_in_draw_order": [job["id"] for _, job in selection],
        "dev": [job["id"] for split, job in selection if split == "dev"],
        "held_out": [job["id"] for split, job in selection if split == "held-out"],
    }
    (out_dir / "selection.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    labels_path = out_dir / "labels.csv"
    if labels_path.exists():
        return False
    with labels_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LABEL_COLUMNS)
        writer.writeheader()
        for split, job in selection:
            writer.writerow({"posting_id": job["id"], "split": split, "title": job.get("title")})
    return True


def main() -> int:
    pool_size, selection = select()
    wrote_labels = write_outputs(pool_size, selection)
    print(f"pool size: {pool_size}")
    for i, (split, job) in enumerate(selection, start=1):
        print(f"{i:2d}  {split:8s}  {job['id']}  {job.get('title')}")
    if not wrote_labels:
        print("labels.csv already exists; left unchanged", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
