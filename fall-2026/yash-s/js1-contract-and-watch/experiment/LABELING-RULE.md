# Labeling rule: Job-Search Agent 1

Written by Yash before any posting was labeled. Claude saved the text word for word from Yash's messages and added the headings. The two choices under "Choices I accepted from Claude" were Claude's suggestions; Yash agreed to them.

## The rule

I am checking jobs for Priya Nair, a fictional candidate who is looking for AI Engineer, Machine Learning Engineer, or Data Engineer roles.

I will mark a job as relevant if its main work is related to AI, machine learning, or data engineering, and Priya has skills, experience, or projects that match the work.

I will also consider whether the job's required experience and seniority are suitable for Priya.

I will mark a job as not relevant if it is mainly about marketing, finance, sales, or another unrelated field.

A matching job title alone is not enough. I will check the actual responsibilities and requirements.

If a job requires much more experience than Priya has, I will mark it as not relevant.

I will use this rule when checking jobs by hand and when comparing Claude's judgments with my own labels.

## Decisions that make the rule checkable

1. **Experience cutoff:** I will mark jobs as not relevant if they require more than 2 years of professional experience. I will also mark Senior, Staff, Principal, Lead, Manager, and Director positions as not relevant because Priya is an early-career candidate.

2. **Location:** I will only consider jobs located in the United States, including remote US-based positions. Jobs in other countries will be marked not relevant because Priya is currently looking for work in the US.

3. **Customer-facing technical roles:** I will decide Solutions Architect and Forward Deployed Engineer roles case by case. I will mark them relevant only if the work is mainly technical, matches Priya's AI/ML or data engineering skills, and meets my experience and location rules.

4. **Unsure cases:** If I cannot clearly determine whether a job is suitable based on the available information, I will mark it not relevant and write a short explanation of what information is missing.

5. **Selecting 20 postings:** I will select 10 postings with AI, ML, machine learning, or data-related words in the title and 10 postings without those words. I will use a script with a fixed random seed to make the selection reproducible and avoid repeated job titles. I will use the same selection method to choose 5 separate postings for the sampling report, without overlapping with the 20 used for the prompt experiment.


6. **Senior titles:** I will treat "Sr." and "Sr" the same as "Senior". These jobs will be marked not relevant because Priya is an early-career candidate.

7. **Internships and New Grad roles:** I will mark internships and New Grad (2027 Start) programs as not relevant. Priya graduated in December 2025, so these programs may not match her graduation date. I want to focus on full-time early-career positions.

8. **Title keywords:** For selecting the 10 technical postings, I will use AI, ML, GenAI, machine learning, and data. Matching will ignore capital letters and use whole words or phrases. I will also require a US location and no seniority words in the title.

## Choices I accepted from Claude

- **Claude is shown the location.** Because decision 2 depends on location, Claude's JUDGMENT is also shown the posting's `location` and may cite it as a posting field.
- **The topic half is the hard cases.** The 10 postings with AI or data words in the title are the ones that also have a US location and no seniority word in the title. The other 10 are picked at random, with a fixed seed, from titles without those words. These 20 are not a random sample of the board, so pass rates describe hard cases, not Databricks overall.
