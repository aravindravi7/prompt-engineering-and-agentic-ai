"""Tests for watch.py against CONTRACT.md v2, sections 1-3 (the watch only; no judges yet).

run from the js1-contract-and-watch folder:
  python3 -m unittest discover -s tests -v

Offline: every run uses a saved fixture (--from-file). Live fetching is replaced by a
function that fails the test if anything tries to reach the network.
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER))
import watch  # noqa: E402

REAL_FETCH = watch.fetch            # kept before setUp replaces watch.fetch with no_network
FIX = HERE / "fixtures"
DAY1, DAY2 = FIX / "board-day1.json", FIX / "board-day2.json"
PERSONA = FOLDER / "persona" / "priya-nair.resume.example.json"
T1 = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)
T2 = datetime(2026, 10, 29, 12, 0, 0, tzinfo=timezone.utc)
T3 = datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc)


def no_network(*a, **k):
    raise AssertionError("a test tried to reach the network")


class WatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.state = self.dir / "state" / "databricks.state.json"
        self.out = self.dir / "runs"
        patcher = mock.patch.object(watch, "fetch", no_network)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def run_fixture(self, fixture, now, resume=PERSONA):
        return watch.run("databricks", resume, self.state, self.out, from_file=fixture, now=now)

    def main_quiet(self, argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return watch.main(argv)

    def fake_resume(self, email, phone):
        p = self.dir / "resume.json"
        p.write_text(json.dumps({"personal": {"email": email, "phone": phone}, "skills": {"languages": ["Python"]}}))
        return p


class AllowList(WatchTest):
    """Section 3: one host, HTTPS only, no redirects."""

    def test_board_url_is_on_the_allow_list(self):
        watch.assert_allowed(watch.board_url("databricks"))

    def test_other_host_refused_before_any_network(self):
        with mock.patch.object(watch.urllib.request, "build_opener", no_network):
            with self.assertRaises(watch.InputError):
                REAL_FETCH("https://evil.example.com/v1/boards/databricks/jobs")

    def test_plain_http_refused(self):
        with mock.patch.object(watch.urllib.request, "build_opener", no_network):
            with self.assertRaises(watch.InputError):
                REAL_FETCH("http://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true")

    def test_redirect_refused(self):
        with self.assertRaises(watch.FetchError):
            watch.RefuseRedirects().redirect_request(None, None, 302, "Found", {}, "https://evil.example.com/")


class Persona(WatchTest):
    """Section 1: the résumé must have an @example.com email and a 555 phone, or the agent stops."""

    def test_persona_copy_passes(self):
        watch.load_resume(PERSONA)

    def test_non_example_email_refused_and_nothing_written(self):
        bad = self.fake_resume("someone@mail.test", "(617) 555-0100")
        code = self.main_quiet(["--resume", str(bad), "--state", str(self.state), "--out", str(self.out),
                                "--from-file", str(DAY1)])
        self.assertEqual(code, 2)
        self.assertFalse(self.out.exists())
        self.assertFalse(self.state.exists())

    def test_phone_without_555_refused(self):
        bad = self.fake_resume("someone@example.com", "(617) 123-4567")
        with self.assertRaises(watch.InputError):
            self.run_fixture(DAY1, T1, resume=bad)


class Baseline(WatchTest):
    """Section 2: the first run records every id and reports zero new postings."""

    def test_baseline_reports_zero_new_and_records_every_id(self):
        record, _, _ = self.run_fixture(DAY1, T1)
        self.assertEqual(record["mode"], "BASELINE")
        self.assertEqual(record["counts"]["new"], 0)
        self.assertEqual(record["new_postings"], [])
        self.assertEqual(json.loads(self.state.read_text())["seen_ids"], [1001, 1002, 1003, 1004])

    def test_raw_response_saved_byte_for_byte(self):
        record, raw_path, _ = self.run_fixture(DAY1, T1)
        self.assertEqual(raw_path.read_bytes(), DAY1.read_bytes())
        self.assertEqual(record["raw_sha256"], watch.sha256(DAY1.read_bytes()))

    def test_seeded_run_is_labeled(self):
        record, _, _ = self.run_fixture(DAY1, T1)
        self.assertTrue(record["source"].startswith("SEEDED"))
        self.assertIsNone(record["fetched_at"])


class NewSinceLast(WatchTest):
    """Section 2: later runs report only ids not already in state; counting is by id, not title."""

    def setUp(self):
        super().setUp()
        self.run_fixture(DAY1, T1)
        self.record, _, _ = self.run_fixture(DAY2, T2)

    def test_reports_exactly_the_new_ids(self):
        self.assertEqual(self.record["mode"], "WATCH")
        self.assertEqual([p["id"] for p in self.record["new_postings"]], [1005, 1006])

    def test_each_new_posting_carries_its_own_fields(self):
        day2 = {j["id"]: j for j in json.loads(DAY2.read_text())["jobs"]}
        for p in self.record["new_postings"]:
            self.assertEqual(p["original"]["id"], p["id"])
            self.assertEqual(p["original"]["title"], day2[p["id"]]["title"])
            self.assertEqual(p["original"]["absolute_url"], day2[p["id"]]["absolute_url"])

    def test_same_title_different_id_is_new(self):
        titles = {p["id"]: p["original"]["title"] for p in self.record["new_postings"]}
        self.assertEqual(titles[1006], "Staff Machine Learning Engineer")    # same title as 1001
        self.assertEqual(titles[1005], "Account Executive")                  # same title as removed 1002

    def test_id_repeated_in_one_response_is_processed_once(self):
        c = self.record["counts"]
        self.assertEqual(c["postings_in_response"], 6)
        self.assertEqual(c["unique_ids"], 5)
        self.assertEqual(c["ids_repeated_in_response"], 1)
        self.assertEqual(c["unique_titles"], 4)

    def test_removed_posting_stays_seen_and_is_not_new_when_relisted(self):
        self.assertEqual(self.record["no_longer_listed_ids"], [1002])
        record3, _, _ = self.run_fixture(DAY1, T3)                         # 1002 comes back
        self.assertEqual(record3["new_postings"], [])


class FailedRunLeavesState(WatchTest):
    """Section 2 and 3: if fetching, parsing or processing fails, the state file stays unchanged."""

    def setUp(self):
        super().setUp()
        self.run_fixture(DAY1, T1)
        self.before = self.state.read_bytes()

    def test_broken_response_saves_raw_and_keeps_state(self):
        broken = self.dir / "broken.json"
        broken.write_bytes(b'{"jobs": [ {"id": 1001, ')
        code = self.main_quiet(["--state", str(self.state), "--out", str(self.out), "--resume", str(PERSONA),
                                "--from-file", str(broken)])
        self.assertEqual(code, 3)
        self.assertEqual(self.state.read_bytes(), self.before)
        raws = [p for p in self.out.glob("raw-*.json") if p.read_bytes() == broken.read_bytes()]
        self.assertEqual(len(raws), 1)                                       # saved before parsing

    def test_posting_without_id_keeps_state(self):
        bad = self.dir / "no-id.json"
        bad.write_text(json.dumps({"jobs": [{"id": 1001, "title": "x"}, {"title": "no id"}]}))
        with self.assertRaises(watch.FetchError):
            self.run_fixture(bad, T2)
        self.assertEqual(self.state.read_bytes(), self.before)

    def test_corrupt_state_refused_and_not_overwritten(self):
        self.state.write_text("not json")
        code = self.main_quiet(["--state", str(self.state), "--out", str(self.out), "--resume", str(PERSONA),
                                "--from-file", str(DAY2)])
        self.assertEqual(code, 2)
        self.assertEqual(self.state.read_text(), "not json")

    def test_state_for_another_board_refused(self):
        self.state.write_text(json.dumps({"board": "figma", "seen_ids": [1]}))
        with self.assertRaises(watch.InputError):
            self.run_fixture(DAY2, T2)


if __name__ == "__main__":
    unittest.main()
