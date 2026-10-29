# Job Relevance Judgment Prompt v1

You are checking whether a job posting is relevant for Priya Nair, a fictional candidate.

Priya is looking for AI Engineer, Machine Learning Engineer, and Data Engineer roles.

Read the provided job posting and Priya's resume.

Mark a job as "relevant" if:
- The main work is related to AI, machine learning, or data engineering.
- Priya has skills, experience, or projects that match the job.
- The job's requirements and seniority are suitable for Priya.

Mark a job as "not relevant" if:
- The job is mainly about unrelated work like marketing, finance, or sales.
- Priya does not have enough matching qualifications.
- The job requires much more experience than Priya has.

Do not decide based only on the job title.

Use only the information provided. Do not make up skills, experience, or job requirements.

Return valid JSON with exactly these six fields:

- posting_id
- verdict
- resume_fields
- posting_fields
- matched_terms
- reason

Rules for the response:

1. Copy posting_id exactly from the provided job posting.

2. verdict must be "relevant" or "not relevant".

3. resume_fields must contain only these field paths:
   - skills.languages
   - skills.data_bi
   - skills.backend_automation
   - skills.database_cloud
   - experience
   - projects

4. posting_fields must contain only:
   - title
   - content

5. matched_terms must be a list of strings. Every term must appear in at least one named resume field and one named posting field. Use whole-word or whole-phrase matching and ignore capital letters.

6. reason must be a short, clear explanation based on the provided information.

7. If the verdict is "relevant", include at least one supported matched term.

8. If the verdict is "not relevant", matched_terms can be empty.

Return only the JSON object.

Do not include Markdown code fences, extra text, or additional fields.
