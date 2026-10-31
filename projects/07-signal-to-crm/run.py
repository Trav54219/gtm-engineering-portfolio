"""Signal to CRM: a company posts an SDR/BDR job, and the next run puts it in HubSpot
scored, routed, with the person to contact and a drafted first line.

    python3 run.py                # dry run: prints what it would write, spends TheirStack credits
    python3 run.py --apply        # writes to HubSpot
    python3 run.py --apply --limit 15

TheirStack charges 1 credit per job returned. Job ids already seen are sent back as
job_id_not, so a job is never paid for twice. Runs on a schedule via launchd (see README).
"""
import datetime as dt
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "06-crm-cleanup"))
import hs  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state", "seen_jobs.json")
APPLY = "--apply" in sys.argv
LIMIT = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 20

# The seller in this demo is an outbound agency: it wants companies standing up an SDR
# team, 10-200 people, and it doesn't sell to SaaS.
ICP = {
    "titles": ["sales development representative", "business development representative", "SDR", "BDR"],
    "min_employees": 10,
    "max_employees": 200,
    "excluded_industries": {"Software Development", "IT Services and IT Consulting"},
    "outbound_tools": {"outreach", "salesloft", "apollo-io", "smartlead", "instantly", "lemlist", "zoominfo"},
}


def env(name):
    if os.environ.get(name):
        return os.environ[name]
    for line in open(os.path.expanduser("~/gtm-skills/.env")):
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip()
    raise SystemExit(f"{name} not set")


def load_seen():
    return set(json.load(open(STATE))) if os.path.exists(STATE) else set()


def save_seen(seen):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(sorted(seen), open(STATE, "w"))


def pull_jobs(seen):
    body = {
        "job_title_or": ICP["titles"],
        "posted_at_max_age_days": 2,
        "job_country_code_or": ["US"],
        "min_employee_count": ICP["min_employees"],
        "max_employee_count": ICP["max_employees"],
        "company_type": "direct_employer",
        "property_exists_and": ["company_object.domain"],
        "job_id_not": sorted(seen),
        "limit": LIMIT,
    }
    req = urllib.request.Request(
        "https://api.theirstack.com/v1/jobs/search",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + env("THEIRSTACK_API_KEY"), "Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req, timeout=90))["data"]


def score(c, sdr_posts):
    parts = []
    emp = c.get("employee_count") or 0
    if 20 <= emp <= 100:
        parts.append((f"{emp} employees", 30))
    elif emp:
        parts.append((f"{emp} employees", 15))
    jobs30 = c.get("num_jobs_last_30_days") or 0
    if jobs30 >= 10:
        parts.append((f"{jobs30} jobs posted in 30 days", 25))
    elif jobs30 >= 3:
        parts.append((f"{jobs30} jobs posted in 30 days", 15))
    else:
        parts.append((f"{jobs30} jobs posted in 30 days", 5))
    if sdr_posts > 1:
        parts.append((f"{sdr_posts} SDR/BDR posts at once", 15))
    tools = set(c.get("technology_slugs") or []) & ICP["outbound_tools"]
    if tools:
        parts.append(("already pays for " + "/".join(sorted(tools)), 10))
    else:
        parts.append(("no outbound tools seen", 20))
    if c.get("last_funding_round_date") and c["last_funding_round_date"] >= str(dt.date.today() - dt.timedelta(days=365)):
        parts.append(("funded in the last year", 10))
    if c.get("industry") in ICP["excluded_industries"]:
        parts.append((f"{c['industry']}: excluded", -60))
    total = max(0, min(100, sum(v for _, v in parts)))
    return total, ", ".join(f"{k} {v:+d}" for k, v in parts)


def route(total, emp):
    if total < 40:
        return "Nurture"
    return "AE Mid-market" if emp >= 50 else "SDR"


def contact_target(emp):
    if emp < 30:
        return "Founder or CEO"
    if emp < 100:
        return "Head of Sales or VP Sales"
    return "VP Sales, then Sales Development Manager"


def opener(c, job):
    posted = job["date_posted"]
    return (f"Saw {c['name']} posted a {job['job_title']} role on {posted}. "
            "A new SDR usually spends the first month building lists and a sending setup before booking anything. "
            "I build that part so they start on calls. Want me to sketch what I'd set up first?")


def ensure_props():
    hs.ensure_property("companies", "gtm_signal", "GTM signal", "string", "text")
    hs.ensure_property("companies", "gtm_signal_date", "GTM signal date", "date", "date")
    hs.ensure_property("companies", "gtm_signal_url", "GTM signal URL", "string", "text")
    hs.ensure_property("companies", "gtm_fit_score", "GTM fit score", "number", "number")
    hs.ensure_property("companies", "gtm_fit_reason", "GTM fit reason", "string", "textarea")
    hs.ensure_property("companies", "gtm_route", "GTM route", "enumeration", "select",
                       ["AE Enterprise", "AE Mid-market", "SDR", "Nurture"])
    hs.ensure_property("companies", "gtm_contact_target", "GTM contact target", "string", "text")
    hs.ensure_property("companies", "gtm_opener", "GTM drafted opener", "string", "textarea")


def find_company(domain):
    r = hs.call("POST", "/crm/v3/objects/companies/search", {
        "filterGroups": [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": domain}]}],
        "properties": ["domain", "gtm_signal_date"], "limit": 1})
    return r["results"][0] if r["results"] else None


def main():
    seen = load_seen()
    jobs = pull_jobs(seen)
    by_company = {}
    for j in jobs:
        by_company.setdefault(j["company_object"]["domain"].lower(), []).append(j)

    if APPLY:
        ensure_props()
    rows, created, updated, contacts = [], 0, 0, 0
    for domain, js in by_company.items():
        js.sort(key=lambda j: j["date_posted"], reverse=True)
        job, c = js[0], js[0]["company_object"]
        total, why = score(c, len(js))
        emp = c.get("employee_count") or 0
        props = {
            "name": c["name"], "domain": domain, "numberofemployees": str(emp),
            "gtm_signal": f"Hiring: {job['job_title']}", "gtm_signal_date": job["date_posted"],
            "gtm_signal_url": job.get("final_url") or job.get("url") or "",
            "gtm_fit_score": str(total), "gtm_fit_reason": why, "gtm_route": route(total, emp),
            "gtm_contact_target": contact_target(emp), "gtm_opener": opener(c, job),
        }
        rows.append({"company": c["name"], "domain": domain, "employees": emp, "job": job["job_title"],
                     "posted": job["date_posted"], "score": total, "route": props["gtm_route"],
                     "contact_target": props["gtm_contact_target"], "reason": why})
        if APPLY:
            existing = find_company(domain)
            if existing:
                hs.call("PATCH", f"/crm/v3/objects/companies/{existing['id']}", {"properties": props})
                co_id, updated = existing["id"], updated + 1
            else:
                co_id = hs.call("POST", "/crm/v3/objects/companies", {"properties": props})["id"]
                created += 1
            for h in job.get("hiring_team") or []:  # named by TheirStack: attach as a contact
                first, _, last = (h.get("full_name") or "").partition(" ")
                if not first:
                    continue
                ct = hs.call("POST", "/crm/v3/objects/contacts", {"properties": {
                    "firstname": first, "lastname": last, "jobtitle": h.get("role") or "",
                    "hs_linkedin_url": h.get("linkedin_url") or ""}})
                hs.associate([(ct["id"], co_id)])
                contacts += 1
        seen.update(j["id"] for j in js)

    rows.sort(key=lambda r: -r["score"])
    stamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M")
    os.makedirs(os.path.join(HERE, "runs"), exist_ok=True)
    summary = {"run": stamp, "applied": APPLY, "jobs_paid_for": len(jobs), "companies": len(rows),
               "created": created, "updated": updated, "contacts_attached": contacts,
               "routes": {r: sum(1 for x in rows if x["route"] == r) for r in ("AE Mid-market", "SDR", "Nurture")},
               "accounts": rows}
    json.dump(summary, open(os.path.join(HERE, "runs", f"run-{stamp}.json"), "w"), indent=1)
    if APPLY:
        save_seen(seen)
    print(json.dumps({k: v for k, v in summary.items() if k != "accounts"}, indent=1))
    for r in rows:
        print(f"{r['score']:>3} {r['route']:<13} {r['company'][:28]:<28} {r['employees']:>4}  {r['job'][:40]}")


if __name__ == "__main__":
    main()
