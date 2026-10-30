# CONTRACT — Job-Search Agent 1

Written: October 29, 2026 by Pavan Majji, before any implementation.

## In

- **Board:** Greenhouse, slug `gleanwork`, host `boards-api.greenhouse.io`.
- **Résumé:** A fictional JSON file with required fields `name`, `email`, `phone`, `target_titles`, `skills`, and `locations`. Only `target_titles`, `skills`, and `locations` are used by the deterministic relevance rule. Optional realism fields are `experience` and `education`; the deterministic rule ignores them.
- **State:** A local JSON file containing previously seen posting IDs. Its path is provided through configuration.
- **Raw response:** The agent can fetch the current Greenhouse board response or load a previously saved raw JSON response from a local file for a seeded run.
- **Needs:** Network access to the allow-listed hosts `boards-api.greenhouse.io` and `api.anthropic.com`. Greenhouse is used for posting data; Anthropic is used for judgment. API credentials are read from environment variables only. Any local `.env` file must be listed in `.gitignore`.
- **Posting fields:** The agent reads `id`, `title`, `content`, and `location.name`. The `id` is used for tracking, not relevance matching.

## Out

For each new posting, the agent produces two separate verdicts:

1. **Record:** The deterministic rule verdict, either `relevant` or `not_relevant`.
2. **Judgment:** Claude's verdict, either `relevant` or `not_relevant`, or `invalid` if Claude's response fails validation after one retry.

Each result includes:

- Posting `id` and `title`.
- The verdict and its source label, exactly `record` or `judgment`.
- A justification identifying the résumé fields and posting fields used, with matching values or the failed condition.
- Evidence supporting the deterministic rule result.

Every run saves the complete raw Greenhouse JSON response, unchanged, to a timestamped local file before processing. The filename identifies the run timestamp and distinguishes seeded runs from live runs.

A seeded run must be labeled `seeded` in its run metadata and output. It processes the supplied local response without fetching the Greenhouse board. The `seeded` label describes the input mode; it does not replace the `record` or `judgment` source labels.

Claude receives the posting data and Alex's fictional résumé data through a request to `api.anthropic.com`. Because the résumé is fictional, this is acceptable for this test project. The report must make this data transfer explicit.

Claude's output must conform to the schema defined below. The agent retries an invalid response once. If the second response is invalid or the API request fails, the judgment is reported as `invalid`, with the failure reason recorded. The deterministic rule verdict remains available.

## Refuses

- **Unapproved network access:** The only permitted network hosts are `boards-api.greenhouse.io` for posting data and `api.anthropic.com` for judgment. All other hosts and redirects to unapproved hosts are rejected. The Python implementation must enforce this through a host-checking HTTP transport or custom httpx client (for Greenhouse) or httpx2 client (for the Anthropic SDK, which requires httpx2), including when making Anthropic SDK requests. Checking only the URL string is insufficient.
- **Nonfictional résumé identity:** Before any network request or judgment step, a validator requires an email ending in `@example.com` and a phone number containing `555-` followed by exactly four digits. The phone check is a format check, not proof that the number is unassigned. I wrote the persona's employment history and education as fictional test data; this is a manual responsibility and is not checked by code.
- **Unlabeled judgments:** Claude's verdict must always carry the exact source label `judgment`. Output validation rejects missing or incorrect labels.
- **Unsupported field citations:** Every verdict must identify at least one permitted résumé field and one existing posting field. The validator rejects citations to fields that are not permitted or do not exist in the supplied input.
- **Secrets in files:** Credentials must be read from environment variables only. The `.env` file must be excluded through `.gitignore`, and credentials must never appear in logs, raw-response files, or reports.
- **Corrupted state:** The agent must preserve the previous valid state file if fetching or rule processing fails. State writes must be atomic.

## The rule

A posting is `relevant` if and only if all three checks pass. The deterministic rule uses only `target_titles`, `skills`, and `locations` from the résumé. It ignores `experience` and `education`.

### 1. Title check

- Compare `target_titles` against the posting's `title`.
- Matching is case-insensitive substring containment. For example, `Senior Software Engineer` matches `Software Engineer`.
- Reject titles containing the standalone word `intern` or `internship`, `manager`, or `director`, regardless of case. These exclusions take precedence over a positive match.
- A missing or empty title fails the check.
- The justification identifies résumé field `target_titles` and posting field `title`, including the matched target title or reason for failure.

### 2. Skills check

- Decode HTML entities in `content` first, then strip HTML tags, remove script and style contents, and normalize whitespace. This order is required because Glean's content can contain escaped markup such as `&lt;div&gt;`.
- Match at least **3 distinct skills** from the résumé's `skills` list against the cleaned description.
- Matching is case-insensitive. A match must not have a letter or digit immediately before or after the matched term.
- Internal spaces in a skill phrase match one or more whitespace characters in the description. Punctuation inside a skill must match literally after HTML decoding; it is not interchangeable with arbitrary punctuation.
- Therefore, `Java` does not match `JavaScript`, and `Spring Boot` matches `Spring   Boot` but not `Spring-Boot`. `CI/CD` matches `CI/CD`, but not `CI CD`.
- Match skill names as written. Do not infer synonyms or equivalent technologies. For example, `REST APIs` does not match `RESTful APIs`, and `Apache Kafka` does not match `Kafka`.
- Each skill counts at most once, regardless of how many times it appears in the description.
- Missing or empty content fails the check.
- The justification identifies résumé field `skills` and posting field `content`, listing matching skills or explaining why the minimum was not reached.

**Known limitation:** Exact skill phrases may miss common variants such as `Kafka` for `Apache Kafka`. This is intentional for version 1 to keep matching deterministic.

### 3. Location check

- Compare résumé field `locations` against posting field `location.name`.
- Matching is case-insensitive substring containment after trimming leading and trailing whitespace and normalizing repeated spaces.
- A target location of `San Francisco, CA` matches a posting location containing that phrase.
- A target location of `Remote` matches any posting location containing `Remote`, including `Remote - Canada` and `Remote - EMEA`. This behavior is intentional in version 1 and may produce geographic false positives.
- A missing or empty posting location fails the check. The agent must not infer remote eligibility from a missing value.
- The justification identifies résumé field `locations` and posting field `location.name`, including the matched value or reason for failure.

### Combining the checks

All three checks must pass for a `record` verdict of `relevant`. If any check fails, the `record` verdict is `not_relevant`.

Claude independently judges each new posting and produces a `judgment` verdict. Claude may consider the full fictional résumé, including `experience` and `education`, but may cite only these résumé fields:

- `target_titles`
- `skills`
- `locations`
- `experience`
- `education`

Claude must not cite `name`, `email`, or `phone` as relevance evidence. It may cite only posting fields that actually exist in the supplied posting.

This distinction is intentional: Claude may find relevant experience in `experience` that the deterministic rule ignores. The two verdicts can therefore disagree, and reports must preserve both results rather than silently treating one as the other.

### Claude output schema and validation

Claude must return exactly one JSON object with these keys and no additional keys:

```json
{
  "verdict": "relevant",
  "justification": "The posting matches the target title and lists relevant backend skills.",
  "resume_fields": ["target_titles", "skills"],
  "posting_fields": ["title", "content"]
}
```

Requirements:

- `verdict` must be exactly `relevant` or `not_relevant`.
- `justification` must be a nonempty string.
- `resume_fields` must be a nonempty array containing only permitted résumé field names.
- `posting_fields` must be a nonempty array containing only existing posting field names.
- Every cited field must have a nonempty value in the input.
- The response must contain valid JSON only. Markdown fences, introductory text, trailing commentary, missing keys, extra keys, and incorrect value types are rejected.
- The validator checks structure, allowed field names, and nonempty cited values. It does not prove that Claude's justification is truthful or that its reasoning is sound.
- On rejection, retry once. If the retry fails validation or the API request fails, output `judgment: invalid` and record the error. Do not fabricate a valid verdict or evidence.

The agent attaches the `judgment` source label outside Claude's JSON response. Claude does not control the label.

## Watch rules

- A posting is new if its `id` does not exist in the previously saved state.
- On the first live run, if the state file does not exist, the agent performs a baseline: it saves the retrieved IDs and reports **0 new postings**.
- On subsequent successful runs, only previously unseen IDs are reported as new.
- A seeded run uses a saved response file and is explicitly labeled `seeded`. It uses the same relevance rules and Claude validation as a live run. Its baseline or new-posting behavior follows the existing state file.
- Every run saves its full raw input response to a timestamped file before processing. A seeded run preserves the supplied raw response without modifying it.
- After a successful fetch and rule-processing step, the state is updated with the union of previously seen IDs and successfully processed posting IDs. Disappearing postings do not cause their IDs to be removed.
- State depends only on a successful fetch and rule step. A Claude API outage or invalid judgment is reported but does not block the state update.
- If fetching or rule processing fails, the state must not advance.
- A posting with no usable `id` is rejected from tracking and reported as a validation error. The agent must never invent an ID.

## Wrong versions my tests must catch

1. **Shifted labels:** Verdicts are attached to the wrong posting. Caught by `test_verdicts_remain_associated_with_correct_posting_ids`, which verifies that two postings retain their own IDs, titles, verdicts, and evidence.

2. **Empty justification:** A verdict cites no valid fields. Caught by `test_every_verdict_has_resume_and_posting_field_evidence`, which verifies that each verdict cites at least one existing résumé field and one existing posting field.

3. **Incorrect baseline:** The first run reports all existing postings as new. Caught by `test_first_run_baseline_reports_zero_new_postings`.

4. **Unsafe input:** An unapproved host is fetched or an invalid résumé identity is accepted. Caught by `test_rejects_unapproved_hosts_and_redirects` and `test_rejects_nonfictional_resume_identity`.

5. **Incorrect skill matching:** `JavaScript` counts as `Java`, escaped HTML is not cleaned correctly, or fewer than three distinct skills count as a match. Caught by `test_skills_require_three_distinct_whole_word_matches`.

6. **Invalid Claude response:** Claude returns extra text, missing keys, an invalid verdict, or nonexistent or empty cited fields. Caught by `test_invalid_judgment_retries_once_then_marks_invalid`.

7. **State advances after rule failure:** A failed fetch or rule step permanently skips unprocessed postings. Caught by `test_failed_fetch_or_rule_preserves_previous_state`.

8. **Seeded run fetches the network:** The agent makes a Greenhouse request even though a saved response was supplied. Caught by `test_seeded_run_uses_saved_response_without_greenhouse_request`.

## What a failure looks like

October 29, 2026: The agent has failed if it reports an already-seen posting as new, processes an invalid résumé, fetches an unapproved host, fails to save the raw response, mislabels a seeded run, or produces a verdict without a valid source label and evidence citing existing permitted résumé and posting fields.

## Revisions after the first commit
- October 30, 2026: The Anthropic SDK (anthropic 2.3.0) requires an `httpx2.Client`, not `httpx`. The allow-list for the Claude call is enforced with the same host-check hook on an `httpx2` client. Behavior is unchanged; only the library name was corrected.

- October 30, 2026: Per TA instruction, the Claude judgment uses the Northeastern-provided claude.ai chat, not the API. `agent/manual_judge.py` builds each prompt with the same builder as `judge_claude`; I paste it into a fresh claude.ai chat, save the reply to a file, and the same `validate_reply` from `agent/judge.py` accepts or rejects it, with one retry. No API key is used, and the code makes no request to `api.anthropic.com`; the résumé fields sent to Claude are typed into claude.ai by me instead.