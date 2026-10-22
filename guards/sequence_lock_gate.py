#!/usr/bin/env python3
"""Claude Code PreToolUse hook: never re-save a Smartlead campaign's sequences once it has SENT.

Why (10-16): re-saving sequences gives every step a NEW id, so Smartlead treats every lead as
unsent and re-sends step 1 on the next restart. It emailed 12 prospects twice.
Catches the MCP save_campaign_sequences tool and any shell command / script that POSTs to
/campaigns/<id>/sequences. Allowed only when every campaign id named has sent_count == 0.
To add a follow-up to a campaign that has sent: build a NEW follow-up campaign. No bypass flag.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_scan import read_only, script_sources  # noqa: E402
import sl_api  # noqa: E402

SEQ_WRITE = re.compile(
    r"save_campaign_sequences"
    r"|/sequences\b[^\n]{0,240}\bPOST\b|\bPOST\b[^\n]{0,240}/sequences\b"
    r"|/sequences\b[^\n]{0,240}method\s*=\s*['\"]POST|-X\s*POST[^\n]{0,240}/sequences\b", re.I)


def deny(why: str) -> int:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "SEQUENCE LOCK: " + why +
        " Re-saving sequences on a campaign that has sent resets every lead and re-sends step 1. "
        "Build a NEW follow-up campaign for the single-touch leads instead. There is no bypass."}}))
    return 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    tool, inp = data.get("tool_name", ""), data.get("tool_input") or {}
    if tool == "mcp__smartlead__save_campaign_sequences":
        ids = [str(inp.get("campaign_id") or inp.get("id") or "")]
    elif tool == "Bash":
        cmd = inp.get("command", "")
        if read_only(cmd):
            return 0
        text = cmd
        if not SEQ_WRITE.search(cmd):
            srcs = [t for _, t in script_sources(cmd, data.get("cwd", "")) if SEQ_WRITE.search(t)]
            if not srcs:
                return 0
            text = cmd + "\n" + "\n".join(srcs)
        ids = sorted(set(re.findall(r"\b(\d{7})\b", text)))
        if not ids:
            return deny("this command writes sequences but names no campaign id, so it can't be checked.")
    else:
        return 0
    bad = []
    for cid in ids:
        if not cid.isdigit():
            return deny("no campaign id given.")
        a = sl_api.get(f"campaigns/{cid}/analytics")
        if not isinstance(a, dict):
            bad.append(f"{cid}: could not read its send count, so the write is not allowed")
            continue
        sent = int(a.get("sent_count") or 0)
        if sent > 0:
            bad.append(f"{cid} has already sent {sent} email(s)")
    return deny("; ".join(bad) + ".") if bad else 0


if __name__ == "__main__":
    sys.exit(main())
