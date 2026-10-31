---
layout: default
title: A blocklist listing across 309 inboxes
---

# A blocklist listing across 309 inboxes: what broke and what I changed

**Short version:** my inbox vendor told me 16 of my sending domains were blocklisted. The domains weren't the problem. Every inbox sent through one shared relay domain, and that relay was on the Spamhaus domain blocklist. I pulled the inboxes out of every campaign without deleting them, held launches for three weeks until the vendor swapped the relay, then moved the fleet and re-attached 37 campaigns with 0 mismatches. Then the new relay turned out to be listed too.

Built with: Smartlead API, Python, Spamhaus DBL lookups, Peeker blacklist API

## Timeline

| Date | What happened | What I did |
|---|---|---|
| Oct 1 | The vendor said 16 domains were blacklisted and asked me to pause campaigns and warm-up. | Found the cause: every inbox's SMTP host was the vendor's shared relay, and that relay was on the Spamhaus DBL. Removed the 23 affected inboxes from 50 campaigns. Removed, not deleted, so they could come back. |
| Oct 2 | Rechecked before a planned launch. | Both relay domains were listed, and they carried all 309 inboxes (267 on one, 42 on the other). With no clean relay left, I blocked the launch. |
| Oct 20 | The vendor swapped the relay domain. | Snapshotted the old accounts, the inbox map for 63 campaigns, and the lead exports first. Deleted the 309 old inboxes, uploaded 225 new ones across 75 domains, and re-attached them to the 37 paused and draft campaigns. 0 mismatches, and none started on their own. |
| Oct 23 | Checked the new relay with Peeker before scaling sends. | The new relay was on the DBL too. Checked every sending domain (63 clean, 10 flagged), picked senders for new campaigns only from clean domains, and removed a listed inbox from 9 campaigns. |

## What went wrong in how I checked

- **A public DNS resolver gives a fake answer.** Looking up a domain on Spamhaus through 1.1.1.1 returns 127.255.255.254, which means "public resolver refused." It's not a listing and it's not a clean result. I ran every check through a resolver Spamhaus answers, with a known-listed test domain as a control.
- **Domain-level health hid it.** The sending domains looked fine. The listing was on the relay hostname each inbox sends through, which nothing on my dashboard showed.
- **I checked the new relay after uploading, not before.** That's the lesson I'd lead with: test the SMTP host before any inbox goes on it.

## What the move cost

- 84 inboxes didn't come back, and 2 campaigns were left with no inboxes until a person picked new senders.
- 26 completed campaigns weren't re-attached, so their stats lost their inbox history.
- Smartlead tests SMTP and IMAP on every inbox save, about 14 seconds each. Uploading 75 one at a time took 17 minutes, so the rest ran 10 at a time.

## A second bug I caught: a fix the code would have undone

The one measured deliverability win I had was raising the warm-up reply rate from 30% to 40%, which cut warm-up spam placement from 33.9% to 12.2%. Later I went to apply a different warm-up change and previewed it first. The preview showed it would also drop the reply rate back to 31% on 27 inboxes.

The cause: inbox settings were picked partly by age, and only the setting for new inboxes carried 40%. As an inbox got older, a daily job moved it to a setting that still said 31%, which quietly undid the win. I put the 40% in one constant both settings read and added a test so it can't drift back.

The rule I took from it: a fix applied to the live system isn't permanent if the code that reconciles that system every day disagrees with it. Preview every apply and read every field it changes.

## What I'd build now

- A daily check that resolves the SMTP host of every inbox against Spamhaus and pauses any campaign whose relay is listed.
- The upload script refuses to run unless the relay host checks clean that day.

**The raw notes:** [the incident log](https://github.com/Trav54219/gtm-engineering-portfolio/blob/main/deliverability/incident-blacklisted-main-domain.md) and [the swap runbook](https://github.com/Trav54219/gtm-engineering-portfolio/blob/main/deliverability/inbox-swap-and-warmup-ramp.md).
