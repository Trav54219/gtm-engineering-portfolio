# Incident: the sending fleet's shared main domain landed on a blocklist (2026-10-01)

**What happened.** The inbox provider told me 16 of my sending domains were blacklisted. The cause was one shared main domain that every inbox's SMTP host pointed to. It was listed on Spamhaus DBL, and a recheck the next morning showed a second relay domain listed too, so about 309 accounts sat behind two listed hosts.

**What I did**
- Pulled 23 affected inboxes out of 50 campaigns through the API (the provider had asked for campaigns and warmup to be paused first). I did not delete any account: removal is reversible, deletion isn't.
- Rechecked with the local resolver. A public resolver (1.1.1.1) answered `127.255.255.254`, which means "query refused", not "clean". A known-listed control domain confirmed my lookup path was working before I trusted the result.
- Turned warmup back on for the relay inboxes at 20 a day with no campaign attached, so they'd be ready when the provider's fix landed.
- Recorded which campaign lost which inbox, so nothing got re-attached to the wrong place. One campaign ended at zero inboxes and I flagged it rather than leaving it to fail silently.

**Fix.** The provider swapped the main domain. On 2026-10-20 I deleted all 309 old accounts, re-uploaded 225 new ones (75 domains, new SMTP host), and re-attached them to the 37 paused or drafted campaigns, verifying zero mismatches. The 26 completed campaigns were not re-attached.

**What it cost.** Sending capacity for the weeks between the listing (10-01) and the swap (10-20): the affected inboxes sat out of campaigns. In the migration 84 inboxes weren't carried over (27 on one relay host, 57 on another), and two campaigns still need senders.

**What I'd change**
- Never put every domain behind one shared SMTP host again, so one listing can't take the whole fleet down.
- Snapshot the inbox-to-campaign map before any bulk change. I did, and it's what made the re-attach verifiable.
- A bulk "save inbox" call tests SMTP and IMAP and blocks about 14 seconds per inbox. Sequential took 17 minutes for 75; 10 in parallel was fine for saves, but the warmup toggle rate-limits at 10 threads (HTTP 429), so I use 3 threads plus retry there.
