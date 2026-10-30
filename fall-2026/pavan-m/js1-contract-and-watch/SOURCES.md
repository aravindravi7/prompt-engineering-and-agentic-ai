# SOURCES — Job-Search Agent 1

## What I used
- Greenhouse public Job Board API: `boards-api.greenhouse.io/v1/boards/gleanwork/jobs?content=true` (board: Glean, slug `gleanwork`)
- Python 3.14.6; httpx 0.28.1; anthropic 2.3.0; pytest 9.2.0 (full list in `requirements.txt`)
- INFO7375 JS1 assignment brief

## What I wrote
- CONTRACT.md, all three drafts (final committed as `5c579720e624de0fe41e21301a636814583f0973`, before any code)
- The relevance rule: title, skill, and location checks; the 3-skill threshold; title exclusions (intern, internship, manager, director); failing on missing location; intentional "Remote" behavior
- The fictional persona Alex Morgan (`data/persona_alex.json`)
- Choice of board (Glean) after checking Glean, Palantir, and Capital One

## What Claude contributed (claude.ai chat, October 29, 2026)
- A step-by-step breakdown of the assignment requirements
- Review of my CONTRACT.md drafts, pointing out gaps I then fixed myself: missing raw-response saving and seeded runs, missing Claude output schema and validator, HTML decode order, email/phone contradiction, two unverifiable claims, "internship" not excluded
- Pointing out that "semantic" matching is not hand-predictable
- Suggested project folder layout and `.gitignore`
- make_client(transport=None): tests can pass a fake transport, so the host check is tested without the real internet.
- HostNotAllowed: a specific error the client raises for blocked hosts. If a test only checked for any error, an unrelated bug would make it pass by accident.
