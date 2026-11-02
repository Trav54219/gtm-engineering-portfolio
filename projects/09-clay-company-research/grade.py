"""Grade the Clay table against a hand-built answer key. Prints aggregate results only:
no names or emails, since the key holds real people.
usage: grade.py <dir with answer_key.json and out_*.json>"""
import json, re, sys
from pathlib import Path

d = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
key = json.loads((d / "answer_key.json").read_text())
# Mail domains that verified for a company besides its website domain (BounceBan, 11-01).
EXTRA_MAIL = {"basis": {"ofbasis.com"}, "pigment": {"gopigment.com", "pigment.com"}}


def rows(name):
    return {r["id"]: (r.get("result") or {}) for r in json.loads((d / name).read_text()).get("data", [])}


dom, email, ppl, tech = rows("out_domain.json"), rows("out_email.json"), rows("out_people.json"), rows("out_tech.json")
n = len(key)
dom_ok = [k for k, v in key.items() if dom.get(k, {}).get("Domain") == v["domain"]]
same = [k for k, v in key.items() if (email.get(k, {}).get("Work Email") or "").lower() == v["email"].lower()]
deliverable_alt = [k for k, v in key.items() if k not in same and (email.get(k, {}).get("Work Email") or "").split("@")[0] == v["email"].split("@")[0]
                   and (email.get(k, {}).get("Work Email") or "").split("@")[-1] in EXTRA_MAIL.get(k, set())]


def people(k):
    out = []
    for x in ppl.get(k, {}).values():
        if isinstance(x, dict):
            out += x.get("people") or []
    return out


in_top = [k for k, v in key.items() if any(v["manager"].split()[0] in p.get("fullName", "") and v["manager"].split()[-1] in p.get("fullName", "") for p in people(k))]
stack = {k: str(tech.get(k, {}).get("Website Tech Stack", "")).lower() for k in key}
hs = {k for k, s in stack.items() if "hubspot" in s}
sf = {k for k, s in stack.items() if "salesforce" in s}

print(f"Domain from company name: {len(dom_ok)}/{n} right")
for k, v in key.items():
    if k not in dom_ok:
        print(f"  {v['name']}: got {dom.get(k, {}).get('Domain')}, right is {v['domain']}")
print(f"Work email: {len(same)}/{n} identical to the hand-verified address, {len(deliverable_alt)} more on another verified mail domain")
print(f"People finder (no title filter): hand-picked manager in the returned list at {len(in_top)}/{n}")
print(f"Homepage tech: HubSpot {len(hs)}, Salesforce {len(sf)}, both {len(hs & sf)}, neither {n - len(hs | sf)}")
