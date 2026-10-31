"""Seed a HubSpot account with a fake, messy B2B CRM and write the answer key.

Every record gets gtm_seed_key. answer_key.json maps each key to the real
company or person it stands for, so the cleanup can be scored afterwards.
All emails sit on example.com subdomains or example.net, so nothing can reach a real inbox.

    python3 seed.py            # create
    python3 seed.py --reset    # archive every seeded record
"""
import json
import random
import sys

import hs

SEED = 20261031
rng = random.Random(SEED)

PREFIX = ["Harbor", "Summit", "Ridge", "Cedar", "Iron", "Bluewater", "Granite", "Northfield",
          "Keystone", "Prairie", "Lakeshore", "Copper", "Redwood", "Pioneer", "Atlas", "Beacon",
          "Liberty", "Sterling", "Union", "Frontier", "Oakline", "Meridian", "Crestview", "Tidewater"]
NOUN = {  # noun -> industry
    "Valve Supply": "Manufacturing", "Fabrication": "Manufacturing", "Machine Works": "Manufacturing",
    "Packaging": "Manufacturing", "Controls": "Manufacturing", "Tooling": "Manufacturing",
    "Coatings": "Manufacturing", "Logistics": "Logistics", "Freight": "Logistics",
    "Plumbing": "Home services", "Electric": "Home services", "Roofing": "Home services",
    "HVAC": "Home services", "Staffing": "Staffing", "Dental Lab": "Healthcare",
}
SUFFIX = ["Inc", "LLC", "Co", "Group", ""]
STATES = ["TX", "OH", "PA", "NC", "GA", "FL", "IL", "MI", "WI", "TN", "AZ", "CO"]
FIRST = ["James", "Maria", "Robert", "Linda", "Michael", "Patricia", "David", "Jennifer", "Daniel",
         "Elizabeth", "Kevin", "Susan", "Brian", "Karen", "Jason", "Nancy", "Eric", "Lisa", "Mark",
         "Angela", "Steven", "Megan", "Paul", "Rachel", "Gregory", "Laura", "Derek", "Tanya", "Omar",
         "Priya", "Luis", "Grace", "Andre", "Hannah", "Victor", "Chloe", "Marcus", "Ivy", "Felix", "Nora"]
LAST = ["Smith", "Johnson", "Williams", "Brown", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Wilson", "Anderson", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
        "Harris", "Clark", "Lewis", "Walker", "Hall", "Young", "King", "Wright", "Lopez", "Hill",
        "Scott", "Green", "Adams", "Baker", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner"]
TITLES = ["Owner", "President", "CEO", "Founder", "VP of Operations", "VP of Sales", "Director of Operations",
          "Director of Purchasing", "Head of Growth", "Operations Manager", "Purchasing Manager",
          "Plant Manager", "Office Manager", "Sales Manager", "Account Executive", "Coordinator", "Engineer"]
PERSONAL = ["gmail.example.net", "yahoo.example.net", "outlook.example.net"]


def slug(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def build():
    key = {"companies": {}, "contacts": {}}
    companies, contacts = [], []

    # 80 real companies
    names = set()
    real = []
    while len(real) < 80:
        p, n = rng.choice(PREFIX), rng.choice(list(NOUN))
        if (p, n) in names:
            continue
        names.add((p, n))
        base = f"{p} {n}"
        suffix = rng.choice(SUFFIX)
        real.append({
            "id": f"CO{len(real):03d}", "base": base, "suffix": suffix,
            "name": f"{base} {suffix}".strip(), "domain": f"{slug(p + n)}.example.com",
            "industry": NOUN[n], "employees": int(min(900, max(3, rng.lognormvariate(3.6, 1.1)))),
            "state": rng.choice(STATES),
        })

    def add_company(rec_key, true_id, name, domain, c):
        props = {"name": name, "gtm_industry": c["industry"], "numberofemployees": str(c["employees"]),
                 "state": c["state"], "gtm_seed_key": rec_key}
        if domain:
            props["domain"] = domain
        companies.append(props)
        key["companies"][rec_key] = true_id

    for c in real:
        add_company(f"K{c['id']}a", c["id"], c["name"], c["domain"], c)

    # 18 companies get a second record: suffix change, www domain, or no domain + lowercase name
    for i, c in enumerate(rng.sample(real, 18)):
        kind = ["suffix", "www", "blank"][i % 3]
        if kind == "suffix":
            name, domain = f"{c['base']}, {'Inc.' if c['suffix'] != 'Inc' else 'LLC'}", c["domain"]
        elif kind == "www":
            name, domain = c["base"], "www." + c["domain"]
        else:
            name, domain = c["base"].lower() + (" & co" if i % 2 else ""), None
        add_company(f"K{c['id']}b", c["id"], name, domain, c)

    # 260 real people at those companies
    people = []
    used = set()
    while len(people) < 260:
        f, l = rng.choice(FIRST), rng.choice(LAST)
        c = rng.choice(real)
        if (f, l, c["id"]) in used:
            continue
        used.add((f, l, c["id"]))
        local = rng.choice([f"{f}.{l}", f"{f[0]}{l}", f"{f}"]).lower()
        email = f"{local}@{c['domain']}"
        if email in {p["email"] for p in people}:
            continue
        people.append({"id": f"P{len(people):03d}", "first": f, "last": l, "company": c,
                       "email": email, "title": rng.choice(TITLES),
                       "phone": f"+1 555 {rng.randint(200, 999)} {rng.randint(1000, 9999)}"})

    # 6 decoys: a different person with the same name at another company (must NOT merge)
    for d in rng.sample(people, 6):
        c = rng.choice([x for x in real if x["id"] != d["company"]["id"]])
        email = f"{d['first'].lower()}.{d['last'].lower()}@{c['domain']}"
        people.append({"id": f"P{len(people):03d}", "first": d["first"], "last": d["last"], "company": c,
                       "email": email, "title": rng.choice(TITLES),
                       "phone": f"+1 555 {rng.randint(200, 999)} {rng.randint(1000, 9999)}", "decoy_of": d["id"]})

    orphans = set(p["id"] for p in rng.sample(people, 60))
    no_title = set(p["id"] for p in rng.sample(people, 30))
    bad_caps = [p["id"] for p in rng.sample(people, 40)]
    upper = set(bad_caps[::2])
    bad_caps = set(bad_caps)
    emails = {p["email"] for p in people}

    def caps(s, pid):
        if pid not in bad_caps:
            return s
        return s.upper() if pid in upper else s.lower()

    def add_contact(rec_key, p, email, associate, first=None, last=None, company_text=None, phone=None):
        if email in emails and rec_key.endswith("b"):
            return
        emails.add(email)
        props = {"email": email, "firstname": first or caps(p["first"], p["id"]),
                 "lastname": last or caps(p["last"], p["id"]), "gtm_seed_key": rec_key}
        if p["id"] not in no_title:
            props["jobtitle"] = p["title"]
        if company_text:
            props["company"] = company_text
        if phone:
            props["phone"] = phone
        contacts.append({"props": props, "company_key": f"K{p['company']['id']}a" if associate else None})
        key["contacts"][rec_key] = p["id"]

    for p in people:
        add_contact(f"K{p['id']}a", p, p["email"], associate=p["id"] not in orphans, phone=p["phone"])

    # 30 people get a duplicate record
    dup_people = rng.sample([p for p in people if "decoy_of" not in p], 30)
    for i, p in enumerate(dup_people):
        kind = ["personal", "alt_pattern", "phone"][i % 3]
        if kind == "personal":  # signed up with a personal address, typed the company name
            email = f"{p['first'].lower()}{p['last'].lower()}{rng.randint(1, 99)}@{rng.choice(PERSONAL)}"
            add_contact(f"K{p['id']}b", p, email, False, company_text=p["company"]["base"])
        elif kind == "alt_pattern":  # same domain, different address
            email = f"{p['first'][0].lower()}.{p['last'].lower()}@{p['company']['domain']}"
            if email == p["email"]:
                email = f"{p['first'].lower()}{p['last'][0].lower()}@{p['company']['domain']}"
            add_contact(f"K{p['id']}b", p, email, True)
        else:  # different address, same phone, nickname
            email = f"{p['first'].lower()}.{p['last'].lower()}.office@{rng.choice(PERSONAL)}"
            add_contact(f"K{p['id']}b", p, email, False, phone=p["phone"])

    # 20 personal-only contacts: 12 typed a real company name, 8 left it blank
    for i in range(20):
        f, l = rng.choice(FIRST), rng.choice(LAST)
        c = rng.choice(real)
        pid = f"P{len(people):03d}"
        p = {"id": pid, "first": f, "last": l, "company": c, "title": rng.choice(TITLES)}
        people.append(p)
        email = f"{f.lower()}.{l.lower()}{i}@{rng.choice(PERSONAL)}"
        add_contact(f"K{pid}a", p, email, False, company_text=c["base"] if i < 12 else None)

    key["meta"] = {
        "seed": SEED, "real_companies": len(real), "company_records": len(companies),
        "real_people": len(people), "contact_records": len(contacts),
        "orphans": len(orphans), "dup_records": sum(1 for k in key["contacts"] if k.endswith("b")), "decoys": 6,
        "bad_caps": len(bad_caps), "no_title": len(no_title), "personal_only": 20,
    }
    return companies, contacts, key


def reset():
    for obj in ("contacts", "companies"):
        recs = [r for r in hs.list_all(obj, ["gtm_seed_key"]) if r["properties"].get("gtm_seed_key")]
        hs.batch(obj, "archive", [{"id": r["id"]} for r in recs])
        print(f"archived {len(recs)} {obj}")


def main():
    if "--reset" in sys.argv:
        return reset()
    hs.ensure_property("companies", "gtm_seed_key", "GTM seed key", "string", "text")
    hs.ensure_property("contacts", "gtm_seed_key", "GTM seed key", "string", "text")
    hs.ensure_property("companies", "gtm_industry", "GTM industry", "string", "text")

    companies, contacts, key = build()
    made = hs.batch("companies", "create", [{"properties": c} for c in companies])
    co_ids = {r["properties"]["gtm_seed_key"]: r["id"] for r in made}
    made = hs.batch("contacts", "create", [{"properties": c["props"]} for c in contacts])
    ct_ids = {r["properties"]["gtm_seed_key"]: r["id"] for r in made}

    pairs = [(ct_ids[c["props"]["gtm_seed_key"]], co_ids[c["company_key"]]) for c in contacts if c["company_key"]]
    hs.associate(pairs)

    json.dump(key, open("answer_key.json", "w"), indent=1, sort_keys=True)
    print(json.dumps(key["meta"], indent=1))
    print(f"created {len(co_ids)} companies, {len(ct_ids)} contacts, {len(pairs)} associations")


if __name__ == "__main__":
    main()
