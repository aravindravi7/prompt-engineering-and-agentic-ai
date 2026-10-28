
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
