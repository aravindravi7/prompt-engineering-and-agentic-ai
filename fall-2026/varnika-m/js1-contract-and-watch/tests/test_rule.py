"""Rules 1-5 from CONTRACT.md section 4, and the explanation requirement in section 2."""

import re
import unittest

from agent.rule import description_text, judge
from tests.helpers import load_persona, posting

RESUME = load_persona()
SKILL_FIELDS = ["skills.languages", "skills.backend_automation", "skills.database_cloud", "skills.devops_cicd"]


def check(result, rule):
    return next(c for c in result["checks"] if c["rule"] == rule)


def us_job(title="Software Engineer", body="<p>Python and AWS.</p>", location="San Francisco, CA"):
    return judge(posting(1, title, location, body), RESUME)


class WorkedExample(unittest.TestCase):
    def test_contract_worked_example_is_match(self):
        p = posting(1, "Software Engineer", "United States",
                    "<p>The job asks for 2+ years of experience and mentions Python, AWS, and Kubernetes.</p>")
        result = judge(p, RESUME)
        self.assertEqual(result["verdict"], "MATCH")
        self.assertEqual(sorted(m["skill"] for m in check(result, "R5")["matches"]), ["AWS", "Kubernetes", "Python"])

    def test_all_five_checks_reported_even_when_rule_1_fails(self):
        result = us_job(title="Account Executive")
        self.assertEqual([c["rule"] for c in result["checks"]], ["R1", "R2", "R3", "R4", "R5"])
        self.assertEqual(result["verdict"], "NOT_MATCH")


class Rule1Title(unittest.TestCase):
    def test_listed_phrases_pass_ignoring_case(self):
        for title in ["Software Engineer, Sandboxing", "site reliability engineer", "Data Engineer, GTM"]:
            self.assertTrue(check(us_job(title=title), "R1")["passed"], title)

    def test_complete_words_only(self):
        self.assertFalse(check(us_job(title="Software Engineering Generalist"), "R1")["passed"])

    def test_unlisted_engineer_title_fails(self):
        self.assertFalse(check(us_job(title="Research Engineer"), "R1")["passed"])


class Rule2Seniority(unittest.TestCase):
    def test_each_excluded_word_fails(self):
        for word in ["Senior", "Sr.", "Staff+", "Principal", "Lead", "Manager", "Director", "Head", "VP",
                     "Intern", "Internship"]:
            self.assertFalse(check(us_job(title="%s Software Engineer" % word), "R2")["passed"], word)

    def test_excluded_word_inside_a_longer_word_passes(self):
        self.assertTrue(check(us_job(title="Software Engineer, Leadership Tools"), "R2")["passed"])


class Rule3Location(unittest.TestCase):
    def test_contract_examples(self):
        self.assertTrue(check(us_job(location="Remote-Friendly (Travel Required) | San Francisco, CA"), "R3")["passed"])
        self.assertTrue(check(us_job(location="London, UK; San Francisco, CA"), "R3")["passed"])
        self.assertFalse(check(us_job(location="Remote-Friendly (Travel Required) | Canada"), "R3")["passed"])

    def test_united_states_words_pass(self):
        self.assertTrue(check(us_job(location="Remote-Friendly, United States"), "R3")["passed"])

    def test_remote_alone_fails(self):
        self.assertFalse(check(us_job(location="Remote"), "R3")["passed"])

    def test_letters_after_comma_that_are_not_a_state_code_fail(self):
        for location in ["Ontario, CAN", "Zürich, CH", "Dublin, IE", "London, UK"]:
            self.assertFalse(check(us_job(location=location), "R3")["passed"], location)

    def test_dc_passes(self):
        self.assertTrue(check(us_job(location="Washington, DC"), "R3")["passed"])


class Rule4Experience(unittest.TestCase):
    def years_check(self, sentence):
        return check(us_job(body="<p>Python and AWS. %s</p>" % sentence), "R4")

    def test_contract_examples(self):
        self.assertTrue(self.years_check("2+ years of experience")["passed"])
        self.assertTrue(self.years_check("at least 3 years in data engineering")["passed"])
        self.assertFalse(self.years_check("3–5 years of software engineering experience")["passed"])
        self.assertFalse(self.years_check("4+ years building secure IT systems")["passed"])
        self.assertTrue(self.years_check("No years mentioned here.")["passed"])

    def test_spelled_out_numbers_are_not_counted(self):
        result = self.years_check("A clearance held within the last two years. Your last three years of work.")
        self.assertTrue(result["passed"])
        self.assertEqual(result["years_found"], [])

    def test_range_with_hyphen_uses_higher_number(self):
        result = self.years_check("5-8 years of experience")
        self.assertFalse(result["passed"])
        self.assertEqual([y["years"] for y in result["years_found"]], [8])

    def test_three_is_the_limit(self):
        self.assertTrue(self.years_check("3+ years of experience")["passed"])
        self.assertFalse(self.years_check("4+ years of experience")["passed"])

    def test_highest_of_several_phrases_decides(self):
        self.assertTrue(self.years_check("2+ years of Python and 3+ years of Kafka")["passed"])
        self.assertFalse(self.years_check("2+ years of Python and 6+ years overall")["passed"])

    def test_preferred_qualifications_count_too(self):
        self.assertFalse(self.years_check("Preferred qualifications: 5+ years of experience")["passed"])

    def test_two_digit_number_is_read_whole(self):
        result = self.years_check("12+ years of experience")
        self.assertEqual([y["years"] for y in result["years_found"]], [12])


class Rule5Skills(unittest.TestCase):
    def test_wrong_version_1_skills_only_in_description_still_count(self):
        result = us_job(title="Software Engineer", body="<p>You will use Python and AWS every day.</p>")
        self.assertTrue(check(result, "R5")["passed"])
        self.assertEqual({m["skill"]: m["posting_fields"] for m in check(result, "R5")["matches"]},
                         {"Python": ["content"], "AWS": ["content"]})

    def test_wrong_version_2_javascript_does_not_count_as_java(self):
        result = us_job(body="<p>JavaScript and Python.</p>")
        skills = [m["skill"] for m in check(result, "R5")["matches"]]
        self.assertNotIn("Java", skills)
        self.assertFalse(check(result, "R5")["passed"])

    def test_sql_inside_postgresql_or_nosql_does_not_count_as_sql(self):
        result = us_job(body="<p>PostgreSQL and NoSQL.</p>")
        self.assertEqual([m["skill"] for m in check(result, "R5")["matches"]], ["PostgreSQL"])

    def test_familiar_with_not_shipped_skills_do_not_count(self):
        result = us_job(body="<p>Rust and Terraform.</p>")
        self.assertEqual(check(result, "R5")["matches"], [])

    def test_one_skill_is_not_enough(self):
        self.assertFalse(check(us_job(body="<p>Python only.</p>"), "R5")["passed"])

    def test_skill_inside_escaped_html_is_found(self):
        result = us_job(body="<ul><li>Kubernetes</li><li>Docker</li></ul>")
        self.assertEqual(sorted(m["skill"] for m in check(result, "R5")["matches"]), ["Docker", "Kubernetes"])

    def test_skill_list_is_the_contracts_fifteen(self):
        skills = [s for field in SKILL_FIELDS for s in RESUME["skills"][field.split(".")[1]]]
        self.assertEqual(sorted(skills), sorted([
            "TypeScript", "Python", "Java", "SQL", "Node.js", "Kafka", "Redis", "MSSQL", "PostgreSQL",
            "AWS", "Kubernetes", "Docker", "Helm", "Fluent Bit", "Jenkins"]))


class ExplanationsCanBeChecked(unittest.TestCase):
    """Section 2: every rule names a résumé field and a posting field with the values compared.
    Section 6: a verdict that cannot be checked against the fields it lists is a failure."""

    POSTINGS = [
        posting(1, "Software Engineer", "United States", "<p>2+ years. Python, AWS, Kubernetes.</p>"),
        posting(2, "Senior Data Engineer", "London, UK", "<p>5-8 years. SQL and Kafka.</p>"),
        posting(3, "Account Executive", "Remote", "<p>JavaScript only.</p>"),
    ]

    def test_every_check_names_both_fields_and_an_explanation(self):
        for p in self.POSTINGS:
            for c in judge(p, RESUME)["checks"]:
                self.assertIn("posting_value", c)  # may be empty, e.g. no years phrase found
                for key in ["posting_field", "resume_field", "resume_value", "explanation"]:
                    self.assertTrue(c.get(key), (p["id"], c["rule"], key))

    def test_cited_posting_values_are_in_the_posting(self):
        for p in self.POSTINGS:
            result = judge(p, RESUME)
            self.assertEqual(check(result, "R1")["posting_value"], p["title"])
            self.assertEqual(check(result, "R2")["posting_value"], p["title"])
            self.assertEqual(check(result, "R3")["posting_value"], p["location"]["name"])
            text = description_text(p["content"])
            for found in check(result, "R4")["years_found"]:
                self.assertIn(found["phrase"], text)
            for m in check(result, "R5")["matches"]:
                for field in m["posting_fields"]:
                    source = p["title"] if field == "title" else text
                    self.assertRegex(source, re.compile(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(m["skill"]), re.I))

    def test_cited_resume_values_are_in_the_resume(self):
        result = judge(self.POSTINGS[0], RESUME)
        self.assertEqual(check(result, "R1")["resume_value"], [e["title"] for e in RESUME["experience"]])
        self.assertEqual(check(result, "R3")["resume_value"], RESUME["personal"]["location"])
        for m in check(result, "R5")["matches"]:
            self.assertIn(m["skill"], RESUME["skills"][m["resume_field"].split(".")[1]])

    def test_experience_months_are_recomputed_from_the_resume(self):
        months = 0
        for e in RESUME["experience"]:
            (y1, m1), (y2, m2) = [map(int, e[k].split("-")) for k in ("start_date", "end_date")]
            months += (y2 - y1) * 12 + (m2 - m1)
        self.assertEqual(months, 29)
        self.assertEqual(check(judge(self.POSTINGS[0], RESUME), "R4")["resume_value"], "29 months")


if __name__ == "__main__":
    unittest.main()
