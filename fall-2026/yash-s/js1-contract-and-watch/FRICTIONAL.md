
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
