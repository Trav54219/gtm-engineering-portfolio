#!/usr/bin/env python3
"""Claude Code PreToolUse hook: refuse a Smartlead lead upload/update whose
company_name still reads scraped ("HERCON INVESTMENTS LLC").

Covers the Smartlead MCP lead tools, where the payload is visible. Scripts that
POST from inside Python can't be inspected here — they run through
scrub_list.py's cleaned chunks or call clean_company() themselves, and
smartlead_clean_company_names.py (dry run must show 0) is the launch-day net.

Wired in ~/.claude/settings.json next to scrub_gate.sh.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from clean_company import clean_company  # noqa: E402


def names(tool_input: dict):
    if "company_name" in tool_input:
        yield tool_input["company_name"]
    for key in ("lead_list", "leads"):
        for lead in tool_input.get(key) or []:
            if isinstance(lead, dict) and lead.get("company_name"):
                yield lead["company_name"]


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    bad = []
    for raw in names(data.get("tool_input") or {}):
        if isinstance(raw, str) and raw and clean_company(raw) != raw:
            bad.append(f"{raw!r} -> {clean_company(raw)!r}")
    if not bad:
        return 0
    shown = "; ".join(bad[:5]) + (f" (+{len(bad) - 5} more)" if len(bad) > 5 else "")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            f"COMPANY NAME GATE: {len(bad)} company_name(s) still read scraped: {shown}. "
            "Run each through clean_company() from ~/breezy-brain/tools/clean_company.py and resend."),
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
