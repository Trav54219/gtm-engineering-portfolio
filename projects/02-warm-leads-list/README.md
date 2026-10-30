# Project 2: a warm leads list from a competitor's audience

**One profile in, a list read by hand out, nothing sent.** 169 engagement items for $0.34 became
105 people, 27 who fit the ICP, 6 at growing companies I'd actually email, and 5 work emails, 2 of
them verified valid. Total spend: **$0.38**.

Built with LeadGrow's [linkedin-warm-leads](https://github.com/LeadGrowGTM/linkedin-warm-leads).

## The counts

| Step | In | Out | Cost | What narrowed it |
|---|---|---|---|---|
| Scrape one profile | 8 posts | 169 items (8 posts, 139 reactions, 22 comments) → 105 people | $0.338 | Apify's own run record; the estimate was $2.11 |
| Score against the ICP | 105 | 27 at fit 4 or 5 (26 after removing the source profile) | $0.019 (two scoring runs) | gpt-4.1-mini, "honest and stingy" prompt |
| Read the top 10 by hand | 10 | I'd email 7 | $0 | a cost-containment consultant, a non-US company, one that isn't clearly a cleaning company |
| Growth filter (top 20) | 20 | 10 with a dated signal → **6** after a second read | $0 | 9 no signal, 1 not US, then by hand: 1 SaaS startup, 1 vendor-side role, 1 identity I couldn't confirm, 1 residential-only |
| Email waterfall | 6 | 5 found | $0.0145 | see below |
| Verify | 5 | 2 valid, 3 catch-all | 5 DeBounce credits + $0.0036 cross-check | catch-all = the server accepts any address, so it can't be confirmed. DeBounce and MillionVerifier gave the same verdict on all 5 |
| **Would send** | | **2** (house rule: valid only; the 3 catch-all are held) | **$0.38 total** | |

Source profile (type, not name): founder of a 600-person commercial cleaning company who hosts a
podcast for cleaning-business owners. His audience is the buyer.

## Waterfall, cheapest first

Each step only saw the previous step's misses.

| Order | Source | Tried | Found | Cost | Cost per email found |
|---|---|---|---|---|---|
| 1 | The company's own website (home, contact, about, team pages) | 6 | 2 | $0 | $0 |
| 2 | Our own database (prospect library, by domain) | 4 | 0 | $0 | n/a |
| 3 | QuickEnrich (via treg, charged only on a hit) | 4 | 3 | $0.0145 | $0.0048 |
| 4 | AI Ark (via treg, a miss is free) | 1 | 0 | $0 | n/a |
| Verify | DeBounce (my verifier for this run) | 5 | 2 deliverable, 3 accept-all | 5 credits | |
| Cross-check | MillionVerifier (via treg) | 5 | same 2 valid, same 3 catch-all | $0.0036 | |

All emails: 5 found for $0.0145, **$0.003 per email**. Generic info@ addresses on the websites
did not count. No address was guessed from a pattern. One of the 6 has no email after all
four steps and stays without one.

Two things broke on the way. QuickEnrich's direct account had 0 credits, so the step ran
through treg instead. MailTester (my usual verifier) returned "Disabled Key" on every address
and marked all 5 "unknown", so this run used DeBounce, with MillionVerifier as a second opinion.
They agreed on all 5. Both problems are noted here rather than skipped.

## What reading the list taught me

- **The repo's ranking lets a heavy commenter outrank a real buyer.** The score is fit ×
  engagement × intent, so a marketing vendor who scored fit 1 still ranked 4th because he
  commented six times, above five owners who scored 5. The fix is the lesson's own gate: only
  fit 4 to 5 goes forward, whatever the rank.
- **The scoring prompt never sees the ICP's disqualifiers.** It reads titles, industries, size,
  geography and the one-line summary, nothing else. Writing "people who sell to these companies
  score 1" into the summary (`icp.yaml` vs `icp-v1.yaml`) is what moved the vendors down.
- **The source profile shows up in its own list.** He reacts to comments on his posts. Removed
  by hand.
- **The scraper returns LinkedIn's internal member-ID URLs**, not the public profile URL. The
  email finder still matched 3 of 4 using name + company domain alongside them.
- **A growth signal isn't a buyer signal.** One "fit 5" row was an AI software startup with
  open roles: hiring, but SaaS, which the ICP excludes. Reading the 10 survivors cut 4.

## Files

- `icp.yaml`: the ICP the final scoring used. `icp-v1.yaml`: the first version, before the vendor exclusion.
- `sample_ranked_engagers.csv`: the top 30 of the ranked list, people redacted (role and scores only).
- Not published: names, LinkedIn URLs, companies and emails. The lesson's rule, and mine: no
  real people's data in a public repo. Nothing was pushed to a sequencer or sent.

## Post (Legion community)

> **Source profile (type, not name):** founder of a large commercial cleaning company with a podcast for cleaning owners.
> **My ICP in one line:** owners and sales leaders at US B2B companies that win large contracts (commercial cleaning, manufacturing, logistics), 10-200 people, no SaaS.
> **Items collected / cost:** 169 / $0.34 (everything in: $0.38)
> **Fit 4 or 5:** 27, **passed growth:** 10 by signal, 6 after reading
> **Where I'd like feedback:** the ranking puts a fit-1 vendor above fit-5 owners when he comments a lot. Do others gate on fit before rank, or change the formula?
