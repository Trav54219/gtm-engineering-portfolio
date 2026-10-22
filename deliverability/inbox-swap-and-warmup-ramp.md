# Runbook from the incident: swap inboxes, warm up, gate the launch

1. **Snapshot first.** Old accounts, the inbox-to-campaign map for all 63 campaigns, and lead exports go into a dated backup folder before anything is deleted.
2. **Wait for DNS to settle.** The provider asked for 24 hours after the swap. Warmup stays off until then, so T0 + 24h was the earliest switch-on.
3. **Warmup on for the whole fleet:** 20 a day, ramp 5, 40% reply rate. Verified by pulling every account's status afterwards (225 of 225 ACTIVE), not by trusting the toggle's response.
4. **Campaigns stay paused.** First sends go out at a low cap and ramp.
5. **Launch gate.** A campaign can't be started without a preflight PASS written in the last 12 hours (see `guards/launch_gate.py`). A client campaign's full preflight **failed on the first check: all 18 of its inboxes read 0% reputation after about an hour of warmup**, plus no spintax on three steps. I waited. The alternative, overriding the gate, would have burned fresh inboxes on a campaign before they had any reputation.
6. **Re-check after a day or two of warmup.** The gate passes at inbox reputation of 90% or better, or when the owner of the account explicitly overrides.

The same gate hook blocks the "start" call from a shell and from the API tool. An override flag exists, but only the account owner can set it, in the shell before the session starts, so an agent can't type its own way past it.
