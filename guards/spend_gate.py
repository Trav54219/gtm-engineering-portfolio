"""Code-level spend gate (Travis 10-18: "how do we make sure this never happens again").

Why: on 10-18 a 16,913-lead list was verified (about $22 treg + MailTester) before company size was checked and before the funnel ran,
because the PreToolUse hooks only read command text and my scripts called the verifier directly. This runs INSIDE the spending code.

Rule: a BULK verification (more than BULK_MIN emails in one call) refuses unless every email's domain is on a ledger of companies that
already passed a free filter: ~/.breezy/funnel_survivors.txt (lead_funnel.py) or ~/.breezy/size_ok_domains.txt (size_filter.py).
Single or small checks (client previews, replies) are never blocked.
Bypass is Travis-only: he creates the file ~/.breezy/spend_gate_off (`! touch ~/.breezy/spend_gate_off`). An env var typed in a command does nothing.
"""
import os
from pathlib import Path

HOME = Path.home() / ".breezy"
LEDGERS = [HOME / "funnel_survivors.txt", HOME / "size_ok_domains.txt"]
BULK_MIN = 50
FREE_MAIL = {'gmail.com','yahoo.com','hotmail.com','outlook.com','aol.com','icloud.com','live.com','msn.com','comcast.net','att.net','verizon.net','bellsouth.net','me.com','protonmail.com','proton.me'}  # free-mail owners are sized by their company WEBSITE upstream; the email domain says nothing about the company


def _domains(path):
    try:
        return {l.strip().lower() for l in open(path) if l.strip()}
    except FileNotFoundError:
        return set()


def require_free_filters(emails, what="bulk email verification"):
    emails = [e for e in emails if e]
    if len(emails) <= BULK_MIN or (HOME / "spend_gate_off").exists():
        return
    try:
        from lead_guards import root_domain
    except Exception:
        root_domain = lambda x: x.split('@')[-1].lower()
    ok = {root_domain(d) for d in set().union(*(_domains(p) for p in LEDGERS))}
    missing = sorted({e.split("@")[-1].lower() for e in emails if root_domain(e) not in ok} - FREE_MAIL)
    if missing:
        raise SystemExit(
            f"SPEND GATE: {what} on {len(emails)} emails refused: {len(missing)} domains never passed a free filter "
            f"(e.g. {', '.join(missing[:3])}). Run size_filter.py (free size) and/or lead_funnel.py first and verify only the survivors. "
            f"Bypass is Travis-only: he creates ~/.breezy/spend_gate_off.")
