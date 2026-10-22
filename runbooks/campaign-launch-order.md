# Campaign launch order, and the guard behind each step

Each step has a script that refuses to proceed when it's wrong. The guards are in [`../guards`](../guards).

| Step | Rule | Guard |
|---|---|---|
| 1. Size the pool | Count first, free. If the whole market is 13 firms, a 10-lead test can't reach a verdict. | prepull / count steps |
| 2. Name the campaign | Don't create a campaign for a lane that already has one. Compares the name to every active, drafted or paused campaign from the last 21 days and denies at 60% word overlap. Born from two sessions building the same campaign. | `campaign_dup_gate.py` |
| 3. Funnel the list | Company size, persona, already-seen, before any paid step. | `funnel_gate.py` |
| 4. Spend on verification | A bulk verify (more than a threshold of emails) refuses unless every domain already passed a free filter. Born from verifying a 16,913-lead list before checking company size. | `spend_gate.py` |
| 5. Write the copy | Word count 30 to 75, one question, same ask across variants, spintax combinations all printed so a human reads each one, no banned words. | `copy_gate.py` |
| 6. Clean the names | A company name still in SHOUTING CAPS or ending "LLC" is refused at upload. | `company_name_gate.py` |
| 7. Add leads | Never to an ACTIVE or COMPLETED campaign. Leads on an active campaign are emailed within about 10 minutes, before any check can run. The order is pause, add, preflight, restart. | `lead_add_gate.py` |
| 8. Sequences | Never re-save a sequence once the campaign has sent. Re-saving gives every step a new id, so every lead looks unsent and step 1 goes out again. It emailed 12 prospects twice. | `sequence_lock_gate.py` |
| 9. Start | A preflight PASS under 12 hours old, with a test email, or no start. | `launch_gate.py` |
| 10. Judge | Contacted-lead denominator, machine replies removed, no verdict under a minimum number of leads. Flags only, never stops a campaign by itself. | `kill_gate.py` |

## Why hooks and not reminders

A reminder doesn't stop a tired person or a second agent session. These run as Claude Code PreToolUse hooks, so they fire on the tool call itself. If a gate itself crashes, it fails open, so a bug in a guard can't freeze real work. Gates that spend money are the exception: the spend gate lives inside the spending code, because a hook that only reads command text can be bypassed by a script calling the verifier directly. That's exactly what happened on 10-18.
