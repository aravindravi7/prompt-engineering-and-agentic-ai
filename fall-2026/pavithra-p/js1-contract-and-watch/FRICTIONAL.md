# Frictional — Job-Search Agent 1

Pavithra Prasad · INFO 7375 · JS1 The Contract and the Watch

Commits in the course repo (`fall-2026/pavithra-p/js1-contract-and-watch/`), oldest first: `586c296` my contract draft · `9aed486` reviewed contract · `c175a59` watcher · `d6a3a4b` run 1 · `695ed9f` rule and wrong versions · `5b130b8` first freeze · `c16b311` re-freeze · `7327ccd` my labels · `7bfeae4` Claude judge · `71cdf3b` sampling replies · `d500451` persona · `aa3e1ab` sampling report · `287eefe` baseline dev · `30e32c3` prompt experiment · `15e9d2a` run 2 · `5a9bd79` action surfaces · final commit: the hash given in the Canvas submission

My key prompts to Claude Code, quoted short: "first tell me what all should be done in simple give step by step" · "why [so] much details in the table … do what is asked" · "why are u showing only senior roles?" · "I would consider all the SE roles" · "is it mandatory to keep the persona name as aarav" · "1" (the prompt change)

## 2026-10-29 — The contract first

- Wrote my contract draft: In, Out, Refuses, the relevance rule and the failure sentence.
- Claude Code sharpened it: exact title words, whole-word skill matching, the refuses list, and the two wrong versions. The first version came to about 1,050 words with a test table. I asked for only what the assignment asks, so it was cut to the six sections (562 words).
- **Friction:** Pinterest's location field says "CA" for both California and Canada. The rule only accepts "United States", "USA" or "US", and a test checks Toronto, CA.
- Both versions were committed before any code: `586c296` (mine, as written) and `9aed486`.

## 2026-10-29 — The board

- **Tried:** GitLab's board first. **What happened:** my rule marked 1 of its 236 jobs Relevant, too few to test anything. Switched to Pinterest (25 US engineering roles, about 4 new a day).
- A ChatGPT review suggested a board with more entry-level roles. Pinterest stayed the watched board; Figma and Twilio were used only for the experiment snapshots.

## 2026-10-30 — Run 1 and the 20 postings

- Ran the baseline in my own terminal: 165 jobs, 0 new (`d6a3a4b`). The VS Code Terminal menu was greyed out, so I used the Claude app's terminal tab.
- The first freeze of 20 postings (`5b130b8`) was mostly senior roles. I asked why, and it was re-frozen as 20 non-senior US engineering roles from Pinterest, Figma and Twilio (`c16b311`), still before any label or Claude answer.

## 2026-10-30 — My labels

- Labelled all 20 before any Claude run (`7327ccd`): 11 Relevant, 9 Not Relevant.
- **Hard decision:** I labelled by the title. Only plain Software Engineer roles count; senior and ML roles are not Rohan's background. I did not check years in the descriptions. Claude Code pointed out that this differs from my written rule. I kept my labels and recorded the change in `experiment/README.md`.

## 2026-10-30 — Sampling

- 5 dev postings × 4 fresh `claude -p` conversations: 20/20 valid, and the same verdict 4/4 on every posting (`71cdf3b`).
- **Unexpected:** Claude disagreed with my labels on 3 of 5. Its reasons quoted the years: 8009057 asks for "4+ years" (line 35), and 7661919 asks for "Minimum 2-3+ years".
- I thought Claude would mostly agree with my answers. I was surprised when three were different, but I realized I had not checked the job descriptions properly.

## 2026-10-30 — Persona name

- I asked whether the name Aarav Patel was required. It was not, and no classmate's folder used it, so I changed it to Rohan Mehta (`d500451`). Only the name and contact details changed. Claude's prompt never contains the name, and all 20 saved sampling prompts hash the same after the change.

## 2026-10-31 — Prompt experiment

- Baseline on dev: 3/10 against my labels, below answering "Not Relevant" every time (5/10).
- **Tried:** one change, line 6 of the prompt: "the description does not ask for 3 or more years" became "Do not use any years of experience the description asks for." **Predicted (Claude Code, before the run):** about 7/10. **What happened:** 7/10 on dev, then held-out last: 4/10 → 8/10.
- The score went up because the prompt now copies how I labelled, not because it judges better. The watcher still uses the baseline prompt.
- The scores improved, but I am not sure the answers actually got better. The new prompt matched my labels more closely, but I may have made mistakes when labeling the jobs.

## 2026-10-31 — Run 2 and the action surfaces

- Ran the watch in my own terminal: 8 new Pinterest jobs (`15e9d2a`). I ran it twice by accident; the second run, 14 seconds later, found 0 new, which shows nothing is reported twice.
- **Unexpected:** 2 of Claude's 8 replies left `resume_fields` empty. The validator rejected them, and they were saved, not repaired.
- Pasted job 7832348 into claude.ai myself (Opus 5.5, high). Chat, file and agent all said Not Relevant ("Staff", 6+ years) (`5a9bd79`).

## What is unresolved

- Some jobs were still marked incorrectly, and a few answers had format errors. Next time, I would check the job descriptions more carefully and test with more jobs.

## Human and AI contributions

- **I did:** wrote the contract draft, chose the board, rejected the senior-only freeze, labelled all 20 postings, wrote the sampling conclusion, chose the persona name and the one prompt change, ran run 1 and run 2, and did the claude.ai chat.
- **Claude Code contributed:** sharpened the contract, wrote the code and the 43 tests, ran the snapshots, freeze, sampling and experiment, checked some of Claude's quotes against the saved postings, and drafted the reports and the factual entries here. My reflection lines are my own words.
- **Accepted:** the sharpened rule words, the "CA" trap, Pinterest, the split of work between the code and Claude (Claude gets no tools).
- **Changed:** the long contract (cut to six sections), the first freeze (re-frozen), the persona name.
- **Rejected:** changing my labels to match my written rule; switching the watched board away from Pinterest.
