# Watch report: 20261101T020459Z-seeded-second-v2

## Summary

**SEEDED RUN** (a saved response read from disk, not a live fetch). Board `stripe`: 745 postings in the response; 8 new since the last run.
Rule verdicts are a **RECORD** (recomputable from the cited fields). Claude verdicts are a **JUDGMENT** (a model's opinion, not a fact, never overriding the rule).

## Run record

- Started: 2026-11-01T02:04:59.106Z · Source: SEEDED: saved response read from disk, no network · runs/20261101T015849Z-live-baseline/raw-response.json
- Network requests: none
- State: `state/seeded-v2-seen-ids.json` (737 ids before this run)

## New postings

| id | title | location | rule verdict (RECORD) | first failed gate | Claude verdict (JUDGMENT) |
|---|---|---|---|---|---|
| 7950828 | Head of Finance Operations | Bengaluru | not_relevant | 1 Title | not_relevant |
| 8175633 | Manager, Solutions Architecture - Enterprise (West) | San Francisco, CA  | not_relevant | 1 Title | not_relevant |
| 8283786 | Marketing Operations Program Manager | US Remote | not_relevant | 1 Title | not_relevant |
| 8195440 | Product Manager, Connect Growth & Monetization | Seattle, New-York, San Francisco | relevant | — | relevant |
| 8041655 | Product Manager, E-Invoicing | Dublin, Ireland | not_relevant | 3 Experience ceiling | not_relevant |
| 8165137 | Product Manager, Identity & Access Management | US-Remote, US-Chicago | relevant | — | relevant |
| 8223723 | Product Manager - Issuance, Bridge | San Francisco Or New York | relevant | — | relevant |
| 8234243 | Staff Product Manager, Accounting Products  | SF, SEA, NYC | not_relevant | 1 Title | not_relevant |

### 7950828: Head of Finance Operations

<https://stripe.com/jobs/search?gh_jid=7950828>

**Rule (RECORD): not_relevant**

- Gate 1 Title: FAIL ← first failure. Posting `title` = "Head of Finance Operations"; compared with CONTRACT.md `title list`.
- Gate 2 Not junior: pass. Posting `title; content` = {"title":"Head of Finance Operations","junior_term":null,"range_upper_le_2":null}; compared with CONTRACT.md `junior title terms; range upper bound <= 2`.
- Gate 3 Experience ceiling: FAIL. Posting `content` = {"phrase":"18+ years","lower_bound":18}; compared with persona-prefs.json `years_pm` (N <= years_pm + 1 = 3).
- Gate 4 Location: FAIL. Posting `location.name` = "Bengaluru"; compared with persona-prefs.json `locations`.
- Gate 5 Sponsorship: pass. Posting `content` = "no no-sponsorship phrase found"; compared with persona-prefs.json `needs_sponsorship`.
- Gate 6 Citizenship / clearance: pass. Posting `content` = "no citizenship/clearance phrase found"; compared with CONTRACT.md `citizenship/clearance phrases`.
- Domain citation (not a gate): payments (content), fintech (content), data (content)

**Claude (JUDGMENT): not_relevant** (2026-11-01T02:04:59.136Z, claude-sonnet-5-5). Gate 1 FAILED (first failure): title 'Head of Finance Operations' is not an allowed title. Gate 2 pass (no junior terms or ≤2 range). Gate 3 FAIL: '18+ years' > years_pm 2+1. Gate 4 FAIL: 'Bengaluru' matches none of San Francisco/Los Angeles/San Jose/Remote. Gate 5 pass (sponsorship needed, no blocking phrase). Gate 6 pass. Domains: payments (content), data (content), fintech (content); departments none. Cited posting: title, location.name, departments, content; persona: years_pm, locations, needs_sponsorship, domains.

### 8175633: Manager, Solutions Architecture - Enterprise (West)

<https://stripe.com/jobs/search?gh_jid=8175633>

**Rule (RECORD): not_relevant**

- Gate 1 Title: FAIL ← first failure. Posting `title` = "Manager, Solutions Architecture - Enterprise (West)"; compared with CONTRACT.md `title list`.
- Gate 2 Not junior: pass. Posting `title; content` = {"title":"Manager, Solutions Architecture - Enterprise (West)","junior_term":null,"range_upper_le_2":null}; compared with CONTRACT.md `junior title terms; range upper bound <= 2`.
- Gate 3 Experience ceiling: pass. Posting `content` = {"phrase":"3+ years","lower_bound":3}; compared with persona-prefs.json `years_pm` (N <= years_pm + 1 = 3).
- Gate 4 Location: pass. Posting `location.name` = "San Francisco, CA "; compared with persona-prefs.json `locations`; matched "San Francisco".
- Gate 5 Sponsorship: pass. Posting `content` = "no no-sponsorship phrase found"; compared with persona-prefs.json `needs_sponsorship`.
- Gate 6 Citizenship / clearance: pass. Posting `content` = "no citizenship/clearance phrase found"; compared with CONTRACT.md `citizenship/clearance phrases`.
- Domain citation (not a gate): payments (content)

**Claude (JUDGMENT): not_relevant** (2026-11-01T02:05:06.254Z, claude-sonnet-5-5). Gate 1 FAILED (first failure): title cut at the first comma is "Manager", which is not an allowed title. Gate 2 pass (no junior terms or range ≤2). Gate 3 pass (first phrase "3+ years", 3 ≤ years_pm 2 + 1). Gate 4 pass ("San Francisco" in "San Francisco, CA"). Gate 5 pass (needs sponsorship; no refusal phrase). Gate 6 pass. Domains: payments (content); the others none. Cited posting: title, location.name, content, departments; persona: years_pm, locations, needs_sponsorship, domains.

### 8283786: Marketing Operations Program Manager

<https://stripe.com/jobs/search?gh_jid=8283786>

**Rule (RECORD): not_relevant**

- Gate 1 Title: FAIL ← first failure. Posting `title` = "Marketing Operations Program Manager"; compared with CONTRACT.md `title list`.
- Gate 2 Not junior: pass. Posting `title; content` = {"title":"Marketing Operations Program Manager","junior_term":null,"range_upper_le_2":null}; compared with CONTRACT.md `junior title terms; range upper bound <= 2`.
- Gate 3 Experience ceiling: FAIL. Posting `content` = {"phrase":"6+ years","lower_bound":6}; compared with persona-prefs.json `years_pm` (N <= years_pm + 1 = 3).
- Gate 4 Location: pass. Posting `location.name` = "US Remote"; compared with persona-prefs.json `locations`; matched "Remote".
- Gate 5 Sponsorship: pass. Posting `content` = "no no-sponsorship phrase found"; compared with persona-prefs.json `needs_sponsorship`.
- Gate 6 Citizenship / clearance: pass. Posting `content` = "no citizenship/clearance phrase found"; compared with CONTRACT.md `citizenship/clearance phrases`.
- Domain citation (not a gate): payments (content), data (content)

**Claude (JUDGMENT): not_relevant** (2026-11-01T02:05:15.007Z, claude-sonnet-5-5). G1 FAIL (first failure): title 'Marketing Operations Program Manager' is not an allowed title (Program Manager without 'Technical'). G2 pass (no junior terms or range). G3 FAIL: '6+ years of experience' exceeds years_pm 2 + 1 = 3. G4 pass: 'US Remote' matches 'Remote'. G5 pass: no no-sponsorship phrases (needs_sponsorship true). G6 pass. Domains: data (content), payments (content); departments none. Cited posting: title, content, location.name, departments; persona: years_pm, locations, needs_sponsorship, domains.

### 8195440: Product Manager, Connect Growth & Monetization

<https://stripe.com/jobs/search?gh_jid=8195440>

**Rule (RECORD): relevant**

- Gate 1 Title: pass. Posting `title` = "Product Manager, Connect Growth & Monetization"; compared with CONTRACT.md `title list`.
- Gate 2 Not junior: pass. Posting `title; content` = {"title":"Product Manager, Connect Growth & Monetization","junior_term":null,"range_upper_le_2":null}; compared with CONTRACT.md `junior title terms; range upper bound <= 2`.
- Gate 3 Experience ceiling: pass. Posting `content` = "not stated"; compared with persona-prefs.json `years_pm` (N <= years_pm + 1 = 3).
- Gate 4 Location: pass. Posting `location.name` = "Seattle, New-York, San Francisco"; compared with persona-prefs.json `locations`; matched "San Francisco".
- Gate 5 Sponsorship: pass. Posting `content` = "no no-sponsorship phrase found"; compared with persona-prefs.json `needs_sponsorship`.
- Gate 6 Citizenship / clearance: pass. Posting `content` = "no citizenship/clearance phrase found"; compared with CONTRACT.md `citizenship/clearance phrases`.
- Domain citation (not a gate): payments (content)

**Claude (JUDGMENT): relevant** (2026-11-01T02:05:24.077Z, claude-sonnet-5-5). All six gates pass. G1: title 'Product Manager' matches exactly. G2: not junior, no junior title terms or range with upper bound ≤2. G3: experience not stated ("more than three years" is not an N+ or N-M digit phrase). G4: 'San Francisco' is in the location. G5: needs_sponsorship is true and no no-sponsorship phrase appears. G6: no clearance or citizenship terms. Domains: payments matched in content; fintech, data, e-commerce, mobile none; departments matched none. Cited posting: title, location.name, content, departments; persona: years_pm, locations, needs_sponsorship, domains.

### 8041655: Product Manager, E-Invoicing

<https://stripe.com/jobs/search?gh_jid=8041655>

**Rule (RECORD): not_relevant**

- Gate 1 Title: pass. Posting `title` = "Product Manager, E-Invoicing"; compared with CONTRACT.md `title list`.
- Gate 2 Not junior: pass. Posting `title; content` = {"title":"Product Manager, E-Invoicing","junior_term":null,"range_upper_le_2":null}; compared with CONTRACT.md `junior title terms; range upper bound <= 2`.
- Gate 3 Experience ceiling: FAIL ← first failure. Posting `content` = {"phrase":"5+ years","lower_bound":5}; compared with persona-prefs.json `years_pm` (N <= years_pm + 1 = 3).
- Gate 4 Location: FAIL. Posting `location.name` = "Dublin, Ireland"; compared with persona-prefs.json `locations`.
- Gate 5 Sponsorship: pass. Posting `content` = "no no-sponsorship phrase found"; compared with persona-prefs.json `needs_sponsorship`.
- Gate 6 Citizenship / clearance: pass. Posting `content` = "no citizenship/clearance phrase found"; compared with CONTRACT.md `citizenship/clearance phrases`.
- Domain citation (not a gate): payments (content), fintech (content), data (content)

**Claude (JUDGMENT): not_relevant** (2026-11-01T02:05:32.547Z, claude-sonnet-5-5). G1 pass (Product Manager). G2 pass. G3 FAIL (first failure): '5+ years of product management experience' needs 5 > years_pm 2 + 1 = 3. G4 FAIL: 'Dublin, Ireland' matches none of San Francisco/Los Angeles/San Jose/Remote. G5 pass (sponsorship needed, no refusal language). G6 pass. Domains: payments, fintech, data matched in content; departments none; e-commerce, mobile none. Cited posting: title, location.name, content, departments; persona: years_pm, locations, needs_sponsorship, domains.

### 8165137: Product Manager, Identity & Access Management

<https://stripe.com/jobs/search?gh_jid=8165137>

**Rule (RECORD): relevant**

- Gate 1 Title: pass. Posting `title` = "Product Manager, Identity & Access Management"; compared with CONTRACT.md `title list`.
- Gate 2 Not junior: pass. Posting `title; content` = {"title":"Product Manager, Identity & Access Management","junior_term":null,"range_upper_le_2":null}; compared with CONTRACT.md `junior title terms; range upper bound <= 2`.
- Gate 3 Experience ceiling: pass. Posting `content` = "not stated"; compared with persona-prefs.json `years_pm` (N <= years_pm + 1 = 3).
- Gate 4 Location: pass. Posting `location.name` = "US-Remote, US-Chicago"; compared with persona-prefs.json `locations`; matched "Remote".
- Gate 5 Sponsorship: pass. Posting `content` = "no no-sponsorship phrase found"; compared with persona-prefs.json `needs_sponsorship`.
- Gate 6 Citizenship / clearance: pass. Posting `content` = "no citizenship/clearance phrase found"; compared with CONTRACT.md `citizenship/clearance phrases`.
- Domain citation (not a gate): payments (content)

**Claude (JUDGMENT): relevant** (2026-11-01T02:05:40.128Z, claude-sonnet-5-5). G1 pass: title 'Product Manager' exact. G2 pass: no junior terms or range. G3 pass: '5+ years' is not in a sentence containing 'experience', so not stated (years_pm 2). G4 pass: 'Remote' in 'US-Remote, US-Chicago'. G5 pass: needs_sponsorship true, no refusal phrases. G6 pass: no clearance/citizenship terms. No gate failed. Domains: payments (content); departments and other terms none. Cited posting: title, location.name, content, departments; persona: years_pm, locations, needs_sponsorship, domains.

### 8223723: Product Manager - Issuance, Bridge

<https://stripe.com/jobs/search?gh_jid=8223723>

**Rule (RECORD): relevant**

- Gate 1 Title: pass. Posting `title` = "Product Manager - Issuance, Bridge"; compared with CONTRACT.md `title list`.
- Gate 2 Not junior: pass. Posting `title; content` = {"title":"Product Manager - Issuance, Bridge","junior_term":null,"range_upper_le_2":null}; compared with CONTRACT.md `junior title terms; range upper bound <= 2`.
- Gate 3 Experience ceiling: pass. Posting `content` = "not stated"; compared with persona-prefs.json `years_pm` (N <= years_pm + 1 = 3).
- Gate 4 Location: pass. Posting `location.name` = "San Francisco Or New York"; compared with persona-prefs.json `locations`; matched "San Francisco".
- Gate 5 Sponsorship: pass. Posting `content` = "no no-sponsorship phrase found"; compared with persona-prefs.json `needs_sponsorship`.
- Gate 6 Citizenship / clearance: pass. Posting `content` = "no citizenship/clearance phrase found"; compared with CONTRACT.md `citizenship/clearance phrases`.
- Domain citation (not a gate): payments (content), fintech (content), data (content)

**Claude (JUDGMENT): relevant** (2026-11-01T02:05:51.777Z, claude-sonnet-5-5). All six gates pass. G1: 'Product Manager' matches. G2: no junior terms or ranges. G3: experience not stated (the '5+ years' sentence lacks 'experience'). G4: 'San Francisco' is in 'San Francisco Or New York'. G5: sponsorship needed, no refusal phrases. G6: no clearance or citizenship terms. Domains: payments (content), fintech (content), data (content), e-commerce none, mobile none. Cited posting: title, location.name, departments, content; persona: years_pm, locations, needs_sponsorship, domains.

### 8234243: Staff Product Manager, Accounting Products 

<https://stripe.com/jobs/search?gh_jid=8234243>

**Rule (RECORD): not_relevant**

- Gate 1 Title: FAIL ← first failure. Posting `title` = "Staff Product Manager, Accounting Products "; compared with CONTRACT.md `title list`.
- Gate 2 Not junior: pass. Posting `title; content` = {"title":"Staff Product Manager, Accounting Products ","junior_term":null,"range_upper_le_2":null}; compared with CONTRACT.md `junior title terms; range upper bound <= 2`.
- Gate 3 Experience ceiling: FAIL. Posting `content` = {"phrase":"10+ years","lower_bound":10}; compared with persona-prefs.json `years_pm` (N <= years_pm + 1 = 3).
- Gate 4 Location: FAIL. Posting `location.name` = "SF, SEA, NYC"; compared with persona-prefs.json `locations`.
- Gate 5 Sponsorship: pass. Posting `content` = "no no-sponsorship phrase found"; compared with persona-prefs.json `needs_sponsorship`.
- Gate 6 Citizenship / clearance: pass. Posting `content` = "no citizenship/clearance phrase found"; compared with CONTRACT.md `citizenship/clearance phrases`.
- Domain citation (not a gate): payments (content), data (content)

**Claude (JUDGMENT): not_relevant** (2026-11-01T02:06:00.830Z, claude-sonnet-5-5). Gate 1 FAILED first: title 'Staff Product Manager' is not an allowed title. Gate 2 passes (no junior terms, no range ≤2). Gate 3 FAILS: '10+ years' > years_pm+1=3. Gate 4 FAILS: 'SF, SEA, NYC' contains none of San Francisco/Los Angeles/San Jose/Remote. Gates 5 and 6 pass (sponsorship needed, no blocking phrases; no clearance/citizenship text). Domains: payments (content), data (content), others none. Cited posting: title, location.name, departments, content; persona: years_pm, locations, needs_sponsorship, domains.
