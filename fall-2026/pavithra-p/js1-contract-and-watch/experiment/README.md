# Prompt experiment: postings, split and hand labels

## The 20 postings (frozen 2026-10-30T12:21:15Z)

`python3 -m agent freeze evidence/raw/pinterest-20261030T121808Z.json` picked them from the baseline run's raw response, by the selection written in `agent/freeze.py` before it ran. It computes no verdicts.

* The candidates are jobs whose title has "Engineer" plus a role word (rule 1) and whose location has United States, USA or US (rule 4). That day there were 25.
* Group A is titles with no experience word (rule 3); group B is the rest, each sorted by job ID. All of A (6 jobs) is taken, then B, until there are 20.
* Walking that list in order, the postings alternate dev, held-out. That gives 10 dev and 10 held-out, with 3 of group A in each half.

`postings.json` lists the 20 with their split and a fingerprint of each description. `postings/<id>.txt` holds each description as plain text, for labelling.

## Hand labels

The labelling rule is the rule in `CONTRACT.md`, written on 2026-10-29. I label all 20 by hand in `labels.csv` before Claude sees any of them, and the held-out labels are not used to change any prompt.

For each posting I open `postings/<id>.txt` and check:

1. **Role:** does the title have "Engineer" and one of Software, Backend, Back-end, Full-stack, Full Stack, Fullstack, Cloud, AI?
2. **Skills:** which of these appear in the description as whole words? TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit, Jenkins. Two or more is a Y.
3. **Experience:** does the title have none of Senior, Sr, Staff, Principal, Lead, Manager, Director, Head, Distinguished, Intern, and does the description ask for no 3+ years?
4. **Location:** does the location have United States, USA or US?

The label is Relevant only if all four are Y.
