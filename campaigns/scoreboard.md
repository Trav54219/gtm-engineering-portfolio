# Campaign scoreboard (excerpt)

Two rules, written after getting it wrong:

1. **The denominator is contacted leads, never replies.** A departed mailbox auto-replies every time, so reply-based rates read as spectacular nonsense. One campaign: 576 sends, 8 replies, zero human. Quality over replies reads 0/8. Quality over contacted reads a 0.52% floor, not 38%.
2. **Machine replies are not replies.** Out of office, left company, wrong person and autoresponders are counted separately and never go in a numerator.

Diagnosis order when a campaign underperforms: **deliverability, then list, then offer, then copy.** One dimension changes per campaign, or the result isn't attributable.

## Case 1: a list failure that looked like a copy failure

HVAC owners (a client campaign), about 2,000 sends to 717 owners. Zero positive replies, and every categorised reply (19 of 19) was machine or wrong person. Deliverability passed, so the next lever down was the list, and the list was the problem. The list also capped near 2,150 total sends, under the roughly 2,500-send mark where I'd expect a campaign to be able to produce a result at all. Rewriting the emails would never have fixed it, so the next campaigns changed the **audience**, not the copy.

## Case 2: 13 flat-retainer campaigns, small and quiet

Run 10-09 to 10-18 across 13 niches (manufacturing and industrial service firms), then stopped and exported. Replies are Smartlead's raw count, **not** split human vs machine and not scored positive.

| Campaign | Contacted | Emails sent | Replies (raw) |
|---|---|---|---|
| Packaging machine builders | 93 | 153 | 0 |
| Pharma validation | 91 | 142 | 2 |
| Water treatment | 9 | 18 | 0 |
| Water treatment wave 2 | 69 | 102 | 0 |
| Overhead cranes | 42 | 83 | 1 |
| CNC / laser dealers | 62 | 102 | 0 |
| Industrial distributors | 118 | 157 | 0 |
| Food inspection dealers | 19 | 29 | 0 |
| Equipment lenders | 100 | 125 | 0 |
| Packaging converters | 40 | 70 | 0 |
| 3PL warehousing | 65 | 95 | 1 |
| Contract manufacturers | 120 | 138 | 0 |
| Engineering firms | 98 | 127 | 3 |
| **Total** | **926** | **1,341** | **7 (0.76% of contacted)** |

Read: too small to learn the offer's real rate. About 900 contacts and 7 raw replies is not enough to set a guarantee threshold from, and nothing was scored positive. What it did show: the list-build process (below) produced sendable owner-level leads in 13 niches, and the thin pools (9 to 40 contacts in several niches) were the binding constraint, not the copy.

## Case 3: retired campaigns, logged before deletion

Small pay-per-lead and demand-side tests, contacted counts only:

| Campaign type | Contacted | Replies | Bounces | Interested |
|---|---|---|---|---|
| M&A advisors x HVAC/plumbing sellers, verified list | 238 | 3 | 1 | 1 |
| M&A advisors x HVAC/plumbing sellers, catch-all list | 114 | 1 | 9 (7.9%) | 0 |
| Machine vision integrators | 9 | 0 | 0 | 0 |
| Welding cell integrators | 41 | 0 | 0 | 0 |
| Pet kennels x dog food makers (kennel side) | 92 | 1 | 0 | 0 |

The catch-all list bouncing at 7.9% against 0.4% on the verified list is why verified and catch-all go in separate campaigns.

## What this changed in how I work

- A micro-test needs a pool large enough to produce a result. I now size the pool before building the campaign. If the whole market is 13 firms, a 10-lead test can't reach a verdict, and I say so before spending.
- Every campaign gets a stop rule before launch (see `guards/kill_gate.py`).
- No campaign gets judged on fewer sends than its dimension needs. I don't reallocate on a difference under thousands of sends per segment.
