"""The watch: CONTRACT.md section 2 (Out) and section 6 (Failure)."""

import gzip
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agent.watch import run
from tests.helpers import PERSONA, board_bytes, posting

A = posting(101, "Software Engineer, Sandboxing", body="<p>AWS and Kubernetes.</p>")
B = posting(102, "Account Executive", body="<p>Sales.</p>")
C = posting(103, "Data Engineer", body="<p>5+ years. SQL and Kafka.</p>")

VALID_CLAUDE = '{"label":"CLAUDE_JUDGMENT","verdict":"NOT_MATCH","reason":"Constructed reply for a test."}'


class WatchTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.state = self.dir / "state" / "anthropic.state.json"
        self.calls = 0

    def tearDown(self):
        shutil.rmtree(self.dir)

    def fixture(self, name, *postings):
        path = self.dir / name
        path.write_bytes(board_bytes(*postings))
        return path

    def watch(self, fixture=None, **kwargs):
        return run("anthropic", PERSONA, self.state, self.dir / "out", fixture=fixture, **kwargs)

    def new_ids(self, record):
        return [p["job_id"] for p in record["new_postings"]]


class NewByID(WatchTest):
    def test_first_run_is_a_baseline_with_zero_new(self):
        record = self.watch(self.fixture("a.json", A, B))
        self.assertEqual(record["run_kind"], "baseline")
        self.assertEqual(self.new_ids(record), [])

    def test_second_run_on_the_same_response_reports_zero_new(self):
        f = self.fixture("a.json", A, B)
        self.watch(f)
        self.assertEqual(self.new_ids(self.watch(f)), [])

    def test_a_new_id_is_reported(self):
        self.watch(self.fixture("a.json", A, B))
        self.assertEqual(self.new_ids(self.watch(self.fixture("b.json", A, B, C))), [103])

    def test_same_id_with_a_changed_title_is_not_new(self):
        self.watch(self.fixture("a.json", A, B))
        renamed = dict(B, title="Account Executive, Startups")
        self.assertEqual(self.new_ids(self.watch(self.fixture("b.json", A, renamed))), [])

    def test_new_id_with_an_old_title_is_new(self):
        self.watch(self.fixture("a.json", A, B))
        reposted = dict(B, id=104)
        self.assertEqual(self.new_ids(self.watch(self.fixture("b.json", A, B, reposted))), [104])

    def test_posting_that_disappears_and_comes_back_is_not_new(self):
        self.watch(self.fixture("a.json", A, B))
        self.watch(self.fixture("b.json", A))
        self.assertEqual(self.new_ids(self.watch(self.fixture("c.json", A, B))), [])

    def test_state_file_holds_every_id_seen(self):
        self.watch(self.fixture("a.json", A, B))
        self.watch(self.fixture("b.json", A, C))
        self.assertEqual(sorted(json.loads(self.state.read_text())["seen_ids"]), [101, 102, 103])


class Evidence(WatchTest):
    def test_raw_response_saved_byte_for_byte_with_its_hash(self):
        f = self.fixture("a.json", A, B)
        record = self.watch(f)
        raw = gzip.decompress((self.dir / "out" / record["raw_file"]).read_bytes())
        self.assertEqual(raw, f.read_bytes())
        self.assertEqual(record["raw_sha256"], hashlib.sha256(raw).hexdigest())

    def test_raw_response_saved_before_processing(self):
        bad = self.dir / "bad.json"
        bad.write_bytes(b"not json at all")
        with self.assertRaises(ValueError):
            self.watch(bad)
        saved = list((self.dir / "out" / "evidence" / "raw").glob("*.json.gz"))
        self.assertEqual([gzip.decompress(p.read_bytes()) for p in saved], [b"not json at all"])
        self.assertFalse(self.state.exists())

    def test_fetch_failure_leaves_the_state_file_unchanged(self):
        self.watch(self.fixture("a.json", A, B))
        before = self.state.read_bytes()

        def broken(url):
            raise OSError("board unreachable")

        with self.assertRaises(OSError):
            self.watch(fetcher=broken)
        self.assertEqual(self.state.read_bytes(), before)

    def test_fixture_run_is_labeled_seeded(self):
        record = self.watch(self.fixture("a.json", A, B))
        self.assertEqual(record["source"], "seeded")
        self.assertIn("seeded", (self.dir / "out" / record["report_file"]).read_text().lower())

    def test_gzip_fixture_from_evidence_is_read_byte_for_byte(self):
        # Added after the implementation, for seeded runs from evidence/raw/ files.
        first = self.watch(self.fixture("a.json", A, B))
        record = self.watch(self.dir / "out" / first["raw_file"], note="replay of run 1")
        self.assertEqual(record["raw_sha256"], first["raw_sha256"])
        self.assertEqual(record["note"], "replay of run 1")
        self.assertIn("replay of run 1", (self.dir / "out" / record["report_file"]).read_text())

    def test_fetched_run_is_labeled_live(self):
        record = self.watch(fetcher=lambda url: board_bytes(A, B))
        self.assertEqual(record["source"], "live")

    def test_non_fictional_resume_is_refused_before_any_fetch(self):
        real = self.dir / "real.json"
        resume = json.loads(PERSONA.read_text())
        resume["personal"]["email"] = "someone@gmail.com"
        real.write_text(json.dumps(resume))

        def fetcher(url):
            self.calls += 1
            return board_bytes(A)

        with self.assertRaises(ValueError):
            run("anthropic", real, self.state, self.dir / "out", fetcher=fetcher)
        self.assertEqual(self.calls, 0)


class Verdicts(WatchTest):
    def test_each_verdict_stays_with_its_own_posting(self):
        self.watch(self.fixture("a.json", B))
        first = posting(201, "Account Executive", body="<p>Sales.</p>")
        middle = posting(202, "Software Engineer, Tools", body="<p>Python and Docker.</p>")
        last = posting(203, "Senior Software Engineer", body="<p>Python and Docker.</p>")
        record = self.watch(self.fixture("b.json", B, first, middle, last))
        by_id = {p["job_id"]: p for p in record["new_postings"]}
        self.assertEqual({i: p["rule_verdict"]["verdict"] for i, p in by_id.items()},
                         {201: "NOT_MATCH", 202: "MATCH", 203: "NOT_MATCH"})
        for source in (first, middle, last):
            reported = by_id[source["id"]]
            self.assertEqual(reported["title"], source["title"])
            r1 = next(c for c in reported["rule_verdict"]["checks"] if c["rule"] == "R1")
            self.assertEqual(r1["posting_value"], source["title"])

    def test_new_posting_reports_the_contract_fields(self):
        self.watch(self.fixture("a.json", B))
        record = self.watch(self.fixture("b.json", B, A))
        reported = record["new_postings"][0]
        self.assertEqual(
            {k: reported[k] for k in ["title", "company_name", "location", "absolute_url", "job_id"]},
            {"title": A["title"], "company_name": "Anthropic", "location": A["location"]["name"],
             "absolute_url": A["absolute_url"], "job_id": 101})
        self.assertEqual(reported["rule_verdict"]["kind"], "record")


class ClaudeJudgment(WatchTest):
    def test_claude_disagreeing_does_not_change_the_rule_verdict(self):
        self.watch(self.fixture("a.json", B))
        record = self.watch(self.fixture("b.json", B, A), ask_claude=lambda prompt: VALID_CLAUDE)
        reported = record["new_postings"][0]
        self.assertEqual(reported["rule_verdict"]["verdict"], "MATCH")
        self.assertEqual(reported["claude_judgment"]["verdict"], "NOT_MATCH")
        self.assertEqual(reported["claude_judgment"]["status"], "accepted")

    def test_claude_judgment_is_labeled_as_opinion_in_the_report(self):
        self.watch(self.fixture("a.json", B))
        record = self.watch(self.fixture("b.json", B, A), ask_claude=lambda prompt: VALID_CLAUDE)
        self.assertEqual(record["new_postings"][0]["claude_judgment"]["label"], "Claude judgment — opinion, not fact")
        self.assertIn("Claude judgment — opinion, not fact", (self.dir / "out" / record["report_file"]).read_text())

    def test_reply_that_fails_the_validator_is_rejected_not_counted(self):
        self.watch(self.fixture("a.json", B))
        fenced = "```json\n" + VALID_CLAUDE + "\n```"
        record = self.watch(self.fixture("b.json", B, A), ask_claude=lambda prompt: fenced)
        judgment = record["new_postings"][0]["claude_judgment"]
        self.assertEqual(judgment["status"], "rejected")
        self.assertIsNone(judgment["verdict"])
        self.assertEqual(judgment["raw_reply"], fenced)

    def test_baseline_run_asks_claude_nothing(self):
        def ask(prompt):
            self.calls += 1
            return VALID_CLAUDE

        self.watch(self.fixture("a.json", A, B), ask_claude=ask)
        self.assertEqual(self.calls, 0)


if __name__ == "__main__":
    unittest.main()
