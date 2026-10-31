"""Small HubSpot CRM client: retries 429/5xx, raises on anything else."""
import json
import os
import time
import urllib.error
import urllib.request

BASE = "https://api.hubapi.com"


def _token():
    tok = os.environ.get("HUBSPOT_TOKEN")
    if tok:
        return tok
    env = os.path.expanduser("~/gtm-skills/.env")
    for line in open(env):
        if line.startswith("HUBSPOT_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("HUBSPOT_TOKEN not set")


TOKEN = _token()


class HubSpotError(Exception):
    pass


def call(method, path, body=None, tries=6):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(tries):
        req = urllib.request.Request(
            BASE + path,
            method=method,
            data=data,
            headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            raise HubSpotError(f"{method} {path} -> {e.code}: {e.read()[:300]!r}")
    raise HubSpotError(f"{method} {path}: out of retries")


def list_all(obj, props):
    out, after = [], None
    while True:
        q = f"/crm/v3/objects/{obj}?limit=100&properties={','.join(props)}"
        if obj == "contacts":
            q += "&associations=companies"
        if after:
            q += f"&after={after}"
        r = call("GET", q)
        out += r["results"]
        after = r.get("paging", {}).get("next", {}).get("after")
        if not after:
            return out


def batch(obj, action, inputs):
    """batch/create, batch/update or batch/archive in chunks of 100."""
    results = []
    for i in range(0, len(inputs), 100):
        r = call("POST", f"/crm/v3/objects/{obj}/batch/{action}", {"inputs": inputs[i : i + 100]})
        if r:
            results += r.get("results", [])
    return results


def associate(contact_company_pairs):
    for i in range(0, len(contact_company_pairs), 100):
        chunk = contact_company_pairs[i : i + 100]
        call(
            "POST",
            "/crm/v4/associations/contacts/companies/batch/associate/default",
            {"inputs": [{"from": {"id": c}, "to": {"id": co}} for c, co in chunk]},
        )


def merge(obj, primary_id, other_id):
    return call(
        "POST",
        f"/crm/v3/objects/{obj}/merge",
        {"primaryObjectId": primary_id, "objectIdToMerge": other_id},
    )


def ensure_property(obj, name, label, ptype, field, options=None):
    try:
        call("GET", f"/crm/v3/properties/{obj}/{name}")
        return False
    except HubSpotError as e:
        if "404" not in str(e):
            raise
    group = {"contacts": "contactinformation", "companies": "companyinformation"}[obj]
    body = {"name": name, "label": label, "type": ptype, "fieldType": field, "groupName": group}
    if options:
        body["options"] = [{"label": o, "value": o} for o in options]
    call("POST", f"/crm/v3/properties/{obj}", body)
    return True
