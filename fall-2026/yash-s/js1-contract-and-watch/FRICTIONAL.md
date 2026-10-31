
# FRICTIONAL.md: Job-Search Agent 1

## 2026-10-28: Contract v1 and First Prediction

### What I did
Today, I wrote the first version of my CONTRACT.md file for my job-search agent.

I decided to use the Databricks job board on Greenhouse. I am using a fake resume for Priya Nair instead of my real resume.

I also wrote rules to decide whether a job is relevant or not.

I committed my contract (`16ecbcd`) before starting the code.

### My Prediction
I think around 80% of Databricks job postings will have at least two skills from Priya's resume.

I think this because Priya has skills like Python, SQL, Databricks, and MLflow. These skills are related to the work Databricks does.

This is only my guess. I have not checked the actual job postings yet.

### What I am unsure about
During the review, Claude pointed out that some job postings might mention Databricks products in the general company description.

This means my agent might find two matching skills even when the job does not actually require them.

I agree with this point because my current rule checks the whole job description instead of only the job requirements.

I want to test this before changing my rule.

### What I learned
Writing the contract helped me understand what my agent should do and what it should not do.

Claude also reviewed my contract and pointed out some problems that I had not considered.

I learned that just finding matching skills does not always mean a job is relevant.

### What I will do next
I will fetch the Databricks job postings and check how many contain at least two skills from Priya's resume.

Then I will compare the results with my 80% prediction.

If the results show that my rule matches too many unrelated jobs, I will update my contract.

### Result
Not tested yet. I wrote this prediction before checking the actual job data.

## 2026-10-28: First Test Results

### What I did
After writing my first prediction, I asked Claude to fetch the Databricks job postings and check my rules.

Claude fetched the data from the Greenhouse API and tested my matching rules.

### My Prediction vs Actual Result
I predicted that around 80% of job postings would contain at least two skills from Priya's resume.

The actual result was 100%. All 897 job postings matched at least two skills.

My prediction was lower than the actual result.

### What went wrong
Claude found that every job posting included a general "About Databricks" section.

This section mentioned Databricks and Unity Catalog, which are both listed as skills in Priya's resume.

Because of this, my rule counted these skills even when they were not part of the actual job requirements.

Claude also found that removing Databricks product names reduced the matching rate to 37.7%.

### Claude's Feedback
Claude tested what happens if company product names are not counted. The result showed that only 37.7% of job postings matched.

Claude also pointed out that my title rule matched some finance and marketing jobs that were not related to Priya's target roles.

In its earlier review, Claude said that the company description contained Delta Lake and MLflow in most postings. After checking the data, Claude corrected this because those skills appeared in that section in only four postings.

### My Decision
I agree that my skill matching rule needs improvement because it is matching every job posting.

I want to remove Databricks product names from the skill matching rule so it can better identify jobs that match Priya's technical skills.

I also want to improve the title matching rule so unrelated finance and marketing jobs do not get marked as relevant.

### What I learned
I learned that a rule can look correct on paper but give unexpected results when tested with real data.

I also learned that company descriptions can affect skill matching and make the results less useful.

Testing my prediction helped me understand what needs to change before building the agent.

### What I will do next
I will update CONTRACT.md to version 2 with clearer matching rules.

I will also decide how to handle duplicate job titles and improve the checks for job requirements.

After updating the contract, I will commit the changes before building the agent.

### Evidence
Claude saved the test script and its results in `evidence/precheck-2026-10-28/`.

The results are available in `evidence/precheck-2026-10-28/output.txt`.

The test showed that all 897 job postings matched my original skill rule. After removing company product names, only 338 postings matched (37.7%).


## 2026-10-28: Contract v2 Testing and My Decisions

### What I did
I updated my CONTRACT.md to version 2 with better job matching rules.

Claude tested the new rules using the same 897 Databricks job postings.

The results showed that only 2 out of 897 jobs were relevant with my v2 rules.

Claude also tested another version where MLflow and Delta Lake were counted again. This time, 4 jobs were relevant.

Evidence: `evidence/precheck-2026-10-28/output-v2.txt`

### Decision 1: Keep MLflow and Delta Lake

I originally removed MLflow and Delta Lake because I trusted Claude's first review. After checking the actual data, Claude found that its earlier claim was incorrect.

In v2, I removed four product names from skill matching.

Claude pointed out that Databricks and Unity Catalog were common in the general company description, but MLflow and Delta Lake were not.

I decided to keep MLflow and Delta Lake because they are useful technical skills and removing them might cause my agent to miss relevant jobs.

I will exclude only Databricks and Unity Catalog.

### Decision 2: Keep the Two-Skill Rule
Claude found that only 4 out of 23 jobs with matching titles passed all the rules after my chosen change.

I decided to keep the two-skill rule for now because I want my agent to find jobs that match Priya's actual skills instead of only looking at job titles.

I know this might cause some good jobs to be missed, but I want to compare my rule-based results with Claude's judgments later.

### Decision 3: Improve Claude's Response Format
Claude pointed out that checking a normal text explanation is difficult.

I agreed to use structured fields like posting ID, matched skills, resume fields, and posting fields.

I think this will make it easier to check Claude's answers and find mistakes.


### My Prediction Before the Baseline
I expect the first baseline run to save around 897 job posting IDs and report 0 new postings.

I predict this because Claude's earlier check found 897 postings on the Databricks job board. The baseline should report 0 new postings because it is the first run.

I expect around 5 new job postings by tomorrow's second run because companies regularly add new job openings. This is just my guess, and I want to compare it with the actual result.

These are my predictions before running the watcher.

### What I Learned
I learned that making the rules too strict can cause my agent to miss some relevant jobs.

I also learned that testing different versions of the rules helps me understand which changes are useful.

Claude helped me find these problems, but I made the final decisions about which rules to keep.

### What I Will Do Next
I will commit CONTRACT.md v2 and the test evidence.

After that, Claude will build only the watcher and its tests.

I will run the baseline and then update my contract to version 3 before building the judges.


## 2026-10-28: First Baseline Run

### What I did
I committed my CONTRACT.md v2 and the test evidence in commit `172fe24`.

Claude then helped build the watcher and its tests. I ran all 19 tests, and they passed.

I committed the watcher code in commit `ac93993` before running the baseline.

After that, I ran the watcher using the live Databricks job board.

### My Prediction vs Actual Result
I predicted that the baseline would find around 897 job postings and report 0 new postings.

The actual result was 901 postings and 0 new postings.

My prediction was close, with only 4 more postings than expected.

### What I noticed
Claude's earlier check found 897 postings and 661 unique titles.

My baseline found 901 postings and 651 unique titles.

This showed me that the job board can change within a few hours.

### What Claude checked
After my baseline run, Claude checked the saved raw response, run record, and state file.

Claude confirmed that the raw file's SHA-256 matched the run record and that the state file contained all 901 posting IDs.

### What I learned
I learned why the first run is called a baseline. It saves the existing jobs so the agent can find new jobs in later runs.

I also learned that passing tests is important, but checking the actual saved files helps confirm that everything worked correctly.

### What I will do next
I will commit the baseline results and update CONTRACT.md to version 3 before building the two judges.

I will keep my original prediction of 5 new postings for the second run and compare it with the actual results.


### Date and Time Clarification

I noticed that my baseline run files show October 29, 2026, even though I ran the watcher on October 28 at 8:56 PM Boston time.

This happened because the watcher saves timestamps in UTC instead of my local time.

For example, `2026-10-29T005656Z` in the filename is the same as October 28, 2026, at 8:56 PM Eastern Time.

I decided to keep the original timestamps because they are correct. I will use Boston local dates when writing about my runs in FRICTIONAL.md.

This will help avoid confusion when checking my first and second runs.


## 2026-10-28: Judge Tests and Model Check

### What I did
Claude helped build the RECORD judge, JUDGMENT judge, and validator based on CONTRACT.md v3.

I ran 63 automated tests to check the implementation.

I also tested Claude Sonnet 5.5 from my Terminal to confirm that the model was working.

### What I tested
I first ran Claude from my course folder.

The result showed 730 input tokens.

Then I ran the same command from an empty temporary folder.

The second result showed 176 input tokens.

Both tests returned OK.

### What Claude pointed out
Claude explained that running the command from different folders can change how much extra context Claude Code includes.

The difference was 554 tokens.

Claude also pointed out that around 170 input tokens remained even when I used an empty folder.

We could not confirm exactly what those extra tokens contained.

### My Decision
I decided to run the judge from an empty temporary folder with tools disabled.

I made this decision because I want Claude to use as little extra context as possible when checking jobs.

I will also record the model used for each judgment.

### What I learned
I learned that turning off tools does not necessarily remove all additional context from Claude Code.

I also learned that checking token usage can help identify unexpected context.

The empty-folder approach reduces this problem, even though it does not completely explain every input token.

### What I will do next
I will finalize my labeling rules and update the judgment prompt before running live job judgments.

Evidence: `evidence/model-check-2026-10-28/`


## 2026-10-31: Labeling Rules and Posting Selection

### What I did

I finalized my labeling rules for Priya Nair before running any live judgments.

I decided to consider only US-based jobs with no more than 2 years of required experience. I also excluded senior-level jobs, internships, and 2027 New Grad programs.

Claude pointed out that the judgment prompt did not include job location, even though my labeling rule depends on it.

I agreed to include location in Claude's JUDGMENT. I updated CONTRACT.md and the prompt before Claude changed the code.

The RECORD rules stayed unchanged.

### What I tested

Claude updated the judge code and added three new tests for location.

I ran all 66 automated tests, and they passed.

Claude also created a script to select 25 postings from my saved Databricks baseline.

I ran the script again with random seed 7375.

The selected posting IDs and SHA-256 fingerprints matched the earlier results.

### My Decision

I decided to use 10 technical hard cases and 10 other postings for the prompt experiment, plus 5 separate postings for the sampling report.

I chose this method because a completely random selection might contain very few jobs that are suitable for Priya.

I understand that my selection does not represent the entire Databricks job board.

### Labeling the Postings

I completed the labeling for all 25 selected job postings using my labeling rules.

I marked all 25 postings as "not relevant" because they did not meet the requirements for experience, location, seniority, or job type.

I wrote a short explanation for each posting to show why I made that decision.

I noticed that even jobs related to AI or data engineering were not always suitable for Priya because they required more experience than she had.

### What I learned

I learned that a job can match Priya's technical interests but still require too much experience.

I also learned that strict labeling rules can result in a dataset with no relevant jobs.

If all 25 final labels remain "not relevant," even a model that always predicts "not relevant" could achieve 100% accuracy. This is a limitation of my experiment.

### What I will do next

I will commit my completed labeling sheet and write the pass definition for my experiment.

After that, I will run the second live watch and compare the number of new postings with my earlier prediction of 5.

Then I will run the sampling report and prompt experiment to compare Claude's judgments with my labels and see how consistent the results are.

### Evidence

- `experiment/LABELING-RULE.md`
- `experiment/select_postings.py`
- `experiment/selection.json`
- `experiment/LABELING-SHEET.md`


