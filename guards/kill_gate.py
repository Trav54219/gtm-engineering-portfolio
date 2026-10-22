#!/usr/bin/env python3
"""A cut rule as a FLAG ONLY. READ ONLY: pauses nothing, sends nothing.

  set -a; . ~/gtm-skills/.env; set +a
  python3 kill_gate.py [--campaign ID ...] [--min-leads 2000] [--min-reply 1.0] [--min-positive 5.0]

For each ACTIVE campaign: leads whose email 1 went out >=48h ago are the denominator. Once that is >= --min-leads, the campaign is
flagged KILL-CANDIDATE if reply rate (out-of-office removed from both sides) < --min-reply % OR positive/replies < --min-positive %.
Below --min-leads it prints TOO EARLY: no verdict. Categories are Smartlead's AI labels. Single-step campaigns have no step 2 to save,
so the saving here is the inboxes: Travis decides, nothing is stopped by this tool.
"""
import argparse, datetime as dt, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import funnel_feedback as ff  # noqa: E402
import sl_api  # noqa: E402

POSITIVE = {"interested", "meeting request", "meeting booked", "information request", "positive"}


def verdict(rows, min_leads, min_reply, min_pos, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(hours=48)
    seen = {}
    for r in rows:
        em = (r.get("lead_email") or "").lower()
        if not em or int(r.get("sequence_number") or 1) != 1 or not r.get("sent_time"):
            continue
        try:
            t = dt.datetime.fromisoformat(str(r["sent_time"]).replace("Z", "+00:00"))
        except Exception:
            continue
        if t <= cutoff:
            seen[em] = r
    ooo = replies = pos = 0
    for r in seen.values():
        cat = str(r.get("lead_category") or "").lower()
        if cat == "out of office":
            ooo += 1
        elif r.get("reply_time"):
            replies += 1
            pos += cat in POSITIVE
    n = len(seen) - ooo
    out = {"leads": len(seen), "ooo": ooo, "replies": replies, "positive": pos}
    if len(seen) < min_leads:
        return {**out, "v": "TOO EARLY"}
    rr = 100 * replies / max(n, 1)
    pr = 100 * pos / replies if replies else 0.0
    bad = rr < min_reply or pr < min_pos
    return {**out, "rr": round(rr, 2), "pr": round(pr, 1), "v": "KILL-CANDIDATE" if bad else "KEEP"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", type=int, action="append")
    ap.add_argument("--min-leads", type=int, default=2000)
    ap.add_argument("--min-reply", type=float, default=1.0)
    ap.add_argument("--min-positive", type=float, default=5.0)
    a = ap.parse_args()
    camps = sl_api.get("campaigns") or []
    camps = [c for c in camps if (c["id"] in a.campaign if a.campaign else c.get("status") == "ACTIVE")]

    def one(c):
        try:
            return c, verdict(ff.stats(c["id"]), a.min_leads, a.min_reply, a.min_positive)
        except Exception as e:
            return c, {"v": f"ERROR {e}"}
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(one, camps))
    for c, v in sorted(res, key=lambda x: x[1]["v"]):
        print(f"{v['v']:<15} {c['id']}  {c['name'][:55]:<55} {({k: x for k, x in v.items() if k != 'v'})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
