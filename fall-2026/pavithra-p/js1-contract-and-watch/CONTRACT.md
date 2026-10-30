# CONTRACT — Job-Search Agent 1

Pavithra Prasad · INFO 7375 · JS1 · 2026-10-29

## In

The agent takes a Greenhouse job board name and a fictional résumé in JSON format. It uses the résumé's skills, experience, and preferred jobs to check job openings.

## Out

For every new job, the agent shows:

* Job ID, title, company, and location.
* Whether the job is Relevant or Not Relevant.
* A short reason comparing the job requirements with the résumé's skills and experience.
* Claude's separate opinion, clearly marked as an AI judgment.

The first run saves existing jobs and shows zero new jobs. Later runs show only newly found jobs.

## Refuses

The agent will not:

1. Visit websites outside the approved Greenhouse host.
2. Show or upload anyone's real résumé.
3. Apply for jobs, send messages, or log in.
4. Treat Claude's opinion as a confirmed fact.
5. Make up jobs or missing details.

## The Rule

A job is Relevant if:

1. It is a software, backend, full-stack, cloud, or AI engineering role.
2. At least two required skills match the résumé.
3. It asks for 0–2 years of experience, is entry-level, or does not mention experience.
4. It is in the US or allows remote work from the US.

If any condition is not met, the job is Not Relevant.

## Wrong Versions

The tests should catch:

1. Wrong job: A result is matched with the wrong job ID.
2. Missing reason: The agent gives a verdict without mentioning which job requirements and résumé details support it.

## What a Failure Looks Like

2026-10-29: The agent fails if it shows old jobs as new, gives wrong results based on my rule, or gives reasons without evidence from the job posting and résumé.
