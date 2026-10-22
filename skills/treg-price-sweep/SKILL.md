---
name: treg-price-sweep
description: Run BEFORE any new treg task (company search, people search, email find, verify, scrape, signals). Sweeps the whole treg catalog for every provider of the job, ranks by price, and probes quality on 10 rows before any volume spend. Triggers - 'treg', 'enrich', 'find emails', 'find companies', 'pull a list', 'verify emails', 'what does it cost', any paid data call.
---

# treg price sweep (his rule, 10-18)

Travis: "look through the entire catalog and find the best prices for quality so we're not overspending." Another session found companies for almost nothing, so never reuse an old provider or price from memory.

## What costs money here

The sweep is free: `treg catalog search` and `catalog get` are not billed (10-18: 18 sweep queries, none on the treg ledger; balance $111.20). Only step 4's probe spends, about $0.05 for 10 rows at list prices, hard-capped at `--budget 0.25`. Run `treg balance` before and after any paid step and report the real delta. Never probe with `treg.people.email.find` routed (it picks the provider itself); name the child id.

## Claims rule (10-18, his: 'seems like I have to correct you every day')
Never tell him a price, a count, 'free' or 'best' from a catalog listing or an old note. Measure it this session first: `treg balance` before and after (free = delta 0), row counts with a real CSV parser (never `wc -l`, quoted fields have newlines), pool sizes from a free count call, provider quality from a probe. If you have not measured it, say 'listed at, not measured'. Check the other sessions' memory and this price book BEFORE re-sweeping.

## Rule

Before ANY new treg task, in this order:
1. **Sweep.** For each job in the task run `./sweep.sh <outdir> "<phrase>" ...` (several phrasings per job: `find companies by industry`, `search companies by employee count and location`, `find people by job title and company`, `find work email`, `verify email deliverability`, ...). It saves 100 results per phrase. `./sort_prices.sh <outdir>` prints cheapest first. `catalog_search` and the `treg.<job>` routed id only show a few providers: the child ids are the real list.
2. **Read the unit.** per call, per result and per success are not the same. A per-result search at $0.0004 returning 100 rows costs $0.04, not $0.0004.
3. **Free and own-key first.** Free endpoints (contactout verify, companyenrich preview top 25, coresignal ids, hunter domain finder, our own Open Places / Blitz / MoltSets keys) before any paid one. Check `~/.claude/projects/-Users-travis/memory` for what the other sessions already hold (Open Places API is free and was the source for the 10-18 data-advisory wave).
4. **Read the rows, not just the hit rate (10-18, his anger: 113 of 361 'owners' were VPs of R&D).** Before any volume spend, print company, title and email for the first 20 rows and read them. Check each title with `prepull.persona_ok` against the intake buyer line and check the company is a real fit. A finder that returns an email for the wrong person is worse than one that returns none.
4b. **Probe quality on 10 rows** from the real list through the 2-3 cheapest candidates (`prepull.py probe source.csv --n 10 --budget 0.50 --go` reports $ per found email). Price is not quality: pick the cheapest that finds as many as the best one.
5. **Cap it.** Every volume run gets a `--budget` that aborts. No paid call without his OK on the number (`travis-treg-credits-no-paid-calls-without-ok-10-17`).
6. **Write the result** to the price book below with the date, so the next session starts from it, not from zero.

Never use the treg MCP for volume: `gtm-skills/utils/treg_call.py` logs real balance deltas and respects `treg_budget.py`.

## Price book, swept 2026-10-18 (list price, quality NOT probed unless noted; re-sweep if older than ~2 weeks)

Companies search: tomba.companies.search.reveal $0.000178/call · icypeas.companies.search $0.00038/result · blitzapi.companies.search $0.000495/result · crawl4ai.google.serp.maps $0.00015/success (Google Maps places) · companyenrich.companies.search.preview FREE top 25 · coresignal.companies.search free (ids only) · akta.companies.search free (name/domain lookup) · hunter.x.discover-people free · openmart.businesses.search $0.00894/result (expensive).
People search: icypeas.people.search $0.00038/result · blitzapi.people.search $0.000495/result · limadata.people.employees.search $0.002/result · oceanio.people.search $0.0162/result · findymail.search.employees $0.0198/result.
Work email find: blitzapi.people.email.find $0.000495 (works 0.9999, 115k samples; ⚠️ check it is not drawing our Blitz records pool, run 50 first) · quickenrich $0.0048 · trykitt $0.005 · aiark $0.0053 · leadsforge bulk $0.0245 · companyenrich bulk $0.098 · leadmagic profile $0.125.
Email verify: contactout.people.email.verify FREE · dropleads $0.0018 · icypeas $0.0019 · bounceban $0.004 · limadata $0.006 · tomba $0.0089. For reference MillionVerifier cost $21.90 on 16,913 (~$0.0013 each) on the 10-18 data-advisory pull. Free contactout verify is untested for catch-all quality: probe it against MailTester Ninja before relying on it.
Domain from name: hunter.x.domain-finder FREE · blitzapi.companies.linkedin-to-domain $0.000495.
Company enrich: treg.companies.enrich from $0.000495 · thecompaniesapi $0.0019 · hunter $0.0049.

Not yet swept (do it when the task needs it): phone numbers, website contact scrape, technographics, funding/hiring signals, ownership/PE flags, LinkedIn company search. Several sweep queries return nothing for odd phrasings (`search decision makers owners founders CEO` matched zero): use plain job words.

## Full catalog menu (swept 2026-10-18)

Free finds worth remembering: people.search.count and companies.search.count are FREE (companyenrich, dropleads): count before paying for rows. getleadsio has free people.phone.find, people.enrich, organization_contacts, funding and acquisition feeds. contactout work/personal/phone availability checks are free. people.email.find has 33 providers, people.search 47, companies.search 40.
