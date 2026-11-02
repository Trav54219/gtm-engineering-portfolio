---
layout: default
title: A sample GTM engineering roadmap
---

# A sample GTM engineering roadmap

The first thing a company's first GTM engineer should publish is a roadmap. This is the one I'd start from, before meeting a single team. It's generic on purpose: the real one gets reordered once I know where the friction is. The thinking behind it is in [my philosophy on go-to-market](gtm-philosophy.md), and the first 90 days are on [my profile](https://www.breezygrowthco.com/travis#first-90-days).

## How it gets built

1. **Intake from every team.** Sales, Marketing, Customer Success and RevOps each list what wastes their time and what they'd pay to fix. They're the customers.
2. **Every item gets an owner team and a metric.** If nobody can name the number it should move, it waits.
3. **Every item gets a type.** A quick win ships in days and earns trust. A foundation is what later work runs on. A bet is a larger build where the payoff is less certain.
4. **Order by value over effort**, with one rule on top: at least one quick win ships to production in the first 60 days, and no bet starts before the foundations it needs.
5. **Reviewed monthly with the GTM leaders**, reported weekly on one page.

**Scoring an item**

| Factor | Question | Scale |
|---|---|---|
| Reach | How many people or accounts does it touch each month? | 1 to 5 |
| Impact | How much does it move the metric for each of them? | 1 to 5 |
| Confidence | How sure are we, from data or a past build? | 50%, 80%, 100% |
| Effort | How many weeks to production, with docs, monitoring and tests? | weeks |

Score = reach × impact × confidence ÷ effort. It's a starting order, not a verdict: the leaders' review can overrule it, and the reason gets written down.

## The roadmap

| # | Use case | Team | Metric it moves | Type | Effort |
|---|---|---|---|---|---|
| 1 | CRM dedupe, owners and required fields, run on a schedule | RevOps | Duplicate rate, records with an owner | Foundation | M |
| 2 | Inbound lead enrichment and routing to the right rep | Marketing, Sales | Minutes from form to first touch | Quick win | S |
| 3 | Daily signal feed into the CRM (hiring, funding, new leaders), routed to the owner with a reason | Sales | Accounts worked per rep, meetings from signals | Quick win | S |
| 4 | Account scoring from fit plus live signals | Sales, Marketing | Conversion by score band | Foundation | M |
| 5 | Enrichment cost caps, a cache and a credit report per table | RevOps | Cost per qualified account | Foundation | S |
| 6 | Pre-meeting briefs drafted from the account record, the website and recent news | Sales | Rep prep time | Quick win | S |
| 7 | Buying-committee mapping at target accounts, verified | Sales | Contacts per opportunity | Foundation | M |
| 8 | Expansion signals at current customers: new teams, headcount growth, new locations | Customer Success | Expansion pipeline | Bet | M |
| 9 | Renewal risk: champion left, usage drop, support spikes, sent to the account owner | Customer Success | Renewal rate, saves | Bet | L |
| 10 | Champion tracking: past users who land at a new company become warm leads | Sales, CS | Meetings from past champions | Quick win | S |
| 11 | Signal-based outbound plays with guards on lists, copy and sending | Sales, Marketing | Positive replies, cost per positive reply | Foundation | M |
| 12 | Same-day event and webinar follow-up lists | Marketing | Meetings per event | Quick win | S |
| 13 | Attribution from campaign to pipeline | Marketing, RevOps | Pipeline by source | Bet | L |
| 14 | AI reply and research agents, graded against a test set, risky asks routed to a person | Sales | Response time, graded quality | Bet | M |
| 15 | Data vendor review: coverage and cost per useful row, build vs. buy | RevOps | Data spend per qualified account | Quick win | S |

Effort: S is under two weeks, M is two to six, L is more than six.

## Now, next, later

| Now (first 60 days) | Next (60 to 120 days) | Later |
|---|---|---|
| 1 CRM hygiene | 4 Account scoring | 9 Renewal risk |
| 2 Inbound routing | 7 Buying committees | 13 Attribution |
| 3 Signal feed | 8 Expansion signals | |
| 5 Cost caps and cache | 11 Signal-based outbound | |
| 6 Pre-meeting briefs | 14 Graded AI agents | |
| 15 Vendor review | 10 Champion tracking, 12 Event follow-up | |

Scoring waits on the cleanup and the signal feed, because a score on duplicate accounts with no owner routes work to nobody. Renewal risk and attribution wait for clean data and a few months of history.

## Definition of done

An item is done when all of these are true, not when the code merges:

- [ ] It runs in production on a schedule or a trigger, without me
- [ ] It has an owner team that asked for it and uses it
- [ ] A short doc says what it does, what it costs and what to do when it breaks
- [ ] Failures alert someone instead of failing quietly
- [ ] Tests cover the cases that would cost money or a customer if they broke
- [ ] Its metric is on the weekly report, with the number from before it shipped

## The weekly one-pager

| Section | What's on it |
|---|---|
| Shipped | What went to production, and who it's for |
| Moved | Each live item's metric, against the number from before it shipped |
| Cost | Data and tool spend, and cost per qualified account |
| Broke | Anything that failed, what it affected and what changed |
| Next | The next two items and what they're waiting on |

The scorecard behind campaign-level numbers is on [campaign scorecard, checklist and the math](campaign-scorecard.md).
