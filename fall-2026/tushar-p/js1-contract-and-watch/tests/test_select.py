"""The experiment selection is reproducible and never overwrites hand labels."""

import csv
import html
import json

from agent.text import normalize, strip_html
from experiments.select import LABEL_COLUMNS, SEED, readable_text, select, text_blocks, write_outputs


def test_readable_text_layout():
    content = html.escape(
        "<h3>About</h3><p>We build <b>APIs</b>.</p><p>Second&nbsp;paragraph.</p>"
        "<ul><li>Python</li><li>2+ years of <i>SQL</i></li></ul><p>Closing.</p>"
    )
    assert readable_text(content) == (
        "About\n\nWe build APIs .\n\nSecond paragraph.\n\n- Python\n- 2+ years of SQL\n\nClosing."
    )


def test_readable_text_keeps_strip_html_words_for_all_20_postings():
    # The labeling files may only change layout: same words, same order, same spacing
    # between them, once line breaks and the "- " list markers are removed.
    _, selection = select()
    for _, job in selection:
        blocks = text_blocks(job["content"])
        assert normalize(" ".join(text for _, text in blocks)) == strip_html(job["content"]), job["id"]
        assert len(blocks) > 1, job["id"]  # the layout actually split the text


def test_selection_twice_gives_same_20_ids_in_same_order():
    pool_size_1, first = select()
    pool_size_2, second = select()
    ids_1 = [job["id"] for _, job in first]
    ids_2 = [job["id"] for _, job in second]
    assert pool_size_1 == pool_size_2
    assert ids_1 == ids_2
    assert len(ids_1) == 20 and len(set(ids_1)) == 20
    assert [split for split, _ in first] == ["dev"] * 10 + ["held-out"] * 10
    assert all("engineer" in job["title"].lower() for _, job in first)


def test_different_seed_gives_different_draw():
    _, default = select()
    _, other = select(seed=SEED + 1)
    assert [j["id"] for _, j in default] != [j["id"] for _, j in other]


def test_outputs_have_empty_label_columns_and_labels_are_never_overwritten(tmp_path):
    pool_size, selection = select()
    assert write_outputs(pool_size, selection, out_dir=tmp_path) is True

    with (tmp_path / "labels.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert list(rows[0].keys()) == LABEL_COLUMNS
    assert [int(r["posting_id"]) for r in rows] == [j["id"] for _, j in selection]
    for row in rows:
        assert all(row[col] == "" for col in ("label", "R1", "R2", "R3", "R4", "R5", "R6", "note", "labeled_date"))

    written = json.loads((tmp_path / "selection.json").read_text())
    assert written["seed"] == 7375 and written["pool_size"] == pool_size
    assert written["ids_in_draw_order"] == [j["id"] for _, j in selection]

    for split, job in selection:
        text = (tmp_path / "postings" / split / f"{job['id']}.md").read_text()
        assert f"- id: {job['id']}" in text
        assert "rule_verdict" not in text and "&lt;" not in text

    (tmp_path / "labels.csv").write_text("hand labels\n")
    assert write_outputs(pool_size, selection, out_dir=tmp_path) is False
    assert (tmp_path / "labels.csv").read_text() == "hand labels\n"
