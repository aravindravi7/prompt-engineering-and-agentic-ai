"""Fictional-résumé check: CONTRACT.md section 1 (In) and section 3 (Refuses)."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from agent.resume import ResumeRefused, load_resume
from tests.helpers import PERSONA, load_persona


class FictionalCheck(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir)

    def changed(self, **personal):
        resume = load_persona()
        resume["personal"].update(personal)
        path = self.dir / "resume.json"
        path.write_text(json.dumps(resume))
        return path

    def test_persona_passes(self):
        self.assertEqual(load_resume(PERSONA)["personal"]["location"], "Boston, MA")

    def test_email_outside_example_com_is_refused(self):
        with self.assertRaises(ResumeRefused):
            load_resume(self.changed(email="aarav.patel@realmail.invalid"))

    def test_lookalike_domain_is_refused(self):
        with self.assertRaises(ResumeRefused):
            load_resume(self.changed(email="aarav@notexample.com"))

    def test_phone_without_555_is_refused(self):
        with self.assertRaises(ResumeRefused):
            load_resume(self.changed(phone="(617) 212-0148"))

    def test_missing_contact_fields_are_refused(self):
        resume = load_persona()
        del resume["personal"]["email"]
        path = self.dir / "resume.json"
        path.write_text(json.dumps(resume))
        with self.assertRaises(ResumeRefused):
            load_resume(path)


if __name__ == "__main__":
    unittest.main()
