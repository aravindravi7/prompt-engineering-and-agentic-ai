# Labeling rule L-v1 — written before any posting was labelled

Written 2026-10-21, before the 20 postings were drawn and before any of them
were looked at. Committed before the label files exist, so the order is
checkable in the git history of this folder.

## Why this is not the same thing as R-v1

R-v1 (CONTRACT.md §4) is the agent's rule: four mechanical gates over four
listing fields. L-v1 is **my** label — what I, the person whose time is being
spent, would say about a posting after reading the same four fields. They are
deliberately different documents, because conflating them makes a whole class
of error invisible:

- if the model disagrees with my hand label, that can be the model failing to
  apply R-v1, **or** R-v1 failing to express L-v1;
- only keeping the two apart lets me say which.

So every row in the experiment records three things: my hand label (L-v1), the
rule verdict (R-v1, recomputable), and the model's verdict (a judgment).

## L-v1, applied by hand to the four listing fields

Answer three questions. Label `yes` only if all three are yes. "Unsure" is not
an available answer: I must commit to a label, and if it was close I write a
note in the `note` column of the label file saying so, before seeing any model
output.

**L1 — Is this an individual-contributor software or ML engineering role?**
Yes for roles whose work is writing and shipping software or models. No for
people-management, sales, marketing, recruiting, finance, legal, support,
content, and for engineering-adjacent roles whose work is not building
software (programme management, technical writing).

**L2 — Could a December 2026 new graduate with no industry experience
plausibly be hired into it?**
No if the title claims seniority (senior, staff, principal, lead, director,
architect, manager, head). No if it is an internship or a co-op, because the
persona wants full-time work starting after graduation. Yes otherwise,
including titles with no level marker at all.

**L3 — Could the persona actually work in it?**
Yes for a location in the United States, and for remote roles whose location
string scopes them to the United States. No for a non-US office, and no for a
remote role scoped to a country the persona is not in.

## Differences from R-v1 that I expect before running anything

Named here so that neither can later be presented as a discovery:

1. **"Site Reliability Engineer", "Security Engineer", "Data Engineer"** — L1
   says yes, R-v1 fails them at G2 because the phrase is not on the closed
   `target_title_phrases` list. I expect R-v1 false negatives here.
2. **"Remote - Netherlands"** — L3 says no, R-v1 says relevant (CONTRACT.md
   §4.2 item 3). I expect an R-v1 false positive here if such a posting is
   drawn.
3. **A department of "Sales Engineering"** — L1 says no, R-v1 passes G3 on the
   substring (CONTRACT.md §6). I expect an R-v1 false positive here too.
4. **A posting with an empty `departments` array** — R-v1 fails it at G3 on a
   missing field; L-v1 ignores departments entirely and would judge it on
   title and location. I expect disagreement.

## What L-v1 cannot do

It reads four fields. It cannot tell whether the work is interesting, whether
the team is any good, whether the "new grad" role is really open to new grads,
whether the salary is liveable, or whether the posting is still real. Nothing
in this assignment measures those, and no number below should be read as if it
did.
