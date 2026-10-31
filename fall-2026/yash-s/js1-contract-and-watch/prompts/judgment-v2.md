
# Job Relevance Judgment Prompt v2

You are checking whether a job posting is relevant for Priya Nair, a fictional candidate.

Priya is looking for AI Engineer, Machine Learning Engineer, and Data Engineer roles.

Read the provided job posting and Priya's resume.

Mark a job as "relevant" if:
- The main work is related to AI, machine learning, or data engineering.
- Priya has skills, experience, or projects that match the job.
- The job's requirements and seniority are suitable for Priya.
- The job is located in the United States, including US-based remote jobs.

Mark a job as "not relevant" if:
- The job is mainly about unrelated work like marketing, finance, or sales.
- Priya does not have enough matching qualifications.
- The job requires more than 2 years of professional experience.
- The job title contains Senior, Sr., Staff, Principal, Lead, Manager, or Director.
- The job is located outside the United States.
- The job is an internship or a New Grad (2027 Start) program.

## Additional Job Relevance Rules

1. **Experience:** Priya is an early-career candidate. Jobs requiring more than 2 years of professional experience are not relevant. Treat "Sr." and "Sr" the same as "Senior".

2. **Location:** Only consider jobs located in the United States, including US-based remote positions.

3. **Customer-facing technical roles:** Solutions Architect and Forward Deployed Engineer roles can be relevant if the main work is technical, matches Priya's AI/ML or data engineering skills, and meets the experience and location rules.

4. **Internships and New Grad programs:** Mark internships and New Grad (2027 Start) programs as not relevant. Priya graduated in December 2025, and the focus is on full-time early-career positions.

5. **Unsure cases:** If there is not enough information to decide whether the job is suitable, mark it as "not relevant". Explain what information is missing.

Do not decide based only on the job title. Check the job responsibilities, requirements, location, and Priya's resume.

Use only the information provided. Do not make up skills, experience, or job requirements.

## Response Format

Return valid JSON with exactly these six fields:

- posting_id
- verdict
- resume_fields
- posting_fields
- matched_terms
- reason

Rules for the response:

1. Copy `posting_id` exactly from the provided job posting.

2. `verdict` must be "relevant" or "not relevant".

3. `resume_fields` must contain only these field paths:
   - `skills.languages`
   - `skills.data_bi`
   - `skills.backend_automation`
   - `skills.database_cloud`
   - `experience`
   - `projects`

4. `posting_fields` must contain only:
   - `title`
   - `content`
   - `location`

5. `matched_terms` must be a list of strings. Every term must appear in at least one named resume field and one named posting field. Use whole-word or whole-phrase matching and ignore capital letters.

6. `reason` must be a short, clear explanation based on the provided information.

7. If the verdict is "relevant", include at least one supported matched term.

8. If the verdict is "not relevant", `matched_terms` can be empty.

Return only the JSON object.

Do not include Markdown code fences, extra text, or additional fields.

End your response immediately after the closing brace `}` of the JSON object. Do not add corrections, comments, or explanations after the JSON.
