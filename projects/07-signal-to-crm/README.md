# 07: Signal to CRM, on a schedule

A company posts an SDR or BDR job. The next morning it's in HubSpot with a fit score, the reason for the score, a route, the title to contact and a drafted first line. Nobody touches it.

## First run (2026-10-31)

- **20 jobs paid for (20 TheirStack credits), 18 companies**, all created in HubSpot. Two companies had two SDR posts at once.
- **Routes:** 5 AE Mid-market, 7 SDR, 6 Nurture.
- **The 6 Nurture accounts:** 5 are software or IT services companies, which the demo seller doesn't sell to, so they score 0. The sixth scored too low to route.
- **Contacts:** TheirStack named a hiring manager on 1 of the 20 jobs, so 1 contact was attached. Every other account gets a recommended title instead.

The full run is in [`runs/`](runs): company, domain, headcount, job title, post date, score, route and reason for each account. It's all public job-post data. No people are published.

| Score | Route | Company | Employees | Job |
|---|---|---|---|---|
| 75 | SDR | Westcor Global | 49 | Title Insurance Business Development Rep |
| 65 | AE Mid-market | CarsDirect.com | 100 | Business Development Representative |
| 60 | SDR | Comfort Wave | 14 | Business Development Representative |
| 0 | Nurture | SewerAI | 115 | Sales Development Representative (software: excluded) |

## How it works

1. **Pull.** TheirStack jobs API: SDR/BDR titles, US, posted in the last 2 days, 10 to 200 employees, direct employers with a domain. Every job id already seen goes back as `job_id_not`, so no job is paid for twice.
2. **Group by company.** Several SDR posts at once is a signal of its own.
3. **Score the account (0 to 100).** The reason field shows the arithmetic, for example "49 employees +30, 22 jobs posted in 30 days +25, no outbound tools seen +20".

   | Signal | Points |
   |---|---|
   | 20 to 100 employees | +30 (any other size +15) |
   | Jobs posted in the last 30 days | +25 for 10 or more, +15 for 3 to 9, +5 otherwise |
   | Several SDR/BDR posts at once | +15 |
   | No outbound tools in the stack | +20 |
   | Already pays for Outreach, Apollo, Smartlead and the like | +10 instead |
   | Funded in the last year | +10 |
   | Software or IT services company | -60 (excluded) |

4. **Route.** A score under 40 goes to Nurture. Otherwise 50+ employees goes to AE Mid-market and smaller goes to SDR.
5. **Who to contact.** Founder or CEO under 30 people. Head of Sales or VP Sales under 100. VP Sales, then the Sales Development Manager, above that. If TheirStack names the hiring team, they're attached as contacts.
6. **Draft the opener.** It names the role and the post date, then the one problem a new SDR hits first: a month spent building lists and a sending setup.
7. **Write to HubSpot.** Upsert the company by domain, so a company that posts again gets its signal refreshed instead of a duplicate record.

`launchd` runs it every day at 8:30 with `--limit 15` ([the plist](com.travis.gtm-signal-to-crm.plist)). At 1 credit a job, the free 200 credits last about two weeks.

## What broke or surprised me

- **The hiring team is almost always empty.** TheirStack named one on 1 of the 20 jobs, so a real version needs a people lookup after this step. I left it out to keep the run at 20 credits. The fix is a waterfall on the recommended title, cheapest source first, like [project 02](../02-warm-leads-list).
- **"Direct employer" still lets agencies through.** A few of the 18 resell IT services or office equipment. The industry exclusion catches some, and a hand pass would catch the rest.
- **Dry runs aren't free.** The API charges per job returned, whether or not you write anything. So the first real run went straight to `--apply` against a sandbox HubSpot account instead of being paid for twice.

## Run it

```
export THEIRSTACK_API_KEY=...   HUBSPOT_TOKEN=pat-...   # private app with company schema write
python3 run.py --apply --limit 20
cp com.travis.gtm-signal-to-crm.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.travis.gtm-signal-to-crm.plist
```

It uses the HubSpot client from [project 06](../06-crm-cleanup).
