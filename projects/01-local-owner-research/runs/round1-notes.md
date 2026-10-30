# Round 1 notes (2026-10-30)

Run: 18 patterns x 6 tuning companies, 100 searches (8 skipped: two companies have no website).
Two fresh agents ran the searches; neither could see `ground-truth/`. Search: Keenable, $0.
Model use: 408,739 agent tokens for 6 companies.

## Result

- **Plain accuracy:** 3 of 6 tuning companies had their owner found by at least one pattern (50%).
  Excluding Shamrock (see below): 3 of 5 (60%).
- **Stack accuracy (repo formula):** 0 of 18 patterns reached PRIMARY or ENRICHMENT. No single
  query finds the owner for most companies; the hits are spread across different patterns.
- **By tier:** large 1/2, mid 2/2, tiny 0/2. The two tiny ones returned no owner from any allowed
  source. Their only named person was on banned registry-copy sites. No wrong name was given for
  either: the agent said "not enough evidence", which is the behaviour we want.
- **Confident wrong names:** 8, all one company (Shamrock).

## What broke

**Shamrock Plumbing was sold.** Founded 2003 by a local plumber, acquired Feb 2024 by Seacoast
Service Partners (White Wolf Capital's plumbing/HVAC rollup). Every pattern that found a name found
the founder, from his own press release and LinkedIn, which still say "owner". The registry answer
(the manager of the buyer's new LLC) was not the owner either. Corrected answer:
**owned by Seacoast Service Partners since 2024-02-27**. Checked by hand against the buyer's own
announcement, White Wolf's portfolio page and Contractor magazine.

This is the main failure mode for "large" local businesses in 2026: private-equity rollups. The web
keeps naming the founder long after a sale. Round 2 adds an acquisition check.

## Scorer fix (made after seeing results, logged here)

A two-surname name on the web ("first + both surnames") is the registry's "first + first surname". The scorer
compared only the last word and called it wrong. It now matches first name + the accepted surname
anywhere in the name. Effect: Coastal Roofing went from 2 to 6 patterns finding the owner; plain
accuracy unchanged (it was already found). No other score moved.

## Patterns

Killed (Q 2 or below): P02 about-page, P05 "owned by", P08 LinkedIn, P09 BBB, P10 Facebook,
P11 Yelp, P12 Nextdoor, P14 "family owned", P15 license board via search.
Kept for round 2: P06 `"{company}" founder OR president OR CEO` (3/6, best), P04 owner + city (2/6),
P01/P03 domain-anchored (1/4 each, only for companies with a website), P17, P18, P07, P13.

## Round 2 plan

1. Acquisition check first: `"{company}" acquired OR acquisition OR "joins"`. If a buyer is found,
   the answer is the buyer and the date, and the founder is reported as "former owner".
2. Stack the survivors in order (P06, P04, then domain-anchored, then P17) and stop at the first
   owner named with a quote, instead of scoring each query alone.
3. Fetch the cited page before reporting a name (every round-1 hit was snippet-only).
4. Tiny companies: try the Facebook page's About section and owner replies to Google reviews.
