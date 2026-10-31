# Hand-label worksheet — L-v1, 25 real postings (filled)

Labels by Weiting W. `decided = author_first` means she decided the row on
2026-10-26 with no derived label in front of her. `decided =
derived_then_confirmed` means Claude derived it mechanically from L-v1's
wording and she checked and confirmed it row by row on 2026-10-30, changing
none. **Neither set is a blind label** — see the `provenance` block in
`labels-L-v1.json` and the "where these labels are weak" sections of both
reports.

L-v1, as three questions. Label `yes` only if all three are yes.

- **L1** individual-contributor software or ML engineering role?
- **L2** could a Dec-2026 new grad with no industry experience plausibly be hired into it?
- **L3** could the persona actually work in it (US location, or remote scoped to the US)?

| # | set | id | title | Job Family | location | L-v1 | decided | note |
|---|---|---|---|---|---|---|---|---|
| 1 | sampling | 8299781 | Machine Learning Engineer, Answers Relevance | None | Remote - United States | **yes** | author_first | L-v1 does not read Job Family; an ML engineer role, Remote US. Labelled after Claude had already said the agent fails it at G3 - not a blind label. |
| 2 | sampling | 6469397 | Software Engineer, Ads | Software Engineering | Remote - United States | **yes** | derived_then_confirmed |  |
| 3 | sampling | 6512458 | Software Engineer, Ads | Software Engineering | Remote - Ontario, Canada | **no** | author_first | Remote - Ontario, Canada, so L3 says no. Labelled after Claude had already said both the rule and the model call it relevant - not a blind label. |
| 4 | sampling | 8153017 | Account Executive, Mid-Market (DACH) | Account Executive | Amsterdam, Netherlands | **no** | derived_then_confirmed |  |
| 5 | sampling | 6909091 | Senior Software Engineer, Ads | Software Engineering | Remote - United States | **no** | derived_then_confirmed |  |
| 6 | development | 6909093 | Senior Software Engineer, Ads | Software Engineering | Remote - Ontario, Canada | **no** | derived_then_confirmed |  |
| 7 | development | 6960833 | Senior Machine Learning Engineer | Machine Learning | Remote - Ontario, Canada | **no** | derived_then_confirmed |  |
| 8 | development | 7131932 | Machine Learning Engineer | Machine Learning | Remote - United States | **yes** | derived_then_confirmed |  |
| 9 | development | 7445240 | Staff Data Scientist, Marketing | Data Science | Remote - United States | **no** | derived_then_confirmed |  |
| 10 | development | 7701558 | Staff Product Designer, Growth | Specialized UX Design | Remote - United States | **no** | derived_then_confirmed |  |
| 11 | development | 8139781 | Software Engineer, Content Platform | Software Engineering | Remote - United States | **yes** | derived_then_confirmed |  |
| 12 | development | 8172457 | Software Engineer, Consumer Engineering | Software Engineering | Remote - United States | **yes** | derived_then_confirmed |  |
| 13 | development | 8191664 | Creative Strategist (M&E/Retail) | Creative Strategy | Los Angeles, CA | **no** | derived_then_confirmed |  |
| 14 | development | 8198102 | Front End Software Engineer, Media Player | Software Engineering | Remote - United States | **yes** | derived_then_confirmed |  |
| 15 | development | 8234154 | International Payroll Analyst | Payroll | Remote - United Kingdom | **no** | derived_then_confirmed |  |
| 16 | heldout | 6960831 | Senior Machine Learning Engineer | Machine Learning | Remote - United States | **no** | derived_then_confirmed |  |
| 17 | heldout | 7131934 | Machine Learning Engineer | Machine Learning | Remote - Ontario, Canada | **no** | author_first | Remote - Ontario, Canada, same as row 3. Labelled after Claude had already said the rule calls it relevant - not a blind label. |
| 18 | heldout | 7330347 | Principal Data Scientist, Ads | Data Science | Remote - United States | **no** | derived_then_confirmed |  |
| 19 | heldout | 7511679 | Senior Software Engineer, Storage | Software Engineering | Remote - United States | **no** | derived_then_confirmed |  |
| 20 | heldout | 7721787 | Staff Data Scientist, Ads | Data Science | Remote - United States | **no** | derived_then_confirmed |  |
| 21 | heldout | 8147559 | Front End Software Engineer, Consumer Engineering | Software Engineering | Remote - United States | **yes** | derived_then_confirmed |  |
| 22 | heldout | 8192369 | International Payroll Analyst | Payroll | Remote - United States | **no** | derived_then_confirmed |  |
| 23 | heldout | 8194576 | Frontend Engineer, Ads | Software Engineering | Remote - United States | **yes** | derived_then_confirmed |  |
| 24 | heldout | 8214910 | Software Engineer, Ingestion Platform | Software Engineering | Remote - United States | **yes** | derived_then_confirmed |  |
| 25 | heldout | 8282760 | Analytics Engineer | Data Science | Remote - United States | **yes** | author_first | Analytics Engineer counts as an IC engineering role under L1. Labelled after Claude had already said the agent fails it at G2 - not a blind label. |

Totals: 10 yes, 15 no.

