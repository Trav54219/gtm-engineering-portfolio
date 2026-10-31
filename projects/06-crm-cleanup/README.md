# 06: CRM cleanup, scoring and routing in HubSpot

A messy B2B CRM goes in. A deduplicated, scored and routed CRM comes out, and an answer key grades every merge.

## Result (HubSpot account, 2026-10-31)

| | Before | After |
|---|---|---|
| Company records | 98 | 80 |
| Companies with a duplicate record | 18 | 0 |
| Contact records | 316 | 286 |
| People with a duplicate record | 30 | 0 |
| Contacts with no company | 40 | 8 |
| Names in all caps or all lowercase | 86 | 0 |
| Contacts with a fit score and a route | 0 | 286 |

**48 merges, 48 right, 0 wrong**, graded against the answer key. That includes 6 decoys: different people with the same name at different companies, and none of them were merged. The 8 contacts left without a company used a personal email and gave no company name, so there was nothing to match them on. A second run finds nothing to do.

Routes: 10 AE Enterprise, 101 AE Mid-market, 154 SDR, 21 Nurture.

## What's in the mess

`seed.py` builds it from a fixed random seed, so every run is the same. Every email sits on an `example.com` subdomain or `example.net`, which can't reach a real inbox.

- 80 companies, plus 18 duplicate records: a changed suffix ("Inc" to ", LLC"), a `www.` domain, or no domain and a lowercase name.
- 286 people, plus 30 duplicate records:
  - a personal address with the company name typed in
  - a second work address at the same domain
  - a personal address that shares the phone number
- 6 decoys with the same name at a different company.
- 60 contacts with no company attached, 40 with broken name casing, and 30 with no title.

`answer_key.json` maps every record to the company or person it really is.

## What `clean.py` does

1. Archives companies created on a personal-email domain.
2. Merges companies that share a domain (with `www.` stripped) or a name (lowercased, punctuation removed, "Inc/LLC/Co/Group" dropped). It keeps the record with a clean domain, then the oldest.
3. Merges contacts that share a first name, last name and company, or a phone number. It keeps the work-email record, then the most complete record, then the oldest. A contact's company is found from its association, then its email domain, then the company name it typed.
4. Attaches contacts to their company, then fixes name casing.
5. Writes three properties on every contact:
   - `gtm_fit_score` (0 to 100)
   - `gtm_fit_reason`, which is the score's arithmetic, for example "manager title +15, 52 employees +30, Manufacturing industry +20, work email +10"
   - `gtm_route`: AE Enterprise for 200+ employees, AE Mid-market for 50 to 199, SDR below that, and Nurture for a score under 30 or a personal email with no company

The default is a dry run, which writes `runs/plan.csv` and changes nothing. `--apply` makes the changes and logs every merge with both records' seed keys to `runs/merges.csv`, so `audit.py after` can grade them.

## What broke

- **HubSpot fixed the orphans before I did.** Its default "automatically associate contacts with companies" setting attached all 60 orphans by email domain the moment they were created. My attach step only matters for contacts with a typed company name or a matching phone. In a real portal the useful check is which contacts HubSpot *couldn't* match.
- **HubSpot invented 3 companies.** It doesn't know my fake personal domains are free-email providers, so it created a company for each one and attached every personal-email contact to it. Real Gmail addresses don't do this, but a small ISP's domain would, so the archive step stays.
- **Label clash.** HubSpot rejected a custom property labelled "Industry group" because its own `hs_industry_group` already uses that label. Labels have to be unique, not just names.
- **Merge order matters.** Contacts can only be matched to a company after the company duplicates are merged, so the dry run undercounts contact merges, and it says so.

## Limits

- The score weights are mine. They aren't fit to closed-won data, because this account has none.
- The account has one user, so the route is written to a property instead of an owner. Mapping each route to an owner list is a few lines more.
- The data is synthetic. Real CRMs have messes this doesn't model: nicknames, maiden names, shared inboxes like info@.

## Run it

```
export HUBSPOT_TOKEN=pat-...   # private app: contacts, companies, deals read/write; owners read; contact + company schemas read/write
python3 seed.py
python3 audit.py before
python3 clean.py               # dry run
python3 clean.py --apply
python3 audit.py after
python3 seed.py --reset        # archive everything seeded
```
