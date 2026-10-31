"""The Claude judgment validator: CONTRACT.md section 2 (Out)."""

import unittest

from agent.claude_judge import validate

GOOD = '{"label":"CLAUDE_JUDGMENT","verdict":"MATCH","reason":"Python and AWS appear in the description."}'


class Validator(unittest.TestCase):
    def assertRejected(self, reply):
        ok, _ = validate(reply)
        self.assertFalse(ok, reply)

    def test_exact_format_is_accepted(self):
        ok, value = validate(GOOD)
        self.assertTrue(ok)
        self.assertEqual(value["verdict"], "MATCH")
        self.assertTrue(validate(GOOD.replace('"MATCH"', '"NOT_MATCH"'))[0])

    def test_surrounding_whitespace_is_allowed(self):
        # Reading of "only this JSON object": a trailing newline from the CLI is not other text.
        self.assertTrue(validate("\n" + GOOD + "\n")[0])

    def test_code_fence_is_rejected(self):
        self.assertRejected("```json\n" + GOOD + "\n```")

    def test_text_before_or_after_is_rejected(self):
        self.assertRejected("Here is my judgment: " + GOOD)
        self.assertRejected(GOOD + " Hope this helps.")

    def test_extra_or_missing_keys_are_rejected(self):
        self.assertRejected(GOOD[:-1] + ',"confidence":0.9}')
        self.assertRejected('{"label":"CLAUDE_JUDGMENT","verdict":"MATCH"}')

    def test_duplicate_keys_are_rejected(self):
        self.assertRejected('{"label":"CLAUDE_JUDGMENT","verdict":"MATCH","verdict":"NOT_MATCH","reason":"x"}')

    def test_other_verdicts_are_rejected(self):
        for verdict in ["match", "MAYBE", "RELEVANT", ""]:
            self.assertRejected(GOOD.replace('"MATCH"', '"%s"' % verdict))

    def test_wrong_label_is_rejected(self):
        self.assertRejected(GOOD.replace("CLAUDE_JUDGMENT", "FACT"))

    def test_empty_or_non_text_reason_is_rejected(self):
        self.assertRejected('{"label":"CLAUDE_JUDGMENT","verdict":"MATCH","reason":"   "}')
        self.assertRejected('{"label":"CLAUDE_JUDGMENT","verdict":"MATCH","reason":42}')

    def test_not_an_object_is_rejected(self):
        self.assertRejected("[" + GOOD + "]")
        self.assertRejected("MATCH")
        self.assertRejected("")


if __name__ == "__main__":
    unittest.main()
