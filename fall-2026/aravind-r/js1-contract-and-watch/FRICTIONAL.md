# FRICTIONAL — Job-Search Agent 1

Honest log of what I tried, what broke, and what I accepted, modified or rejected from Claude.
Dates are 2026-10-31 ET unless noted. Facts trace to commits, run folders and tests.
"Claude Code" is the build session in the desktop app; "Claude (chat)" is a separate claude.ai conversation.

## 1. Board scouting happened before the allow-list existed
- What happened: before CONTRACT.md was written, Claude Code made one request each to eight
  Greenhouse boards (stripe, databricks, datadog, mongodb, robinhood, reddit, figma, asana) to count
  PM-family titles. Nothing was saved; it is not evidence.
- Why it matters: my contract's Refuses section forbids fetching any host off the allow-list. No
  contract existed yet, so the agent broke nothing, but this is exactly the behavior I then had to forbid.
- What I take from it: in the next layer, scouting becomes a declared, logged step with its own
  allow-list, not something that happens off the record before the contract.

## 2. "California" never matched Stripe's location strings
- What happened: my first locations value included "California". Claude Code flagged that Stripe's
  `location.name` uses city names, so a substring match on "California" could never pass.
- Changed: replaced it with San Francisco, Los Angeles, San Jose, and made Gate 4 case-insensitive
  for every entry. This was fixed before the contract commit 5656bfb.
- Lesson: write rules against real data, not assumed shapes.

## 3. Gate 2 "Intern" matched "International"
- Found: on the live baseline (runs/20261101T015849Z-live-baseline/), 8 titles containing
  "International" showed a Gate 2 fail. All 8 already failed Gate 1, so no verdict changed, but their
  justifications were wrong.
- Why I amended the contract instead of only logging it: a TA applying the contract literally would
  reproduce the same wrong justification, and the contract has to be something a TA can apply by hand.
- Changed: a dated revision in CONTRACT.md (title terms match whole words only), with the original
  wording kept above it. Code and a new test landed in f762059 (tests 11 → 12). The contract revision
  was committed after that code commit, in f090693. That ordering is out of step with "contract first";
  I'm recording it rather than rewriting history.

## 4. The first seeded run hit my held-out set
- What happened: the first seeded draw removed 8147961, which is held-out 1. Running the Claude judge
  on it would have exposed a held-out posting before the final run.
- Changed: redrew with the same seed (20261031), excluding all 20 labeling postings. The v1 folders
  are kept with a SUPERSEDED.md note in each. v2 asserted exactly 8 new ids, and the assertion passed.
  The run is labeled SEEDED / CONSTRUCTED.
- Decision: I chose the 3 rule-relevant ids; the other 5 were drawn with seed 20261031 from pools I
  defined (3 PM-family not-relevant, 2 non-PM), so both verdicts appear among the new postings. This is
  a constructed test, not an observed change on the board.

## 5. I saw one Claude verdict before hand-labeling
- What happened: the seeded run's report printed Claude's verdict on 8195440, which is dev 9.
- Handling: I labeled dev 9 mechanically by the six gates, as for every other posting, and noted the
  exposure in its gut field. It did not influence the label.

## 6. Run timestamp rolled over to UTC
- The live baseline is stamped 2026-11-01T01:58Z, but locally it was still 31 Oct ET. It does not
  count as a second calendar day; the second run is seeded and labeled as such.

## 7. The Claude CLI wasn't signed in
- claude -p calls failed until I ran claude auth login myself. The rule judge, fetch and state did
  not depend on it; the Claude judge, sampling and prompt experiment did.

## 8. Claude Code misreported dev 2's first failed gate
- Claude Code reported dev 2 (8143563) failing Gate 4 from the location alone; my hand label said
  Gate 3; the record confirmed Gate 3 ("7+ years" against a ceiling of 3; Gate 4, Dublin, also fails
  but comes later). The score was right; the claim in conversation was not.

## 9. Held-out 7: an invalid reply under prompt v1
- On the final held-out run, v1's reply for held-out 7 (7984866, 2026-11-01T02:53:02Z) was a JSON object
  followed by prose ("Correction to the above: …"). The validator rejected it as not a bare JSON object;
  it was recorded as invalid, not repaired or retried, and counts as a fail (v1 held-out 9/10).

## Accepted / modified / rejected from Claude
Accepted:
- Stripe as the board (Claude Code's pick from the scouting counts).
- years_pm = 2: Claude Code computed ~2.2 years across Maya's two PM roles, Claude (chat) recommended
  2, and I set it.
- A seeded second run instead of waiting for a live change (Claude Code, given the deadline).
- The single v2 prompt change: Claude (chat) suggested the evidence-quote change; I chose it and
  specified the validator and the quote-fidelity rule (a required evidence object quoting the
  sentence behind gates 2, 3, 5 and 6, with quote fidelity recorded separately and never changing a
  verdict).

Modified:
- Failure sentence: Claude (chat) gave six example sentences; I took inspiration from one and wrote
  mine myself.
- Locations: replaced "California" with cities after Claude Code flagged the mismatch.
- Domains: removed "semi-conductor" after Claude Code flagged that a whole-word match would miss the
  usual spelling "semiconductor".
- Gate 3: limited to the first "N years" phrase in a sentence containing "experience", after Claude
  Code flagged that company boilerplate (e.g. "over 10 years of building…") would match.

Rejected:
- Claude (chat) suggested a persona shaped like me and my profile. I kept the shipped Maya Sehgal
  persona for three reasons: it was already validated, which saved time; it keeps anything resembling
  my real résumé off GitHub; and a separate, labeled persona-prefs.json adds the rule's fields while
  leaving the shipped résumé untouched.
- Pure random removal for the seeded run: Claude (chat) advised against it (it would almost certainly
  have produced zero relevant postings); Claude Code offered a mix of chosen and seeded-random ids;
  I chose the mix.

## Unresolved
- The rule is very strict: 3 of 745 baseline postings are relevant, and all 3 pass Gate 3 only because
  no years requirement was found. Passing on absence may be too lenient; not tested against hand review.
- Gate 4's substring "Remote" may match non-US remote roles; not checked across all 745 postings.
- Gate 3's sentence extraction is hand-verified only on the 20 labeled postings.
- The sampling report used dev 1–5, likely mostly easy Gate 1 failures, so the consistency it shows
  says little about the hard text gates (2, 3, 5, 6).

## Contract wording
Contract decisions are mine; the wording was drafted with Claude from my decisions and edited by me
(CONTRACT.md, line 3).
