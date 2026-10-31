"""Tests for the sampling report and prompt-experiment runners (experiment/).

run from the js1-contract-and-watch folder:
  python3 -m unittest discover -s tests -v

Offline: real Claude is blocked; a fake returns fixed answers. Every output goes to a
temporary folder, so experiment/sampling/ and experiment/results/ are never written.
The committed selection, labels and baseline response are read, never changed.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER))
sys.path.insert(0, str(FOLDER / "experiment"))
import harness  # noqa: E402
import judge  # noqa: E402
import run_experiment  # noqa: E402
import sample  # noqa: E402

PROMPT = FOLDER / "prompts" / "judgment-v1.md"


def blocked(*a, **k):
    raise AssertionError("a test tried to reach Claude")


def answer(pid, verdict):
    """A valid answer. 'Databricks' is in skills.data_bi and in every Databricks posting's content."""
    if verdict == "relevant":
        return {"posting_id": pid, "verdict": "relevant", "resume_fields": ["skills.data_bi"],
                "posting_fields": ["content"], "matched_terms": ["Databricks"], "reason": "Fake answer (test)."}
    return {"posting_id": pid, "verdict": "not relevant", "resume_fields": [], "posting_fields": ["title"],
            "matched_terms": [], "reason": "Fake answer (test)."}


def fake(script):
    """script(posting_id, call number for that posting) -> dict, raw string, or exception."""
    seen = {}

    def ask(prompt_text, message, model):
        pid = json.loads(message)["job_posting"]["posting_id"]
        seen[pid] = seen.get(pid, 0) + 1
        a = script(pid, seen[pid])
        if isinstance(a, Exception):
            raise a
        return (a if isinstance(a, str) else json.dumps(a)), ["fake-model (test)"]
    ask.seen = seen
    return ask


class Offline(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(judge, "call_claude", blocked)
        p.start()
        self.addCleanup(p.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)


class Inputs(Offline):
    def test_committed_labels_parse(self):
        labels = harness.load_labels()
        sel = harness.load_selection()
        ids = {r["id"] for k in ("development", "held_out", "sampling") for r in sel[k]}
        self.assertEqual(set(labels), ids)
        self.assertTrue(all(v["label"] in judge.VERDICTS and v["note"] for v in labels.values()))

    def test_a_missing_label_is_refused(self):
        sheet = self.out / "sheet.md"
        sheet.write_text(harness.SHEET.read_text(encoding="utf-8").replace(
            "- **My label (relevant / not relevant):** not relevant", "- **My label (relevant / not relevant):** ", 1))
        with self.assertRaises(harness.SetupError):
            harness.load_labels(sheet)

    def test_a_changed_baseline_response_is_refused(self):
        sel = {**harness.load_selection(), "source_sha256": "0" * 64}
        with self.assertRaises(harness.SetupError):
            harness.load_postings(sel)

    def test_pass_definition(self):
        valid = {"status": "valid", "verdict": "not relevant"}
        self.assertTrue(harness.is_pass(valid, "not relevant"))
        self.assertFalse(harness.is_pass(valid, "relevant"))
        self.assertFalse(harness.is_pass({"status": "invalid", "verdict": None}, "not relevant"))
        self.assertFalse(harness.is_pass({"status": "unavailable", "verdict": None}, "not relevant"))


class Sampling(Offline):
    def test_every_posting_asked_repeats_times_and_spread_counted(self):
        ids = [r["id"] for r in harness.load_selection()["sampling"]]
        flip, broken = ids[0], ids[1]

        def script(pid, n):
            if pid == flip:
                return answer(pid, "relevant" if n % 2 else "not relevant")
            if pid == broken and n == 1:
                return "```json\n" + json.dumps(answer(pid, "not relevant")) + "\n```"
            return answer(pid, "not relevant")
        ask = fake(script)
        r, base = sample.sample(4, PROMPT, "m", self.out, ask=ask)
        self.assertEqual(ask.seen, {pid: 4 for pid in ids})
        self.assertEqual(r["summary"]["calls"], 20)
        per = {p["posting_id"]: p for p in r["per_posting"]}
        self.assertEqual(per[flip]["outcomes"], ["relevant", "not relevant", "relevant", "not relevant"])
        self.assertEqual((per[flip]["distinct_outcomes"], per[flip]["passes"]), (2, 2))
        self.assertEqual(per[broken]["counts"]["invalid"], 1)
        self.assertEqual(per[broken]["passes"], 3)
        self.assertEqual(r["summary"]["passes"], 2 + 3 + 4 + 4 + 4)
        self.assertEqual(r["summary"]["postings_with_more_than_one_outcome"], 2)
        self.assertTrue(base.with_suffix(".json").exists() and base.with_suffix(".md").exists())
        self.assertIn("| no |", base.with_suffix(".md").read_text())

    def test_fewer_than_four_repeats_refused(self):
        with self.assertRaises(harness.SetupError):
            sample.sample(3, PROMPT, "m", self.out, ask=fake(lambda p, n: answer(p, "not relevant")))


class Experiment(Offline):
    def test_development_run_scores_each_posting_by_its_own_label(self):
        dev = [r["id"] for r in harness.load_selection()["development"]]
        says_relevant = dev[2]
        ask = fake(lambda p, n: answer(p, "relevant") if p == says_relevant else answer(p, "not relevant"))
        r, path = run_experiment.run("baseline", PROMPT, "development", self.out, ask=ask)
        self.assertEqual(sorted(ask.seen), sorted(dev))
        rows = {x["posting_id"]: x for x in r["rows"]}
        self.assertEqual(rows[says_relevant]["outcome"], "relevant")
        self.assertFalse(rows[says_relevant]["pass"])                         # every label here is "not relevant"
        self.assertEqual(r["summary"]["passes"], 9)
        self.assertEqual(r["summary"]["claude_relevant_where_i_said_not"], 1)
        for pid, x in rows.items():
            self.assertEqual(x["judgment"]["posting_id"], pid)
        self.assertTrue(path.exists())

    def test_held_out_needs_final_and_runs_once_per_prompt(self):
        ask = fake(lambda p, n: answer(p, "not relevant"))
        with self.assertRaises(harness.SetupError):
            run_experiment.run("baseline", PROMPT, "held_out", self.out, ask=ask)
        run_experiment.run("baseline", PROMPT, "held_out", self.out, final=True, ask=ask)
        with self.assertRaises(harness.SetupError):
            run_experiment.run("baseline", PROMPT, "held_out", self.out, final=True, ask=ask)
        run_experiment.run("revision", PROMPT, "held_out", self.out, final=True, ask=ask)   # a different prompt name

    def test_invalid_and_unavailable_answers_fail(self):
        dev = [r["id"] for r in harness.load_selection()["development"]]
        ask = fake(lambda p, n: "not json" if p == dev[0] else
                   (judge.ClaudeUnavailable("offline") if p == dev[1] else answer(p, "not relevant")))
        r, _ = run_experiment.run("baseline", PROMPT, "development", self.out, ask=ask)
        self.assertEqual(r["summary"]["outcomes"]["invalid"], 1)
        self.assertEqual(r["summary"]["outcomes"]["unavailable"], 1)
        self.assertEqual(r["summary"]["passes"], 8)

    def test_report_lists_every_saved_run(self):
        ask = fake(lambda p, n: answer(p, "not relevant"))
        run_experiment.run("baseline", PROMPT, "development", self.out, ask=ask)
        run_experiment.run("revision", PROMPT, "development", self.out, ask=ask)
        path, runs = run_experiment.report(self.out)
        text = path.read_text()
        self.assertEqual(len(runs), 2)
        self.assertIn("**10/10**", text)
        self.assertIn("## development: each posting, each run", text)


if __name__ == "__main__":
    unittest.main()
