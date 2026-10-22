#!/usr/bin/env python3
"""Claude Code PreToolUse hook: never add leads to an ACTIVE or COMPLETED Smartlead campaign.

Why (10-16): leads added to an ACTIVE campaign are emailed within ~10 minutes, before any
check of ours can run; adding to a COMPLETED campaign re-activates it and sends at once.
Safe order: PAUSE the campaign, add leads, run smartlead_preflight.py until it PASSES, then
restart it. Catches the MCP add/push-leads tools and any shell command / script that POSTs to
/campaigns/<id>/leads. Allowed when every campaign id named is DRAFTED, PAUSED or STOPPED.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_scan import read_only, script_sources  # noqa: E402
import sl_api  # noqa: E402

LEAD_WRITE = re.compile(
    r"add_leads_to_campaign|push_leads_to_campaign"
    r"|/leads\b(?!/\d)[^\n]{0,240}\bPOST\b|\bPOST\b[^\n]{0,240}/leads\b"
    r"|/leads\b[^\n]{0,240}method\s*=\s*['\"]POST|-X\s*POST[^\n]{0,240}/leads\b", re.I)
BLOCK = {"ACTIVE", "COMPLETED"}


def deny(why: str) -> int:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "LEAD-ADD LOCK: " + why +
        " Pause the campaign first, add the leads, run smartlead_preflight.py until it PASSES, "
        "then restart it. Leads added to a live campaign are emailed within minutes, before any "
        "check can run."}}))
    return 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    tool, inp = data.get("tool_name", ""), data.get("tool_input") or {}
    if tool in ("mcp__smartlead__add_leads_to_campaign", "mcp__smartlead__push_leads_to_campaign"):
        ids = [str(inp.get("campaign_id") or inp.get("id") or "")]
    elif tool == "Bash":
        cmd = inp.get("command", "")
        if read_only(cmd):
            return 0
        text = cmd
        if not LEAD_WRITE.search(cmd):
            srcs = [t for _, t in script_sources(cmd, data.get("cwd", "")) if LEAD_WRITE.search(t)]
            if not srcs:
                return 0
            text = cmd + "\n" + "\n".join(srcs)
        ids = sorted(set(re.findall(r"\b(\d{7})\b", text)))
        if not ids:
            return deny("this command adds leads but names no campaign id, so it can't be checked.")
    else:
        return 0
    bad = []
    for cid in ids:
        if not cid.isdigit():
            return deny("no campaign id given.")
        c = sl_api.get(f"campaigns/{cid}")
        if not isinstance(c, dict) or not c.get("status"):
            bad.append(f"{cid}: could not read its status")
        elif str(c["status"]).upper() in BLOCK:
            bad.append(f"{cid} is {c['status']}")
    return deny("; ".join(bad) + ".") if bad else 0


if __name__ == "__main__":
    sys.exit(main())
