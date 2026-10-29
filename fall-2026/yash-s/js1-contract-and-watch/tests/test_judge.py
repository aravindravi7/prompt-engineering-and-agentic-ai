"""Tests for judge.py and the judges inside watch.py, against CONTRACT.md v3 sections 2, 4 and 5.

run from the js1-contract-and-watch folder:
  python3 -m unittest discover -s tests -v

Offline: Claude is never called. A fake stands in for it and returns fixed answers;
the real CLI call is tested only with subprocess.run replaced.
"""
import html
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER))
import judge  # noqa: E402
import watch  # noqa: E402

REAL_CALL_CLAUDE = judge.call_claude          # kept before setUp blocks it
PERSONA = FOLDER / "persona" / "priya-nair.resume.example.json"
PROMPT = FOLDER / "prompts" / "judgment-v1.md"
RESUME = json.loads(PERSONA.read_text(encoding="utf-8"))
DAY1, DAY2 = HERE / "fixtures" / "board-day1.json", HERE / "fixtures" / "board-day2.json"
T1 = datetime(2026, 10, 28, 12, 0, 0, tzinfo=timezone.utc)
T2 = datetime(2026, 10, 29, 12, 0, 0, tzinfo=timezone.utc)


def posting(i, title, text):
    """A constructed posting, entity-escaped the way Greenhouse sends content."""
    return {"id": i, "title": title, "content": html.escape(f"<p>{text}</p>"),
            "absolute_url": f"https://example.com/jobs/{i}"}


def blocked(*a, **k):
    raise AssertionError("a test tried to reach Claude or the network")


def fake_claude(answers):
    """Stands in for call_claude: answers[posting_id] is a dict, a raw string, or an exception."""
    def ask(prompt_text, message, model):
        a = answers[json.loads(message)["job_posting"]["posting_id"]]
        if isinstance(a, Exception):
            raise a
        return (a if isinstance(a, str) else json.dumps(a)), ["fake-model (test)"]
    return ask


class Offline(unittest.TestCase):
    def setUp(self):
        for target, name in ((judge, "call_claude"), (watch, "fetch")):
            p = mock.patch.object(target, name, blocked)
            p.start()
            self.addCleanup(p.stop)


class RecordRule(Offline):
    """Section 4: all three rules must pass."""

    def verdict(self, title, text):
        return judge.record_verdict(posting(1, title, text), RESUME)

    def test_relevant_when_all_three_pass(self):
        r = self.verdict("Staff Machine Learning Engineer", "Python and SQL every day.")
        self.assertEqual(r["verdict"], "relevant")
        self.assertEqual([h["skill"] for h in r["checks"]["rule2_skills"]["matched"]], ["Python", "SQL"])

    def test_databricks_and_unity_catalog_do_not_count(self):
        r = self.verdict("AI Engineer", "Databricks, Unity Catalog and Python.")
        self.assertEqual(r["verdict"], "not relevant")
        self.assertFalse(r["checks"]["rule2_skills"]["passed"])

    def test_mlflow_and_delta_lake_count(self):
        self.assertEqual(self.verdict("Data Engineer", "MLflow and Delta Lake.")["verdict"], "relevant")

    def test_familiar_with_not_shipped_does_not_count(self):
        self.assertEqual(self.verdict("ML Engineer", "Ray, Kubeflow and Python.")["verdict"], "not relevant")

    def test_whole_words_only(self):
        self.assertEqual(self.verdict("ML Engineer", "PostgreSQL and Pythonic code.")["checks"]["rule2_skills"]["matched"], [])
        self.assertFalse(self.verdict("AI Engineering Manager", "Python, SQL")["checks"]["rule1_title"]["passed"])
        self.assertFalse(self.verdict("Sr. Product Manager, Data Engineering", "Python, SQL")["checks"]["rule1_title"]["passed"])

    def test_html_is_decoded_before_matching(self):
        p = {"id": 1, "title": "ML Engineer", "content": "&lt;ul&gt;&lt;li&gt;Python&lt;/li&gt;&lt;li&gt;SQL&lt;/li&gt;&lt;/ul&gt;"}
        self.assertEqual(judge.record_verdict(p, RESUME)["verdict"], "relevant")

    def test_ai_alone_in_a_title_is_not_enough(self):
        r = self.verdict("Director, Marketing Strategy and AI Transformation", "Python and SQL.")
        self.assertFalse(r["checks"]["rule1_title"]["passed"])

    def test_software_engineer_needs_an_ai_word(self):
        self.assertTrue(self.verdict("Senior Software Engineer, AI Runtime", "")["checks"]["rule1_title"]["passed"])
        self.assertFalse(self.verdict("Senior Software Engineer, Payments", "")["checks"]["rule1_title"]["passed"])

    def test_blocker_applies_even_when_negated(self):
        r = self.verdict("ML Engineer", "Python and SQL. No security clearance required.")
        self.assertEqual(r["verdict"], "not relevant")
        self.assertEqual(r["checks"]["rule3_blocker"]["found_in"], ["content"])

    def test_each_skill_counted_once(self):
        r = self.verdict("ML Engineer", "Python, python, PYTHON.")
        self.assertEqual(len(r["checks"]["rule2_skills"]["matched"]), 1)
        self.assertEqual(r["verdict"], "not relevant")


class WrongVersion1VerdictOnTheWrongId(Offline):
    """Section 5, wrong version 1: a verdict must sit on the id it was computed from."""

    EXPECTED = {11: "relevant", 12: "not relevant", 13: "relevant", 14: "not relevant"}

    def postings(self):
        return [posting(11, "ML Engineer", "Python and SQL."), posting(12, "Account Executive", "Python and SQL."),
                posting(13, "Data Engineer", "SQL and AWS."), posting(14, "AI Engineer", "Go only.")]

    def test_verdicts_follow_ids_not_positions(self):
        for order in (self.postings(), list(reversed(self.postings()))):
            got = {r["posting_id"]: r["verdict"] for r in (judge.record_verdict(p, RESUME) for p in order)}
            self.assertEqual(got, self.EXPECTED)

    def test_watch_run_keeps_both_verdicts_on_each_new_id(self):
        with tempfile.TemporaryDirectory() as d:
            state, out = Path(d) / "state.json", Path(d) / "runs"
            ask = fake_claude({1005: {"posting_id": 1005, "verdict": "not relevant", "resume_fields": [],
                                      "posting_fields": ["title"], "matched_terms": [], "reason": "A sales role."},
                               1006: {"posting_id": 1006, "verdict": "relevant", "resume_fields": ["skills.languages"],
                                      "posting_fields": ["content"], "matched_terms": ["Python", "SQL"],
                                      "reason": "ML work using Python and SQL."}})
            watch.run("databricks", PERSONA, state, out, from_file=DAY1, now=T1, prompt=PROMPT, ask=ask)
            record, _, _ = watch.run("databricks", PERSONA, state, out, from_file=DAY2, now=T2, prompt=PROMPT, ask=ask)
        by_id = {p["id"]: p for p in record["new_postings"]}
        self.assertEqual(sorted(by_id), [1005, 1006])
        for i, p in by_id.items():
            self.assertEqual(p["record"]["posting_id"], i)
            self.assertEqual(p["judgment"]["posting_id"], i)
        self.assertEqual(by_id[1005]["record"]["verdict"], "not relevant")
        self.assertEqual(by_id[1006]["record"]["verdict"], "relevant")
        self.assertEqual(by_id[1006]["judgment"]["verdict"], "relevant")


class WrongVersion2ReasonWithoutEvidence(Offline):
    """Section 5, wrong version 2: every reason names real fields and values, and explains failures."""

    def test_relevant_reason_names_fields_and_values(self):
        r = judge.record_verdict(posting(1, "Staff Machine Learning Engineer", "Python and SQL."), RESUME)
        for s in ("title", "'Staff Machine Learning Engineer'", "content",
                  "Python (skills.languages)", "SQL (skills.languages)", "rule 3 passed"):
            self.assertIn(s, r["reason"])

    def test_not_relevant_reason_explains_every_failed_check(self):
        r = judge.record_verdict(posting(1, "Account Executive", "Go. Active security clearance."), RESUME)
        for s in ("rule 1 failed", "rule 2 failed", "rule 3 failed", "skills.languages"):
            self.assertIn(s, r["reason"])

    def test_every_cited_skill_is_in_the_posting_and_the_resume(self):
        texts = ["Python and SQL.", "MLflow, Delta Lake, AWS.", "LangGraph and Power BI.", "Nothing here."]
        for i, t in enumerate(texts):
            p = posting(i, "ML Engineer", t)
            for h in judge.record_verdict(p, RESUME)["checks"]["rule2_skills"]["matched"]:
                self.assertTrue(judge.has_phrase(h["skill"], judge.clean_text(p["content"])))
                group = h["resume_field"].split(".", 1)[1]
                self.assertIn(h["skill"], RESUME["skills"][group])


class Validator(Offline):
    """Section 2: exactly six fields; wrong answers are rejected, never fixed."""

    P = posting(42, "Staff Machine Learning Engineer", "Python and SQL. PostgreSQL experience. LangGraph agents.")
    GOOD = {"posting_id": 42, "verdict": "relevant", "resume_fields": ["skills.languages"],
            "posting_fields": ["content"], "matched_terms": ["Python"], "reason": "Both mention Python."}

    def check(self, answer):
        text = answer if isinstance(answer, str) else json.dumps(answer)
        return judge.validate(text, self.P, judge.claude_view(self.P, RESUME))

    def with_(self, **changes):
        return {**self.GOOD, **changes}

    def assertInvalid(self, answer):
        a, errors = self.check(answer)
        self.assertIsNone(a)
        self.assertTrue(errors)

    def test_good_answer_is_valid(self):
        self.assertEqual(self.check(self.GOOD), (self.GOOD, []))

    def test_code_fences_or_extra_text_are_invalid(self):
        self.assertInvalid("```json\n" + json.dumps(self.GOOD) + "\n```")
        self.assertInvalid("Here is my answer: " + json.dumps(self.GOOD))

    def test_missing_or_extra_fields_are_invalid(self):
        self.assertInvalid({k: v for k, v in self.GOOD.items() if k != "reason"})
        self.assertInvalid(self.with_(confidence=0.9))

    def test_wrong_or_string_posting_id_is_invalid(self):
        self.assertInvalid(self.with_(posting_id=43))
        self.assertInvalid(self.with_(posting_id="42"))

    def test_verdict_must_be_exact(self):
        self.assertInvalid(self.with_(verdict="Relevant"))
        self.assertInvalid(self.with_(verdict="maybe"))

    def test_only_the_six_resume_fields(self):
        self.assertInvalid(self.with_(resume_fields=["skills"]))
        self.assertInvalid(self.with_(resume_fields=["skills.familiar_with_not_shipped"]))

    def test_only_title_and_content(self):
        self.assertInvalid(self.with_(posting_fields=["location"]))

    def test_term_must_be_in_the_named_resume_field(self):
        self.assertInvalid(self.with_(resume_fields=["skills.data_bi"]))          # Python is in skills.languages
        self.assertInvalid(self.with_(matched_terms=["PostgreSQL"]))              # not in the résumé at all

    def test_term_must_be_in_the_named_posting_field(self):
        self.assertInvalid(self.with_(posting_fields=["title"]))                  # Python is in content, not title

    def test_term_matches_whole_words_only(self):
        p = posting(42, "ML Engineer", "PostgreSQL only.")
        a, errors = judge.validate(json.dumps(self.with_(matched_terms=["SQL"])), p, judge.claude_view(p, RESUME))
        self.assertTrue(errors)

    def test_term_matching_ignores_capitals(self):
        self.assertEqual(self.check(self.with_(matched_terms=["python"]))[1], [])

    def test_term_can_come_from_experience(self):
        self.assertEqual(self.check(self.with_(resume_fields=["experience"], matched_terms=["LangGraph"]))[1], [])

    def test_relevant_needs_a_matched_term(self):
        self.assertInvalid(self.with_(matched_terms=[]))

    def test_not_relevant_may_have_no_terms(self):
        a = self.with_(verdict="not relevant", resume_fields=[], posting_fields=[], matched_terms=[], reason="Too senior.")
        self.assertEqual(self.check(a)[1], [])

    def test_empty_reason_is_invalid(self):
        self.assertInvalid(self.with_(reason="  "))


class ClaudeCall(unittest.TestCase):
    """Section 3: Claude gets no tools, no project files, no saved session; the model is recorded."""

    ENVELOPE = {"type": "result", "is_error": False, "result": '{"posting_id": 1}',
                "modelUsage": {"claude-sonnet-5-5": {}}}

    def test_command_turns_every_tool_off(self):
        cmd = judge.claude_command("PROMPT TEXT", "claude-sonnet-5-5")
        self.assertEqual(cmd[:2], ["claude", "-p"])
        self.assertEqual(cmd[cmd.index("--tools") + 1], "")
        self.assertEqual(cmd[cmd.index("--system-prompt") + 1], "PROMPT TEXT")
        self.assertEqual(cmd[cmd.index("--model") + 1], "claude-sonnet-5-5")
        for flag in ("--strict-mcp-config", "--no-session-persistence"):
            self.assertIn(flag, cmd)

    def fake_run(self, stdout, returncode=0, seen=None):
        def run(cmd, **kw):
            if seen is not None:
                seen.update(cwd=kw["cwd"], files=list(Path(kw["cwd"]).iterdir()), input=kw["input"])
            return subprocess.CompletedProcess(cmd, returncode, stdout=stdout, stderr="boom")
        return run

    def test_runs_in_an_empty_temporary_folder_and_reports_the_model(self):
        seen = {}
        with mock.patch.object(judge.subprocess, "run", self.fake_run(json.dumps(self.ENVELOPE), seen=seen)):
            text, models = REAL_CALL_CLAUDE("PROMPT", "MESSAGE", "claude-sonnet-5-5")
        self.assertEqual((text, models), ('{"posting_id": 1}', ["claude-sonnet-5-5"]))
        self.assertEqual(seen["files"], [])
        self.assertNotEqual(Path(seen["cwd"]).resolve(), FOLDER)
        self.assertFalse(Path(seen["cwd"]).exists())                              # removed afterwards

    def test_failures_are_unavailable(self):
        for stdout, code in (("", 1), ("not json", 0), (json.dumps({**self.ENVELOPE, "is_error": True}), 0)):
            with mock.patch.object(judge.subprocess, "run", self.fake_run(stdout, code)):
                with self.assertRaises(judge.ClaudeUnavailable):
                    REAL_CALL_CLAUDE("PROMPT", "MESSAGE", "m")

    def test_missing_cli_is_unavailable(self):
        def missing(*a, **k):
            raise FileNotFoundError("claude")
        with mock.patch.object(judge.subprocess, "run", missing):
            with self.assertRaises(judge.ClaudeUnavailable):
                REAL_CALL_CLAUDE("PROMPT", "MESSAGE", "m")

    def test_claude_sees_no_contact_details(self):
        view = judge.claude_view(posting(1, "ML Engineer", "Python"), RESUME)
        message = json.dumps(view)
        self.assertEqual(sorted(view["resume"]), ["experience", "projects", "skills"])
        self.assertEqual(sorted(view["resume"]["skills"]), sorted(judge.SKILL_GROUPS))
        for secret in ("example.com", "555", "linkedin", "personal"):
            self.assertNotIn(secret, message)


class JudgmentRecord(Offline):
    """Section 2: a JUDGMENT is labeled, valid / invalid / unavailable, and never invented."""

    P = posting(7, "ML Engineer", "Python and SQL.")
    GOOD = {"posting_id": 7, "verdict": "relevant", "resume_fields": ["skills.languages"],
            "posting_fields": ["content"], "matched_terms": ["SQL"], "reason": "SQL in both."}

    def test_valid_answer_is_labeled_and_records_the_model(self):
        j = judge.judgment(self.P, RESUME, PROMPT, ask=fake_claude({7: self.GOOD}))
        self.assertEqual((j["status"], j["verdict"]), ("valid", "relevant"))
        self.assertIn("opinion", j["label"])
        self.assertEqual(j["model_requested"], judge.DEFAULT_MODEL)
        self.assertEqual(j["models_reported"], ["fake-model (test)"])
        self.assertEqual(len(j["prompt_sha256"]), 64)

    def test_invalid_answer_gives_no_verdict_and_keeps_the_raw_text(self):
        raw = "```json\n" + json.dumps(self.GOOD) + "\n```"
        j = judge.judgment(self.P, RESUME, PROMPT, ask=fake_claude({7: raw}))
        self.assertEqual((j["status"], j["verdict"], j["raw_answer"]), ("invalid", None, raw))

    def test_unavailable_claude_gives_no_verdict(self):
        j = judge.judgment(self.P, RESUME, PROMPT, ask=fake_claude({7: judge.ClaudeUnavailable("offline")}))
        self.assertEqual((j["status"], j["verdict"]), ("unavailable", None))


class WatchWithJudges(Offline):
    """Sections 2 and 3: a bad or missing JUDGMENT never removes the RECORD or blocks the state update."""

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state, self.out = Path(self.tmp.name) / "state.json", Path(self.tmp.name) / "runs"
        watch.run("databricks", PERSONA, self.state, self.out, from_file=DAY1, now=T1, prompt=PROMPT, ask=blocked)

    def day2(self, answers, prompt=PROMPT):
        return watch.run("databricks", PERSONA, self.state, self.out, from_file=DAY2, now=T2,
                         prompt=prompt, ask=fake_claude(answers))[0]

    def test_judgment_never_replaces_the_record(self):
        says_relevant = {"posting_id": 1005, "verdict": "relevant", "resume_fields": ["skills.languages"],
                         "posting_fields": ["content"], "matched_terms": ["Python"], "reason": "Python appears."}
        rec = self.day2({1005: says_relevant, 1006: says_relevant | {"posting_id": 1006}})
        p = {x["id"]: x for x in rec["new_postings"]}[1005]
        self.assertEqual((p["judgment"]["verdict"], p["record"]["verdict"]), ("relevant", "not relevant"))

    def test_invalid_and_unavailable_judgments_still_update_state(self):
        rec = self.day2({1005: "not json", 1006: judge.ClaudeUnavailable("offline")})
        statuses = {p["id"]: p["judgment"]["status"] for p in rec["new_postings"]}
        self.assertEqual(statuses, {1005: "invalid", 1006: "unavailable"})
        self.assertTrue(all(p["record"]["verdict"] for p in rec["new_postings"]))
        self.assertIn(1006, json.loads(self.state.read_text())["seen_ids"])

    def test_no_judgment_records_unavailable(self):
        rec = self.day2({}, prompt=None)
        self.assertEqual({p["judgment"]["status"] for p in rec["new_postings"]}, {"unavailable"})

    def test_report_labels_the_judgment_as_an_opinion(self):
        self.day2({1005: "not json", 1006: "not json"})
        report = (self.out / "report-databricks-2026-10-29T120000Z.md").read_text()
        self.assertIn("JUDGMENT (Claude's opinion)", report)
        self.assertIn("| 1006 | Staff Machine Learning Engineer | relevant | _invalid_ |", report)

    def test_missing_prompt_file_is_refused(self):
        with self.assertRaises(watch.InputError):
            self.day2({}, prompt=Path(self.tmp.name) / "no-such-prompt.md")


if __name__ == "__main__":
    unittest.main()
