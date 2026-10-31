"""Clean the CRM: merge duplicate companies and contacts, attach orphans, fix name
casing, then write a fit score, the reason behind it and a route onto every contact.

    python3 clean.py           # dry run: writes runs/plan.csv, changes nothing
    python3 clean.py --apply   # does it, and logs every merge to runs/merges.csv
"""
import csv
import os
import re
import sys

import hs

APPLY = "--apply" in sys.argv
PERSONAL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "aol.com",
            "gmail.example.net", "yahoo.example.net", "outlook.example.net"}
SUFFIXES = {"inc", "llc", "co", "corp", "group", "company", "ltd", "and"}
TARGET_INDUSTRIES = {"Manufacturing"}
CO_PROPS = ["name", "domain", "numberofemployees", "gtm_industry", "gtm_seed_key"]
CT_PROPS = ["email", "firstname", "lastname", "jobtitle", "company", "phone", "gtm_seed_key"]

os.makedirs("runs", exist_ok=True)


def norm_domain(d):
    d = (d or "").lower().strip()
    d = re.sub(r"^https?://", "", d).split("/")[0]
    return d[4:] if d.startswith("www.") else d


def norm_name(n):
    toks = re.sub(r"[^a-z0-9 ]", " ", (n or "").lower().replace("&", " and ")).split()
    while toks and toks[-1] in SUFFIXES:
        toks.pop()
    return " ".join(toks)


def email_domain(e):
    return (e or "").lower().split("@")[-1]


def digits(p):
    return re.sub(r"\D", "", p or "")


class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)

    def groups(self, items):
        out = {}
        for i in items:
            out.setdefault(self.find(i), []).append(i)
        return [g for g in out.values() if len(g) > 1]


def seeded(obj, props):
    return [r for r in hs.list_all(obj, props) if r["properties"].get("gtm_seed_key")]


def merge_groups(obj, groups, by_id, pick, log, plan):
    for g in groups:
        primary = pick([by_id[i] for i in g])["id"]
        for other in g:
            if other == primary:
                continue
            row = [obj, primary, other, by_id[primary]["properties"]["gtm_seed_key"],
                   by_id[other]["properties"]["gtm_seed_key"]]
            plan.writerow(["merge"] + row)
            if APPLY:
                hs.merge(obj, primary, other)
                log.writerow(row)


def junk_company_pass(plan):
    """Archive companies whose domain is a personal email provider (auto-created from a contact's address)."""
    junk = [c for c in hs.list_all("companies", ["name", "domain"])
            if norm_domain(c["properties"].get("domain")) in PERSONAL]
    for c in junk:
        plan.writerow(["archive", "companies", c["id"], "", c["properties"].get("domain"), "personal-email domain"])
    if APPLY and junk:
        hs.batch("companies", "archive", [{"id": c["id"]} for c in junk])
    return len(junk)


def company_pass(log, plan):
    cos = seeded("companies", CO_PROPS)
    by_id = {c["id"]: c for c in cos}
    uf, seen = UF(), {}
    for c in cos:
        for k in (("d", norm_domain(c["properties"].get("domain"))), ("n", norm_name(c["properties"].get("name")))):
            if not k[1]:
                continue
            if k in seen:
                uf.union(c["id"], seen[k])
            seen[k] = c["id"]
    groups = uf.groups(by_id)

    def pick(recs):  # keep the record that has a clean domain, then the oldest
        return sorted(recs, key=lambda r: (not r["properties"].get("domain"),
                                           (r["properties"].get("domain") or "").startswith("www."), int(r["id"])))[0]

    merge_groups("companies", groups, by_id, pick, log, plan)
    return len(groups), sum(len(g) - 1 for g in groups)


def company_index():
    cos = seeded("companies", CO_PROPS)
    by_domain, by_name = {}, {}
    for c in cos:
        d = norm_domain(c["properties"].get("domain"))
        if d:
            by_domain[d] = c
        by_name.setdefault(norm_name(c["properties"].get("name")), c)
    return {c["id"]: c for c in cos}, by_domain, by_name


def resolve_company(ct, by_id, by_domain, by_name):
    """Return (company record, how it was found) or (None, None)."""
    assoc = ct.get("associations", {}).get("companies", {}).get("results", [])
    for a in assoc:
        if a["id"] in by_id:
            return by_id[a["id"]], "associated"
    dom = email_domain(ct["properties"].get("email"))
    if dom not in PERSONAL and dom in by_domain:
        return by_domain[dom], "email domain"
    typed = norm_name(ct["properties"].get("company"))
    if typed and typed in by_name:
        return by_name[typed], "typed company name"
    return None, None


def contact_pass(log, plan):
    by_id, by_domain, by_name = company_index()
    cts = seeded("contacts", CT_PROPS)
    cmap = {c["id"]: c for c in cts}
    uf, seen = UF(), {}
    for c in cts:
        p = c["properties"]
        co, _ = resolve_company(c, by_id, by_domain, by_name)
        keys = []
        if co:
            keys.append(("name@co", (p.get("firstname") or "").lower(), (p.get("lastname") or "").lower(), co["id"]))
        if len(digits(p.get("phone"))) >= 10:
            keys.append(("phone", digits(p.get("phone"))))
        for k in keys:
            if k in seen:
                uf.union(c["id"], seen[k])
            seen[k] = c["id"]
    groups = uf.groups(cmap)

    def pick(recs):  # keep the work-email record, then the one with more filled fields, then the oldest
        def rank(r):
            p = r["properties"]
            personal = email_domain(p.get("email")) in PERSONAL
            filled = sum(1 for k in CT_PROPS if p.get(k))
            return (personal, -filled, int(r["id"]))
        return sorted(recs, key=rank)[0]

    merge_groups("contacts", groups, cmap, pick, log, plan)
    return len(groups), sum(len(g) - 1 for g in groups)


def fix_case(s):
    if not s or not (s.isupper() or s.islower()):
        return s
    return "-".join(w.capitalize() for w in s.lower().split("-"))


def score(p, co):
    title = (p.get("jobtitle") or "").lower()
    parts = []
    if re.search(r"\b(owner|founder|ceo|president)\b", title):
        parts.append(("owner-level title", 40))
    elif re.search(r"\b(vp|vice president|director|head)\b", title):
        parts.append(("VP/director title", 30))
    elif "manager" in title:
        parts.append(("manager title", 15))
    elif title:
        parts.append(("other title", 5))
    else:
        parts.append(("no title", 0))
    emp = int((co or {}).get("properties", {}).get("numberofemployees") or 0) if co else 0
    if 50 <= emp <= 500:
        parts.append((f"{emp} employees", 30))
    elif 10 <= emp < 50:
        parts.append((f"{emp} employees", 20))
    elif emp > 500:
        parts.append((f"{emp} employees", 15))
    elif emp:
        parts.append((f"{emp} employees", 5))
    else:
        parts.append(("no company", 0))
    ind = co["properties"].get("gtm_industry") if co else None
    parts.append((f"{ind or 'unknown'} industry", 20 if ind in TARGET_INDUSTRIES else 5 if ind else 0))
    if email_domain(p.get("email")) not in PERSONAL:
        parts.append(("work email", 10))
    total = min(100, sum(v for _, v in parts))
    return total, ", ".join(f"{k} +{v}" for k, v in parts), emp


def route(total, emp, co, personal):
    if not co and personal:
        return "Nurture"
    if total < 30:
        return "Nurture"
    if emp >= 200:
        return "AE Enterprise"
    if emp >= 50:
        return "AE Mid-market"
    return "SDR"


def enrich_pass(plan):
    hs.ensure_property("contacts", "gtm_fit_score", "GTM fit score", "number", "number")
    hs.ensure_property("contacts", "gtm_fit_reason", "GTM fit reason", "string", "text")
    hs.ensure_property("contacts", "gtm_route", "GTM route", "enumeration", "select",
                       ["AE Enterprise", "AE Mid-market", "SDR", "Nurture"])
    by_id, by_domain, by_name = company_index()
    updates, links, attached, recased = [], [], 0, 0
    for c in seeded("contacts", CT_PROPS):
        p = c["properties"]
        co, how = resolve_company(c, by_id, by_domain, by_name)
        if co and how != "associated":
            links.append((c["id"], co["id"]))
            attached += 1
            plan.writerow(["attach", "contacts", c["id"], co["id"], p["gtm_seed_key"], how])
        props = {}
        for f in ("firstname", "lastname"):
            fixed = fix_case(p.get(f))
            if fixed != p.get(f):
                props[f] = fixed
        if props:
            recased += 1
        total, why, emp = score(p, co)
        personal = email_domain(p.get("email")) in PERSONAL
        props.update({"gtm_fit_score": str(total), "gtm_fit_reason": why,
                      "gtm_route": route(total, emp, co, personal)})
        updates.append({"id": c["id"], "properties": props})
    if APPLY:
        hs.associate(links)
        hs.batch("contacts", "update", updates)
    return attached, recased, len(updates)


def main():
    with open("runs/plan.csv", "w", newline="") as pf, open("runs/merges.csv" if APPLY else os.devnull, "a", newline="") as lf:
        plan, log = csv.writer(pf), csv.writer(lf)
        plan.writerow(["action", "object", "primary_or_contact", "other_or_company", "seed_key_a", "seed_key_b"])
        print(f"junk companies on personal-email domains: {junk_company_pass(plan)}")
        g, m = company_pass(log, plan)
        print(f"companies: {g} duplicate groups, {m} merges")
        g, m = contact_pass(log, plan)
        print(f"contacts: {g} duplicate groups, {m} merges" + ("" if APPLY else " (company merges not applied, so this undercounts)"))
        a, r, n = enrich_pass(plan)
        print(f"attached {a} contacts to companies, fixed casing on {r}, scored and routed {n}")
    print("APPLIED" if APPLY else "DRY RUN: nothing changed. See runs/plan.csv, then rerun with --apply")


if __name__ == "__main__":
    main()
