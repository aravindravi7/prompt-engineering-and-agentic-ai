# Sources

## Summary

What this submission used, what I (Aravind) wrote or decided, and what Claude contributed.

## Used

- Greenhouse Job Board API, public endpoint `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` (no key, no login), fetched by the agent on 2026-10-31.
- Fictional persona Maya Sehgal: `search/examples/maya-sehgal/resume.example.json` from The Reallocation Engine (commit `d08afdd`), copied byte for byte (`persona/SOURCE.md`).
- Claude Code CLI 2.1.310, model `claude-sonnet-5-5`, for the judge, sampling and experiment calls; and Claude Code (desktop app) as the build assistant in one session on 2026-10-31.
- Course Chapters 1–3 (assignment brief).

## Written or decided by me

[Aravind to confirm/edit] The contract's decisions (CONTRACT.md: inputs, refusals, the six gates and their thresholds, wrong versions, the failure sentence, the Gate 2 revision); the persona preferences (years_pm, locations, needs_sponsorship, domains); the board choice; the labeling rule and all 20 hand labels; the seeded-run design (which ids to remove, the seed, excluding labeling postings); the one change for prompt v2 and the quote-fidelity rule; the decision to keep held-out locked; the autonomy choice, sign-off and driver's seat; FRICTIONAL.md.

## Contributed by Claude (Claude Code build session, 2026-10-31)

- CONTRACT.md wording, drafted from my decisions and edited by me (as the contract's first line says).
- All code in `src/` and `tools/`, and the tests in `test/` (including the constructed fixture and the mutant versions of each wrong version), written against my contract. I ran the tests myself: [Aravind to confirm].
- Prompt v1 text (`prompts/judge.v1.md`), and the v2 text implementing the change I specified.
- Drafts of README.md (toolchain, commands, what ran, layout), this file's factual sections, and the factual columns of ACTION-SURFACE.md.
- One scouting call per board to eight Greenhouse boards on 2026-10-31 to count PM titles before I chose Stripe (not evidence, not saved).
