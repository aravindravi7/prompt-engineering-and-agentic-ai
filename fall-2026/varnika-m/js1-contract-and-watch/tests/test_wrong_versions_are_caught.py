"""CONTRACT.md section 5: run each wrong-version test against that wrong version, and check that it fails.

A test that also passes on the wrong version would not be catching anything.
Added after the implementation, to show the two committed tests do their job.
"""

import re
import unittest
from unittest import mock

from agent import rule
from tests import test_rule

WRONG_1 = "Rule5Skills.test_wrong_version_1_skills_only_in_description_still_count"
WRONG_2 = "Rule5Skills.test_wrong_version_2_javascript_does_not_count_as_java"
REAL_FIND_SKILLS = rule.find_skills


def passes(test_name):
    result = unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromName(test_name, test_rule).run(result)
    return result.wasSuccessful()


def title_only(title, description, resume):
    return REAL_FIND_SKILLS(title, "", resume)


def partial_words(term):
    return re.compile(re.escape(term), re.I)


class WrongVersionsAreCaught(unittest.TestCase):
    def test_both_tests_pass_on_the_real_rule(self):
        self.assertTrue(passes(WRONG_1))
        self.assertTrue(passes(WRONG_2))

    def test_wrong_version_1_title_only_skills_fails_its_test(self):
        with mock.patch.object(rule, "find_skills", title_only):
            self.assertFalse(passes(WRONG_1))

    def test_wrong_version_2_partial_word_matching_fails_its_test(self):
        with mock.patch.object(rule, "term_pattern", partial_words):
            self.assertFalse(passes(WRONG_2))


if __name__ == "__main__":
    unittest.main()
