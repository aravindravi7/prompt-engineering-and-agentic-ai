# FRICTIONAL.md — JS1

This is where things went wrong or didn't go the way I expected while building JS1. I started on Oct 27 (due Oct 31) and finished on Oct 29.

## Oct 27

**My board check had no posting text.** I checked Greenhouse `stripe` with curl and got 711 jobs (`raw/check-2026-10-27.json`), but I forgot `?content=true`, so I only got titles and metadata. R4–R6 need the actual posting text, so that file was useless for them. I switched to fetching with content. Since v0.3 the agent refuses a raw file with no content, so this old check file now errors.

**"Dublin" broke my location rule.** The first posting just said "Dublin", with no country. My rule had no case for that. I changed it so anything not clearly US fails, and "Remote" on its own is unknown. Dublin could also be Dublin, CA or OH, so it's a good false-friend example for JS3.

**The persona I wanted didn't exist.** I wanted to use cole-palmer, but the engine only has aarav-patel, maya-sehgal, priya-nair, and rohan-desai. Priya needs sponsorship, but she targets AI/ML roles, has no years-of-experience field, and her skills are nested in groups, so she didn't fit. I invented Cole Palmer instead (`persona/cole-palmer.example.json`: new-grad MS CS, one co-op, 0 years, needs H-1B). The name is a real footballer's, but the persona is fake (555 phone, @example.com).

**I didn't know what some contract terms meant.** I had to ask what "cannot tell" and "Refuses" meant before I could answer the contract questions.

**My contract had way more holes than I thought.** I committed CONTRACT.md v0.1 and the persona before writing any code (`a842c11`). Then Claude Code read it against the real data and stopped with 16 questions (A–P) instead of guessing. Some of the bad ones:
- "Intern" matched "Software Engineer, Internal Identity" because of substring matching.
- Cities with no state (Chicago, San Francisco, Seattle) failed the location rule.
- "London OR Dublin" passed, because "OR" was read as Oregon.
- "Australia" contains "us".
- A posting with no date would pass R2.
- My "seen posting reported as new" test couldn't actually catch the bug, because the first run is always a baseline with 0 new.

Claude chat also noticed that Claude Code was planning to gitignore `state/`, which the assignment requires us to submit. I fixed all of this in v0.2 (`eb2d5ee`). My lesson: a contract isn't precise until you check it against real data.

**The real location data was messy.** I pulled all the real location values and built the US list from them. Some abbreviations were traps. "Toronto, CA" is Canada, not California. "London OR Dublin" isn't Oregon. "IN-Bengaluru" isn't Indiana. Claude Code's first fix (uppercase only) wouldn't have stopped "OR", because the data writes it in caps. I made abbreviations count only right after a comma or semicolon. "AMER" and "Remote North America" still fail, which I'm leaving as known gaps.

**The build found even more gaps (v0.3).** R2 compares dates, so it has no résumé field, but my contract says every justification has to cite one. Claude also needed the run date and posting id, which weren't on my list. I updated the contract to v0.3 (`f9a5418`).

**Claude Code left the requirements unpinned.** `requirements.txt` had no versions in it, so I pinned `anthropic==2.3.0` and `pytest==9.2.0` myself and re-ran pytest (236 passed) before committing.

**All 236 tests passed on the first try, which made me suspicious.** I did a mutation test: I changed `max(minimums)` to `min(minimums)` at line 151 of `agent/rules.py`. Only 1 test failed: `test_r4_experience[5+ years backend, 2+ years Go-fail]` (it said "largest 2" and passed instead of failing). So the test works, but only one test out of 236 actually checks that case. Evidence: `1d3e809`.

**I overwrote my own evidence.** After undoing the mutation, I ran pytest with `tee` into the same file, which replaced the failing output with "236 passed". I had to redo the mutation and save the two runs to separate files.

**The board kept changing.** It had 711 postings in the morning and 715 at my baseline run (`python -m agent --no-claude`, which reported 0 new as designed). Files: `raw/greenhouse-stripe-2026-10-27T203128.json`, `state/seen_ids.json`, `out/run-2026-10-27T203128.*`. The count is only a snapshot.

**Copy-paste mistakes.** I pasted a Python command with the indentation still in it and got `IndentationError`. Later I pasted a Claude Code prompt into Terminal instead of Claude Code, and zsh tried to run every line. I checked `git status` afterwards to make sure nothing weird got created.

**"Sponsor" doesn't mean what I thought on this board.** I searched all 715 postings for "sponsor". None of the 14 sentences were about visas. They were things like "executive sponsor" and event sponsorships. A simple keyword match would have rejected sales roles for no reason. My phrase list matched none of them, which is right, but it also means the "won't sponsor" failure case never happens with Stripe. I'm marking it as not checked.

**I chased a bug that wasn't real.** I saw `&nbsp;` left in the text and thought R4 was missing years because of it. I asked Claude Code to write a failing test first. The test passed, so Claude Code stopped and didn't change `agent/text.py`. It turned out my check (written by Claude chat) used one `html.unescape`, while the agent's `strip_html` actually decodes twice. I kept the test as a guard (237 tests) and didn't change the code. If I hadn't insisted on the test first, a useless "fix" would have gone in.

**Picking postings to label.** A random 20 from the whole board would have been almost all sales and non-US jobs, so I only picked from titles containing "Engineer" (170 postings), with a fixed seed (7375) in `experiments/select.py`. I wrote `LABELING-RULE.md` before labeling, and labeled all 20 without looking at the code's answers.

**My first label row was wrong.** I left out the label column for 8257892, so everything shifted over by one. I also marked R5 unknown because the posting didn't mention sponsorship, but my own rule says silence means pass. I kept the rule and fixed the row. Claude chat later found 3 more note mistakes in my labels (7947546, 8209307, 8257892). Labels committed in `89d0e94`.

**Only 1 of my 20 labels was relevant.** That means a judge that always says "not relevant" would score 9/10 on dev and 10/10 on held-out. The pass rate mostly measures rejecting. I didn't re-pick postings to get more relevant ones, because that would be picking data after seeing it. A lot of postings also failed just for being old (6717520 was 551 days old).

## Oct 28

**All 16 Claude answers came back invalid.** My second live run found 16 new postings (`raw/greenhouse-stripe-2026-10-28T141616.json`). I checked this myself with a set difference of ids between the two raw files, and it matched. But every Claude call failed with a 401, so the API key was being rejected. Run committed in `c71eaec`.

**Fixing the API key took way too long.**
- My first guess was that I pasted the key prompt wrong. That was wrong; the key looked fine.
- I set it again and the first character got dropped.
- I made a new key. Then Claude chat gave me steps using `pbpaste`, but copying those steps replaced the key on my clipboard, so I saved the command text as my key.
- I tried nano and pressed Cmd+O instead of control+O, which opened Terminal's own dialog.
- I finally used `cat > ~/.js1-anthropic-key` and tested it with a free `/v1/models` call. That worked.

The key lives outside the repo (`~/.js1-anthropic-key`, chmod 600). I ran `grep -r sk-ant` and the only hit is the fake secret in `tests/test_claude_judge.py`. Next time I'll test a key with a free call before a real run.

**The failed run still updated my state file.** So re-running live would show 0 new. I didn't want to fake a second live run. Instead I kept the live run as real evidence and re-ran the Claude judge as a "seeded" run on the same raw file, using the old state restored from git into `state/seen_ids-run2-seeded.json` (output `out/run-2026-10-28T145919.*`). This time all 16 answers were valid, and Claude and the rules agreed on all 16. But they were all easy rejects, and agreeing isn't the same as being right.

Two more small slips: `git show HEAD:state/seen_ids.json` failed because the path needed to be `./state/...`, and I pressed control+C while the SDK was still importing. Neither did any damage.

**The agent didn't stop at the first 401.** It made 16 failing calls and then updated the state anyway. On Oct 29 I had Claude Code fix it to stop right away (exit code 2, no outputs, no state change). It's in contract v0.4 (`cf14bae`).

## Oct 29

**Claude was consistent but wrong on the one posting that mattered.** The baseline prompt (`prompts/baseline.txt`) got 9/10 on dev (`experiments/results/baseline-dev-2026-10-29T190534.*`). The one miss was the only relevant posting (8314283). In the sampling report (`experiments/results/sampling-2026-10-29T190752.*`), Claude said "cannot tell" 4 out of 4 times. When I read its saved answer (`experiments/results/replies/baseline-dev-2026-10-29T190534/8314283.json`), I saw the posting said "two (2) years", and my prompt literally told Claude not to count spelled-out numbers. So Claude followed my prompt correctly; my prompt was the problem. Being repeatable doesn't mean being right.

**Claude cited a field that made no sense.** For R2 (posting age) it cited `years_experience`. The schema forces it to pick a résumé field, and my validator only checks that the name exists, not that it's relevant. So my "cites no fields" test can be passed by citing the wrong field. This is still open.

**My one prompt change proves less than I'd like.** I changed R4 in `prompts/revised.txt` to count "N years" and spelled-out numbers (only lines 27–28 differ, committed before running: `f8dacb2`). Dev went to 10/10 (`experiments/results/revised-dev-2026-10-29T191746.*`), but I designed the change for that exact posting, so that's expected. Held-out was 10/10 for both prompts (logged in `experiments/results/HELDOUT-LOG.md`), because it has no relevant postings at all.

**Way 1 (pasting into a chat) disagreed with my label.** I opened a new claude.ai chat, typed a short description of Cole, and pasted posting 8314283. Claude said `not_relevant`, because the posting asks for 2 years and Cole has 0, and it requires Go and Ruby, which Cole doesn't have. My message didn't include my rule that 0–3 years is OK, so Claude used its own idea of "new grad." Small slip: my first save failed because I typed `actio-surface`.

**Way 1 made me question my own rules.** Is a job that requires 2 years really relevant for someone with 0? My contract says yes, but I'm not sure anymore. It also showed how loose "at least 1 skill" is: this posting passes R6 on AWS alone, even though it requires Go and Ruby.

**Way 2 (giving Claude Code the files) quietly skipped a check.** I told Claude Code to read only the posting, the persona, and `prompts/baseline.txt`, then judge. It said `cannot_tell`, the same as the baseline prompt, because "two (2) years" doesn't count under that prompt's R4. But only 5 checks came back. R2 was missing, because I never gave it a run date, and it skipped the freshness check without saying so. Also, "read only these three files" was just my instruction; nothing actually stopped it from reading others.

**Three ways, three different answers.** The same posting got `not_relevant` from the chat, `cannot_tell` from the file read, and `cannot_tell` or `relevant` from the agent, depending on which prompt it used. Nothing about the posting changed. What changed was what each one was given: my rules, the run date, the exact prompt. The answer depends as much on the inputs as on the model.

**Things I haven't verified.** Claude Code said the model doesn't accept custom temperatures, but didn't check the docs, so I'm not claiming it. The course validator (`scripts/validate_course.py`) fails, but only because of other students' folders; nothing in mine is flagged.

**Being honest about the tests.** I didn't write any of the tests myself; Claude Code wrote all of them. My own checks were the mutation test, the id diff, the key grep, the hand labels, and reading Claude's saved answers.

## Action surface

- I only opened Claude Code inside `js1-contract-and-watch/`, so it couldn't write anywhere else.
- Claude Code saw another student's folder (prasad-s) in the git log and didn't open it.
- Claude Code asked before running `pip install`, because downloading from PyPI is a network call. I approved it.
- Claude Code never ran API calls or made commits on its own. I ran every live run and every commit myself.
- The original contract had no Claude API host on the allow-list. I added it in v0.2.
- The proxy environment variable still isn't covered by the allow-list. This is still open.
- In Way 2, "read only these three files" was only an instruction in my prompt. Nothing enforced it.
- The API key is never in the repo. It's in an env var loaded from a file outside the repo.
- Held-out runs are refused without `--final`, and every held-out run is logged with the prompt's SHA-256, so I couldn't peek at held-out by accident.

## What I accepted, changed, or rejected from Claude

**Accepted**
- Claude Code's A–P fixes from the plan review (contract v0.2).
- Stopping the agent at the first 401 (contract v0.4).

**Changed**
- The location rule. Claude Code's plan let cities with no state fail. I built a US city list from the real data instead, made placeholders like "N/A" unknown instead of fail, and excluded "CA" as a state abbreviation.
- R4 uses the largest minimum, not the smallest, so "5+ backend, 2+ Go" fails.
- The state and raw files stay tracked in git instead of being gitignored.

**Rejected**
- The `&nbsp;` "fix" to `agent/text.py`. The test showed the bug wasn't real.
- Claude Code's uppercase-only abbreviation fix. It wouldn't stop "OR".
- Switching the agent to `prompts/revised.txt`. It stays on the baseline prompt.

## Still open
- "At least 1 skill" is too loose. 8314283 passes on AWS alone even though it requires Go and Ruby.
- Whether "0–3 years" should really include postings that require 2 years, for someone with 0.
- The "won't sponsor" phrase list might miss other wordings.
- Confirm `first_published` is really the posting date.
- R3 still fails "AMER" and US cities that aren't on this board, and the code's R4 still ignores "N years".
- The proxy env variable isn't covered by the allow-list.
- The validator checks field names, not whether they're relevant.
- Decide whether to switch to the revised prompt, or change the code's R4 to match.

## Closed
- Line breaks in the posting files: skipped. I labeled from the files as they were.
- Cole Palmer persona: reviewed on Oct 29, no changes. Every field the rules use matches the contract: titles (R1), `work_country` US (R3), `years_experience` 0 (R4), `needs_sponsorship` true (R5), and a flat skills list (R6). Contact details are still fake (555 phone, @example.com). Two things I noticed but left alone: he targets "AI Engineer" but lists no AI/ML skills, and his skills include Python and SQL, which appear in almost every posting, so R6 will pass nearly anything (same as the "at least 1 skill" open item).