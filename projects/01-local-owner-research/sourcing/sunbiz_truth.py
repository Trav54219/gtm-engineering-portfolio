"""Ground truth from Florida's business registry (Sunbiz), gathered BEFORE any test run.

For each candidate business: search Sunbiz by name, keep it only if exactly one ACTIVE
entity clearly matches, then record every officer whose title marks them as the owner
(President, CEO, Owner, Manager, Managing Member, Authorized Member, Chairman).

The research process under test is NOT allowed to use sunbiz.org. That is what makes this
independent ground truth rather than the process grading itself.

Usage: python sunbiz_truth.py shortlist-ordered.csv answers.json
"""

import csv
import json
import re
import sys
import time
import urllib.parse

from curl_cffi import requests
from selectolax.lexbor import LexborHTMLParser as HTMLParser

BASE = "https://search.sunbiz.org"
OWNER_TITLES = re.compile(r"\b(P|PRES|PRESIDENT|CEO|OWNER|MGR|MGRM|MANAGER|AMBR|MGMR|MEMBER|CHAIRMAN|CHAIR|DIRECTOR|D)\b", re.I)
SUFFIX = re.compile(r"\b(llc|l\.l\.c\.|inc|inc\.|corp|corporation|co|company|incorporated)\b\.?", re.I)


def clean_name(name: str) -> str:
    n = re.split(r"[:|]", name)[0]
    n = SUFFIX.sub("", n)
    n = re.sub(r"[^A-Za-z0-9&' ]+", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def squash(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", SUFFIX.sub("", s.lower()))


def get(url: str) -> str:
    for attempt in range(3):
        r = requests.get(url, impersonate="chrome", timeout=30)
        if r.status_code == 200:
            return r.text
        time.sleep(2 + attempt * 3)
    raise RuntimeError(f"{r.status_code} for {url}")


def search(name: str):
    q = clean_name(name)
    order = re.sub(r"[^A-Z0-9]", "", q.upper())
    url = (f"{BASE}/Inquiry/CorporationSearch/SearchResults?inquiryType=EntityName"
           f"&searchNameOrder={urllib.parse.quote(order)}&searchTerm={urllib.parse.quote(q)}")
    doc = HTMLParser(get(url))
    out = []
    for tr in doc.css("table tr"):
        tds = tr.css("td")
        if len(tds) < 3:
            continue
        a = tds[0].css_first("a")
        if not a:
            continue
        out.append({"entity": a.text(strip=True), "href": a.attributes.get("href"), "doc": tds[1].text(strip=True), "status": tds[2].text(strip=True)})
    return q, out


def officers(href: str):
    doc = HTMLParser(get(BASE + href))
    for sec in doc.css("div.detailSection"):
        text = sec.text(separator="\n", strip=True).strip()
        if text.startswith("Officer/Director Detail") or text.startswith("Authorized Person"):
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            people, title = [], None
            for i, l in enumerate(lines):
                m = re.match(r"Title\s+(.+)", l)
                if m:
                    title = m.group(1).strip()
                    if i + 1 < len(lines):
                        last_first = lines[i + 1]
                        if "," in last_first:
                            last, first = [x.strip() for x in last_first.split(",", 1)]
                            full = f"{first} {last}".title()
                        else:
                            full = last_first.title()
                        people.append({"name": full, "title": title})
            return people
    return []


def main(src: str, dst: str):
    rows = list(csv.DictReader(open(src)))
    results = []
    for r in rows:
        q, hits = search(r["name"])
        target = squash(q)
        active = [h for h in hits if h["status"].lower() == "active" and squash(h["entity"]).startswith(target)]
        rec = {**r, "query": q, "matches": [h["entity"] for h in active]}
        if len(active) != 1:
            rec["usable"] = False
            rec["why"] = f"{len(active)} active matches"
        else:
            ppl = officers(active[0]["href"])
            owners = [p for p in ppl if OWNER_TITLES.search(p["title"])]
            rec.update({"entity": active[0]["entity"], "doc_number": active[0]["doc"], "officers": ppl, "owners": owners})
            rec["usable"] = bool(owners)
            if not owners:
                rec["why"] = "no owner-titled officer on file"
        results.append(rec)
        print(r["tier"], "|", r["name"], "|", rec.get("entity", "-"), "|", [o["name"] for o in rec.get("owners", [])], "|", rec.get("why", "ok"))
        time.sleep(1.5)
    json.dump(results, open(dst, "w"), indent=2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
