# My labeling rule

Written on 2026-10-31, before any of the 20 postings were read. Drafted by Claude Code at my request (see `SOURCES.md`). The labels in `labels.csv` are mine.

The question for each posting: *is this job a real fit for Aarav Patel, the fictional candidate?*

**I label a posting `MATCH` when all three hold:**

1. The core of the job is software engineering of the kind in his résumé: backend services, infrastructure or platform, DevOps or site reliability, or data engineering. His résumé shows TypeScript, Java and Python services; Kafka and Redis; Kubernetes, Docker and Helm; and AWS.
2. He meets the must-have qualifications: what the posting lists under "You may be a good fit if you" or as requirements. That includes any minimum years of experience being 3 or fewer. He has about 2.4 years.
3. He could work in the location: it includes the United States.

**I label a posting `NOT_MATCH` when any of these is true:**

- The job is not engineering: sales, legal, finance, operations, recruiting, policy, communications.
- The job is senior, staff, lead or a manager role, or asks for more than 3 years as a must-have.
- A must-have is a specialism his résumé does not show. Examples: kernel or systems programming, ML research or model training, hardware or electrical engineering, security research.
- It is only outside the United States.

**When I am unsure, I decide by:** looking only at the must-haves. Nice-to-haves ("Strong candidates may also…") never count against him. A skill he lists under `familiar_with_not_shipped` (Rust, Terraform) does not meet a must-have.

**How this differs from the contract's rule:** this is a judgment about the work and the must-haves, not a keyword count. A posting can pass all five contract rules and still be `NOT_MATCH`, for example if it needs kernel programming. It can also fail the contract's title list and still be `MATCH`, if the work is backend engineering under another title. Unlike Rule 4, years listed under nice-to-haves do not count.
