#!/usr/bin/env python3
"""Claude Code PreToolUse hook: do not create a Smartlead campaign for a lane that already has one.

Born 10-16: two Claude sessions each built a data-center-makers campaign (one ACTIVE with 46
leads, one a draft) and overlapping companies would have been emailed twice. At 14 parallel
sessions, only a check against the live account catches it.
Fires on the MCP create_campaign tool and on shell commands that POST to /campaigns/create.
Compares the new name (minus the "Demand Generation |" / "Data Advisory |" label) with every
ACTIVE / DRAFTED / PAUSED campaign created in the last 21 days; denies at >= 60% word overlap.
A name containing "follow-up" or "followup" is allowed (a deliberate second campaign).
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_scan import read_only, script_sources  # noqa: E402
import sl_api  # noqa: E402

# A real create: the REST path, or the gtm-skills CLI subcommand. The bare tool name in prose
# (a memory note, a doc) is not a create and must not trip the gate (false positive 10-16).
CREATE = re.compile(r"/campaigns/create\b|smartlead\.py\s+create[-_ ]campaign\b", re.I)
STOP = {"and", "the", "of", "for", "a", "an", "to", "in", "on", "with", "ppl", "demand", "generation", "data",
        "advisory", "staging", "archive", "makers", "contractors", "dealers", "firms", "companies"}


def toks(name: str) -> set[str]:
    name = re.sub(r"^\s*[\w ]+\|", "", name.lower(), count=1)
    return {w for w in re.findall(r"[a-z0-9]+", name) if w not in STOP and len(w) > 2}


def deny(why: str) -> int:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "DUPLICATE-LANE GATE: " + why +
        " Check with Travis or reuse that campaign. Name a deliberate second campaign with "
        "'follow-up' in the name."}}))
    return 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    tool, inp = data.get("tool_name", ""), data.get("tool_input") or {}
    if tool == "mcp__smartlead__create_campaign":
        names = [str(inp.get("name") or "")]
    elif tool == "Bash":
        cmd = inp.get("command", "")
        if read_only(cmd):
            return 0
        text = cmd
        if not CREATE.search(cmd):
            srcs = [t for _, t in script_sources(cmd, data.get("cwd", "")) if CREATE.search(t)]
            if not srcs:
                return 0
            text = cmd + "\n" + "\n".join(srcs)
        names = re.findall(r"""["']name["']\s*[:=]\s*["']([^"']{4,120})["']""", text)
        if not names:
            return deny("this command creates a campaign but the name could not be read to compare.")
    else:
        return 0
    camps = sl_api.get("campaigns")
    if not isinstance(camps, list):
        return deny("could not read the campaign list to check for a duplicate.")
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=21)
    hits = []
    for nm in names:
        if re.search(r"follow[- ]?up", nm, re.I):
            continue
        a = toks(nm)
        if not a:
            continue
        for c in camps:
            if c.get("status") not in ("ACTIVE", "DRAFTED", "PAUSED", "START"):
                continue
            try:
                made = dt.datetime.fromisoformat(c["created_at"].replace("Z", "+00:00"))
            except Exception:
                continue
            if made < cutoff:
                continue
            b = toks(c.get("name", ""))
            if b and len(a & b) / min(len(a), len(b)) >= 0.6:
                hits.append(f"'{nm}' looks like {c['id']} ({c['status']}) '{c['name']}'")
    return deny("; ".join(hits[:4]) + ".") if hits else 0


if __name__ == "__main__":
    sys.exit(main())
