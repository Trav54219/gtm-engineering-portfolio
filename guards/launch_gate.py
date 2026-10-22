#!/usr/bin/env python3
"""Claude Code PreToolUse hook: no Smartlead campaign STARTS without a fresh preflight PASS.

Catches the MCP status tool and any shell command that sets a campaign's status to START.
Every campaign id in the command needs ~/.breezy/preflight/<id>.json with pass=true,
test_email=true, written in the last 12 hours by smartlead_preflight.py.

Bypass is Travis-only: export LAUNCH_GATE_OFF=1 in the shell BEFORE starting Claude Code (typing it in a command does nothing).
Wired in ~/.claude/settings.json.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_scan import read_only, script_sources  # noqa: E402
import preflight_extra  # noqa: E402

MARKERS = Path.home() / ".breezy/preflight"
# JSON/kwargs status=START, the MCP name, a /status call with START, or the gtm-skills CLI
# (`utils/smartlead.py set-status <id> START`).
START_RE = re.compile(
    # \\? : escaped JSON in a double-quoted curl body, -d "{\"status\":\"START\"}"
    r"""status\\?["']?\s*[:=]\s*\\?["']?START\b|update_campaign_status|/status\b[^\n]*START"""
    r"""|set[-_]status\b[^\n]*\bSTART\b""", re.I)
MAX_AGE = 12 * 3600


def deny(why: str) -> int:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            f"LAUNCH GATE: {why} Run  python3 ~/breezy-brain/tools/smartlead_preflight.py <ids>  "
            "(with the test email) until every campaign PASSES, then start it. "
            "Bypass is Travis-only: export LAUNCH_GATE_OFF=1 in the shell BEFORE starting Claude Code (typing it in a command does nothing)."),
    }}))
    return 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    tool, inp = data.get("tool_name", ""), data.get("tool_input") or {}

    if tool == "mcp__smartlead__update_campaign_status":
        if str(inp.get("status", "")).upper() not in ("START", "ACTIVE"):
            return 0
        # The Smartlead MCP tool names the field "id" (fixed 09-28; "campaign_id" denied every MCP start).
        ids = [str(inp.get("id") or inp.get("campaign_id") or "")]
    elif tool == "Bash":
        cmd = inp.get("command", "")
        if os.environ.get("LAUNCH_GATE_OFF") == "1" or read_only(cmd):
            return 0
        text = cmd
        if not START_RE.search(cmd):
            # `python3 start_it.py 4031730` hides the START in the file (and its imports).
            srcs = [t for _, t in script_sources(cmd, data.get("cwd", "")) if START_RE.search(t)]
            if not srcs:
                return 0
            text = cmd + "\n" + "\n".join(srcs)
        ids = sorted(set(re.findall(r"\b(\d{7})\b", text)))
        if not ids:
            return deny("this command starts a campaign but names no campaign id, so it can't be checked.")
    else:
        return 0

    now = time.time()
    bad = []
    for cid in ids:
        p = MARKERS / f"{cid}.json"
        if not p.exists():
            bad.append(f"{cid} has never passed preflight")
            continue
        m = json.loads(p.read_text())
        if not m.get("pass"):
            bad.append(f"{cid} FAILED its last preflight ({len(m.get('fails', []))} problems)")
        elif not m.get("test_email"):
            bad.append(f"{cid} passed without the test email")
        elif now - m.get("at", 0) > MAX_AGE:
            bad.append(f"{cid} passed {int((now - m['at']) / 3600)}h ago, older than 12h")
        elif not m.get("fingerprint"):
            bad.append(f"{cid} has a receipt with no content fingerprint (old preflight); run it again")
        else:
            fp = preflight_extra.fingerprint(int(cid))
            if fp is None:
                bad.append(f"{cid} could not be read back to compare with its preflight receipt")
            elif fp != m["fingerprint"]:
                bad.append(f"{cid} changed after it passed preflight (copy, leads, inboxes or settings differ from the receipt; fix and re-check in one go with preflight_after.py)")
    return deny("; ".join(bad) + ".") if bad else 0


if __name__ == "__main__":
    sys.exit(main())
