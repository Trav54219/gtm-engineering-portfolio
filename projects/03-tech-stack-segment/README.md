# Project 3: a tech stack segment

**289 growing companies in, two segments out, $0.09 spent.** A free scanner found a stack on 276
of 289 domains (95.5%). On a 25-row random hand check it was right on 13, missed a tool on 6, named
a wrong tool on 2, and on 4 I couldn't confirm what it said. Segment 1 (on HubSpot, no other CRM):
**121**. Segment 2 (on Salesforce or Zoho, no HubSpot): **30**. Paying for the 12 empty rows found
nothing useful, so I stopped after 10.

Built with LeadGrow's [techsight-cli](https://github.com/LeadGrowGTM/techsight-cli).

## The list and why it's growing

289 US companies of 2 to 200 people (235 at 51-200), each with a sales, marketing or business
development job posted on its own hiring page (Greenhouse, Lever, Ashby, Workable) between
2026-10-01 and 2026-10-29. A company paying to add a GTM hire this month is growing. One row per
company, deduped by domain. The list came from my own job-board pull for my job search, so it cost
nothing here.

## The counts

| Step | In | Out | Cost | Notes |
|---|---|---|---|---|
| Hand scan of 3 domains | 3 | see below | $0 | read the DNS and homepage myself next to the tool's output |
| Lite pass, 200 workers | 289 | 243 with a stack | $0 | 2.5 minutes |
| Lite pass again, 50 workers | 289 | 254 with a stack | $0 | 200 workers drops DNS answers (below) |
| Deep pass, empty rows only | 35 still empty | 14 more filled (plus 3 that gained tools) | $0 | 10 subpages per site |
| Remove a false tag | 74 tagged "Apple iCloud Mail" | 0 kept | $0 | none of the 74 has an iCloud MX record |
| **Final** | 289 | **276 with a stack (95.5%)**, 13 empty | $0 | |
| Paid lookup, empty rows | 10 of 12 | 0 with a sales or marketing tool | $0.089 | Tomba via treg, $0.0089 a row |

## Confidence floor: 95

I kept the default and tested it. Re-scanning the 25 checked rows at a floor of 50 added two kinds
of thing. Analytics and hosting (Google Tag Manager, Cloudflare, jQuery) were real but useless for
segmenting. Every sales or marketing tool it added was a guess from a subdomain name, and two of
them were wrong on the evidence: tenonhq.com's `go.` subdomain was called Marketo while it points
at HubSpot, and yieldmo.com's `info.` was called HubSpot while it points at Pardot. Below 95 the
segment fields get worse, so 95 stays.

## 25-row hand check

Random sample (seed 20261030) from the final file. For each row I pulled the DNS TXT and MX
records and the homepage HTML (`scripts/evidence.py`), printed vendor markers next to the tool's
answer (`scripts/markers.py`), then read each one. Scope: sales and marketing tools (CRM,
marketing automation, email marketing, chat, visitor ID, ad pixels). Row by row in
`hand_check_25.csv`.

| Verdict | Rows | Meaning |
|---|---|---|
| Right | 13 | every tool listed is backed by evidence, nothing in scope missed |
| Missed | 6 | what it listed was right, but it left out a tool with clear evidence |
| Wrong | 2 | listed a tool that isn't there |
| Unconfirmed | 4 | rests on evidence I can't check either way |

Of the 21 rows I could judge, 2 had a wrong tool (**90% of rows clean of false tools**) and 6 had
a miss.

What the 6 misses were: HubSpot twice (an SPF record both lite runs skipped, and the HubSpot
WordPress plugin), Klaviyo twice (verification records), Mailchimp once (SPF), Intercom once (help
center). Both wrong rows are the same bug: a `linkedin-site-verification` DNS record reported as
the LinkedIn Insight Tag.

## What broke, and what I did about it

- **"Apple iCloud Mail" was wrong on all 74 rows that had it.** The fingerprint matches any TXT
  record starting `apple-domain`, which is Apple's domain verification, not a mail host. Stripped
  from the output.
- **Half the Salesforce hits are a guess.** The tool checks whether `<name>.my.salesforce.com`
  exists. For 61 of 122 Salesforce rows that is the only evidence. I opened every one: 2 redirect
  to the company's own Microsoft sign-in (confirmed), 59 show a plain Salesforce login that could
  belong to anyone named "factory" or "arbor". Those 59 carry `salesforce_evidence =
  subdomain-guess-only` and don't count toward segment 2.
- **200 workers loses results.** The same lite pass at 50 workers found a stack on 11 more rows
  and HubSpot on 123 domains instead of 109. The final file is the union of both runs.
- **Marketo can hide from it.** Inline loaders (`s.src = '//munchkin.marketo.net/...'`)
  aren't in a script tag, and the Marketo rule only matches script tags. My hand scan of
  yipitdata.com found Munchkin loading this way; the tool found Marketo on 0 of 289.

## Segments

| Segment | Strict count | Loose count (guessed Salesforce counted) |
|---|---|---|
| 1. HubSpot, no competitor CRM | **121** | 87 |
| 2. Salesforce / Pardot / Zoho, no HubSpot | **30** | 54 |
| Both (often HubSpot for marketing, Salesforce as CRM) | 37 | 71 |
| Neither | 88 | 64 |
| No data | 13 | 13 |

Signal tool for segment 1 is HubSpot: a company running its marketing on HubSpot and hiring GTM
people right now is buying for a HubSpot-shaped team. Segment 2 is the competitor stack, which
needs a different opening line. The "both" group is a third message, not a leftover.

## Paid lookup on the empty rows

12 rows had no stack after both passes and deep. I priced four tech-stack providers on treg and
tested the cheapest, Tomba ($0.0089 a row), on 10 rows first. Result: 0 of 10 returned a CRM or
marketing tool, and 4 unrelated domains came back with the identical 13-item WordPress and AdSense
list, which reads like a canned answer. $0.089 for nothing usable, so the other 2 weren't bought.
**Share of the list not paid for: 279 of 289 (96.5%).** Cost per useful row from the paid step:
none found. Next I'd try PredictLeads ($0.04, returns evidence) on the same 10 before paying for
anything at volume.

## Files

- `sample_enriched.csv`: the 25 checked rows from the final file, every column (company data only,
  no people).
- `hand_check_25.csv`: my verdict and evidence for each of the 25.
- `scripts/evidence.py`, `scripts/markers.py`: how the evidence was pulled and printed.
- Not published: the other 264 rows.

## Post (Legion community)

> **List:** 289 US companies, 2-200 people, each posted a sales/marketing/BD job on its own hiring page 10-01 to 10-29.
> **Hit rate:** 276 / 289 (95.5%), lite twice then deep on the empties.
> **25-row check:** 13 right, 6 missed, 2 wrong, 4 unconfirmed (2 wrong of 21 judged).
> **Floor:** 95. At 50 every added CRM/marketing tool was a subdomain guess, two provably wrong.
> **Segments:** HubSpot only 121, competitor only 30 (strict), both 37.
> **Paid lookup:** Tomba, 10 rows, $0.089, 0 useful. 96.5% of the list not paid for.
> **Where I'd like feedback:** 59 Salesforce hits rest only on `<name>.my.salesforce.com` existing. How do others confirm those, or do you just drop them?
