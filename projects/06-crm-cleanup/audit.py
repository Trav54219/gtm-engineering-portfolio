"""Measure the CRM against the answer key. Run before and after clean.py.

    python3 audit.py before
    python3 audit.py after     # also grades every merge in runs/merges.csv
"""
import csv
import json
import os
import sys
from collections import Counter

import hs
from clean import CO_PROPS, CT_PROPS, PERSONAL, email_domain, seeded

label = sys.argv[1] if len(sys.argv) > 1 else "now"
key = json.load(open("answer_key.json"))

cos = seeded("companies", CO_PROPS)
cts = seeded("contacts", CT_PROPS + ["gtm_fit_score", "gtm_route"])

co_true = Counter(key["companies"][c["properties"]["gtm_seed_key"]] for c in cos)
ct_true = Counter(key["contacts"][c["properties"]["gtm_seed_key"]] for c in cts)


real_ids = {c["id"] for c in cos}


def has_company(c):
    return any(r["id"] in real_ids for r in c.get("associations", {}).get("companies", {}).get("results", []))


work = [c for c in cts if email_domain(c["properties"].get("email")) not in PERSONAL]
names = [c["properties"].get(f) or "" for c in cts for f in ("firstname", "lastname")]
out = {
    "label": label,
    "company records": len(cos),
    "companies with a duplicate record": sum(1 for n in co_true.values() if n > 1),
    "contact records": len(cts),
    "people with a duplicate record": sum(1 for n in ct_true.values() if n > 1),
    "work-email contacts with no company": sum(1 for c in work if not has_company(c)),
    "contacts with no company": sum(1 for c in cts if not has_company(c)),
    "names in all caps or all lowercase": sum(1 for n in names if n and (n.isupper() or n.islower())),
    "contacts with no fit score": sum(1 for c in cts if not c["properties"].get("gtm_fit_score")),
    "routes": dict(Counter(c["properties"].get("gtm_route") or "none" for c in cts)),
}

if label == "after" and os.path.exists("runs/merges.csv"):
    right = wrong = 0
    wrongs = []
    for obj, _, _, ka, kb in csv.reader(open("runs/merges.csv")):
        table = key[obj]
        if table[ka] == table[kb]:
            right += 1
        else:
            wrong += 1
            wrongs.append(f"{obj}: {ka} + {kb}")
    out["merges right"] = right
    out["merges wrong"] = wrong
    out["wrong merges"] = wrongs

print(json.dumps(out, indent=1))
os.makedirs("runs", exist_ok=True)
json.dump(out, open(f"runs/audit-{label}.json", "w"), indent=1)
