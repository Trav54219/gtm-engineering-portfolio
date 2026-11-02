# Clay table: researching the companies I'm applying to

15 companies hiring GTM engineers, run through Clay's functions with the Clay CLI, then graded against
an answer key I built by hand the same day (domains, hiring managers and BounceBan-verified emails).
Write-up: [breezygrowthco.com/travis/clay-company-research](https://www.breezygrowthco.com/travis/clay-company-research).

## The table

Columns marked **ran** were run on all 15 rows through `clay routines runs start`. Columns marked
**designed** are the fixes the results call for; they are not run yet.

| # | Column | Type | Input | Credits per row | Status |
|---|---|---|---|---|---|
| 1 | Company Name | input | job board | 0 | ran |
| 2 | Domain | Clay function: Company Domain | Company Name | 1 | ran |
| 3 | Domain check | formula: keep the domain only if it matches the job post's apply link or the company's LinkedIn website, else flag | Domain, post URL | 0 | designed |
| 4 | Employee Count | Clay function: Company Employee Count | Domain, Name | 1 | ran |
| 5 | Open Jobs | Clay function: Company Job Openings | Domain | 1 | ran |
| 6 | Website Tech Stack | Clay function: Website Technology Stack | Domain | 2 | ran |
| 7 | People | Clay function: Find People at Company | Domain | 1 | ran |
| 8 | Hiring manager pick | formula: title ladder by company size (founder under 50 people, head of growth / GTM / RevOps from 51 to 500, director over 500) | People, Employee Count | 0 | designed |
| 9 | Work Email | Clay function: Work Email | manager name, Domain, Name | 3 | ran (on the hand-picked manager) |
| 10 | Email verified | BounceBan, outside Clay | Work Email | n/a | ran outside Clay |

Spend: 144 of the workspace's 200 free credits, including 9 credits of one-row cost tests.

## Results (`python grade.py <run dir>`)

```
Domain from company name: 11/15 right
  Siro: got siroclinpharm.com, right is siro.ai
  Hearth: got hearthdisplay.com, right is gethearth.com
  Basis: got basis.com, right is getbasis.ai
  Strella: got strellabiotech.com, right is strella.io
Work email: 14/15 identical to the hand-verified address, 1 more on another verified mail domain
People finder (no title filter): hand-picked manager in the returned list at 4/15
Homepage tech: HubSpot 11, Salesforce 9, both 6, neither 1
```

## Files

- `run.py` starts one Clay function routine for up to 100 rows, polls until it finishes and records the
  credit balance before and after.
- `grade.py` grades the outputs against the answer key and prints totals only.

The answer key and raw outputs hold real people's names and work emails, so they are not in this repo.
