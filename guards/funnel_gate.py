#!/usr/bin/env python3
"""Claude Code PreToolUse hook: no paid verification on a lead whose company never passed lead_funnel.py.

Travis 10-16: stop paying to verify/enrich companies that were never the buyer. lead_funnel.py appends every domain
that scored >= min-score to ~/.breezy/funnel_survivors.txt. Gated here: `mailtester_filter.py <csv>` and
`debounce.py batch|verify` (the two verification spends). Every email's domain must be in the ledger.
Free steps (funnel itself, prescreen, reads) are never blocked. Bypass is Travis-only: export FUNNEL_GATE_OFF=1 in the shell BEFORE starting Claude Code (typing it in a command does nothing).
A broken gate fails open, like prescreen_gate.py.
"""
import json, os, re, shlex, sys, time, traceback
from pathlib import Path

LEDGER = Path.home() / ".breezy" / "funnel_survivors.txt"
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def deny(why: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "FUNNEL GATE: " + why + " Run  python3 ~/breezy-brain/tools/lead_funnel.py <leads.csv> --buyer \"...\" --sample 100  first "
        "(then without --sample) and verify only survivors.csv. Bypass is Travis-only: export FUNNEL_GATE_OFF=1 in the shell BEFORE starting Claude Code (typing it in a command does nothing)."}}))
    sys.exit(0)


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        return
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if "FUNNEL_GATE_OFF=1" in cmd or os.environ.get("FUNNEL_GATE_OFF") == "1" or re.search(r"^\s*(grep|rg|cat|head|tail|less|sed -n|git (grep|log|diff|show))\b", cmd):
        return
    m = re.search(r"(mailtester_filter\.py|debounce\.py\s+(?:batch|verify|bulk))\s+(\S+)", cmd)
    if not m:
        return
    try:
        arg = shlex.split(m.group(2))[0]
    except ValueError:  # stray quote (e.g. the script name quoted inside an echo): take the raw token, strip quote debris
        arg = m.group(2).strip("'\"}{,")
    if m.group(1).startswith("debounce.py") and "verify" in m.group(1):
        emails = [arg]
    else:
        p = Path(arg).expanduser()
        if not p.exists():
            return
        emails = [x.group(0) for x in EMAIL.finditer(p.read_text(errors="ignore"))]
    if not emails:
        return
    ok = set(LEDGER.read_text().split()) if LEDGER.exists() else set()
    doms = {EMAIL.match(e).group(1).lower().removeprefix("www.") for e in emails if EMAIL.match(e)}
    missing = sorted(d for d in doms if d not in ok)
    if missing:
        deny(f"{len(missing)} of {len(doms)} company domains never passed the funnel (e.g. {', '.join(missing[:3])}).")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:  # fail open (never block unrelated work) but LEAVE A TRACE: on 10-16 a missing import made this gate allow everything, silently
        try:
            with open(Path.home() / ".breezy" / "funnel_gate_errors.log", "a") as f:
                f.write(f"{time.strftime('%F %T')}\n{traceback.format_exc()}\n")
        except Exception:
            pass
