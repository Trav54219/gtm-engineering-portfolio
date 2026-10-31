---
layout: default
title: How I chose the stack
---

# How I chose the stack

Each entry says what I picked, why, and what it cost me. The client portal and the data tooling are in private repos, so the code itself isn't linked here. The public projects are.

## Convex for the portal backend

The portal has three kinds of work: scheduled jobs (an hourly bounce check on campaigns), inbound webhooks (social posting events, sequencer events) and dashboards clients keep open all day. Convex covers all three in one TypeScript codebase. Crons, HTTP endpoints for webhooks, and queries that push changes to an open tab without polling.

Secrets stay in Convex production. The social posting API key and its webhook secret live there and nowhere else, and webhook signatures are checked inside Convex, so the frontend host never holds them.

It also replaced Zapier-style automation tools. Claude Code writes the logic and Convex runs it, so a trigger with real branching is an ordinary function instead of a chain of pre-built steps.

What it cost:

- There's no staging environment. A backend deploy swaps functions under clients' open tabs, so I batch deploys, keep changes to public functions additive, and wrote a test that a failed database call never signs a client out or tells them their account doesn't exist.
- Since GitHub Actions stopped running on my account, the backend deploys by hand: a dry run first, then the deploy, then a check that the function count matches.
- The backend is written against Convex's API. Moving off it would be a rewrite.

## Next.js on Vercel for the frontend

A merge to main deploys the frontend, and the build runs the whole test suite first (about 14,900 tests), so a failing test blocks the deploy. A page left open across a deploy reloads itself instead of throwing errors on the next click.

## WorkOS for sign-in

I didn't want to write authentication myself, so client sign-in runs on WorkOS AuthKit. The one rule I added on top: "couldn't reach the database" is never treated as "you don't have an account" or "your session expired." Both of those bugs logged real clients out before the rule and its test existed.

## A second sequencer added under a live one

Every campaign ran on Smartlead. Adding PlusVibe meant changing code that live client campaigns depended on, so the integration shipped switched off: separate switches for reads and writes, copy translation that refuses to convert anything it can't convert exactly, and no automatic resends. [The write-up](plusvibe-integration.md) has the details and the 123 tests.

## treg for paid data

I don't subscribe to one big contact database. treg is one key in front of thousands of data endpoints, each priced per call with a measured success rate, so I can pick the cheapest provider that works for each job.

- Own keys first. A wrapper calls our own vendor keys first, which costs nothing extra, and falls back to treg credits only when our key fails (401, 402, 429 or a 5xx). Any other error is a mistake in my parameters, and retrying it on credits would pay for the same mistake twice.
- Price sweep before a new job. I search the whole catalog for every provider of that job, read the unit (per call, per result and per success aren't the same price), then test the two or three cheapest on 10 real rows. The cheapest one that finds as much as the best one wins.
- Every call is tagged and logged. Each call carries a job name and logs the real balance change, so I can say what a list cost.
- Paid email lookups need evidence. One early run made 46 paid lookups, and 20 of the results had to be dropped, 7 of them for the wrong person. Now a paid lookup needs a source page naming the person, a free pattern guess gets verified first, and any email that isn't on the company's domain is thrown out.

Example: the NYC job search behind my own job hunt pulled 449 postings for about 5 cents and the full text of 68 more postings at $0.001 each.

## Every paid call is cached

Re-running a list is normal: re-scoring after an ICP change, or resuming a crashed enrichment run. Every paid call goes through one cache keyed on provider, endpoint and exact parameters, kept for 30 days. Three rules:

- A failure is never cached, because a cached error looks exactly like a real answer.
- Account balances are never cached, because a cached balance is wrong and gets worse with age.
- If the cache breaks, the call goes out live. A broken cache should cost money, never crash a run.

## Two checks on every email

Emails come from Blitz, which is a flat-rate plan for email lookups. Every address is then verified with MailTester Ninja before a campaign can launch, and preflight fails if a result is missing. Only invalid addresses and MX errors are hard stops. Catch-all addresses go in their own campaign: on my scoreboard, a catch-all list bounced at 7.9% against 0.4% for the verified list from the same source.

## Guards instead of my own memory

Nine scripts block a launch, a lead upload or a spend when something is wrong. A campaign can't start without a preflight pass from the last 12 hours. That gate stopped a client campaign whose 18 inboxes all read 0% reputation an hour into warmup. Starting it would have burned fresh domains before they had any reputation. [The guard code](https://github.com/Trav54219/gtm-engineering-portfolio/tree/main/guards).

## Claude Code as the builder, a second agent as the checker

An agent grading its own work tends to pass it. So one agent builds, a second agent that never saw the builder's notes grades the result against a written rubric, and I approve the plan and the ship separately. On the first run the checker found four gaps the builder missed. [The write-up](agent-loop.md).

## Public projects in plain Python

The public repos use the Python standard library wherever they can, so anyone can clone one and run it without installing anything.
