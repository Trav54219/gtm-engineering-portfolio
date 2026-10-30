# GTM engineering portfolio: Travis

I run cold email outbound end to end: pick the niche, build the list, write the copy, stand up the sending infrastructure, launch, and read the results. This repo is the working evidence: the guards that stop me sending something wrong, the lists and how I built them, the incidents and what I did, and the scoreboard with the numbers as they are, including the ones that didn't work.

I work with Claude Code as the daily workspace. The copy is mine; the agent handles the scripted, checkable parts.

## What's here

| Folder | What it shows |
|---|---|
| [`projects/01-local-owner-research/`](projects/01-local-owner-research) | A research process I can put a number on: find the owner of a local service business. Answers written first from the state registry, 3 tuning rounds, one holdout run. **Holdout 2 of 4 (50%), zero wrong names**; every large and mid business right, tiny ones honestly "not enough evidence". |
| [`projects/02-warm-leads-list/`](projects/02-warm-leads-list) | A warm list from one competitor-founder's LinkedIn audience: 169 items for $0.34 → 27 ICP fits → 6 growing companies read by hand → 5 emails cheapest-first, 2 verified. $0.38 all in, nothing sent. |
| [`projects/03-tech-stack-segment/`](projects/03-tech-stack-segment) | 289 companies hiring GTM roles this month, scanned free for their stack: 276 found (95.5%), a 25-row hand check (13 right, 6 missed, 2 wrong, 4 unconfirmed), HubSpot segment 121, Salesforce/Zoho segment 30. Found three fingerprint bugs and stopped a paid lookup after 10 rows returned nothing. $0.09. |
| [`projects/04-buyer-language-brief/`](projects/04-buyer-language-brief) | Commercial cleaning owners' own words from Reddit: 51 threads scanned, 8 read in full inside a 90-day window, 19 verbatim phrases (each checked against the source by script) and five copy lines, each linked and dated. Reddit blocked direct requests, so the same two-pass method ran through a paid endpoint. About $0.06. |
| [`projects/05-agent-loop/`](projects/05-agent-loop) | One task built by an agent and graded by a second agent that never saw the builder's notes: cycle 1 4.33/5, cycle 2 4.67/5 after fixing what the checker caught. Plan and ship approved separately; [PR #1](https://github.com/Trav54219/gtm-engineering-portfolio/pull/1) opened, not merged by the loop. |
| [`guards/`](guards) | The code that sits between me (or an agent) and a send. Pre-launch hooks, spend gates, copy gate, a kill-rule flag. Each one exists because something went wrong once. |
| [`campaigns/scoreboard.md`](campaigns/scoreboard.md) | One row per campaign, rates computed on contacted leads, machine replies split out first. Includes 13 campaigns that returned 7 raw replies of 926 contacted, and what I concluded from that. |
| [`lists/`](lists) | Two list builds written as recipes: sources, funnel counts at every stage, cost, and the traps I hit. |
| [`deliverability/`](deliverability) | Two infrastructure incidents: what happened, what I did, what it cost. |
| [`skills/`](skills) | A Claude Code skill I use before any paid data call. |
| [`runbooks/`](runbooks) | The launch order I follow and why. |

## Stack

| Job | Tool |
| --- | --- |
| Sending, sequences, inbox replies | Smartlead (API and MCP) |
| Company and people data | Blitz, MoltSets, TheirStack (hiring signals), Apify (Maps) |
| Priced data calls and enrichment | treg, with a price sweep before any paid call (`skills/treg-price-sweep`) |
| Web reads and research | TinyFish |
| Daily workspace, scripts and guards | Claude Code, Python |

The guards in `guards/` call the Smartlead API directly, so they run on any campaign without the dashboard.

## A real email

This is the first email of the sequence I am sending to hiring managers for this job search (Smartlead campaign, merge fields in double braces). `{{fact}}` is a public fact about their company, `{{q}}` is a question about it, `{{subj}}` is the subject.

> {{first_name}}, {{fact}}.
>
> {{q}}
>
> I build the lists, enrichment, sending setup and copy. I can sketch what I'd set up first.
>
> Want me to send it over?
>
> Travis
> GTM engineer and founder at Breezy Growth

Why it is built this way: it opens on something true about them, asks one question, says what I do in one sentence, and asks for a yes to a one-page sketch instead of a call. No price, no link, no claim I can't show. The follow-up (day 7) says what the sketch contains: who I'd reach, a sample email in their voice, and the first 30 days, from public data only. The copy gate in `guards/copy_gate.py` checks every variant before it is built: 30 to 75 words, no banned words, the same ask in every variant.

## Where I'm honest about the numbers

- Rates use **contacted leads** as the denominator. Reply-based rates are inflated by auto-replies from departed mailboxes: one campaign read 38% on replies and 0.52% on contacted.
- Machine replies (out of office, left company, wrong person) are separated before anything is judged.
- I don't change a past row. A correction is a new row that cites the old one.
- Most of my campaigns so far are small tests. I'd rather show a small honest number than a large vague one.

## Not in this repo

Client names, lead data, API keys, prospect emails, inbox and domain lists, pricing and anything from paid courses. The private repos stay private.
