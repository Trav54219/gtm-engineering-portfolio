"""Score a round's raw search results against the ground truth.

The searching agent never sees ground-truth/; this script is the only thing that reads both.
Rules are the ones written in round1-patterns.md before the run.

Usage: python score.py <round-name> raw-A.json [raw-B.json ...]
Writes <round-name>-scores.md and prints the summary.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
TRUTH = json.loads((HERE.parent / "ground-truth" / "answers.json").read_text())
BANNED = re.compile(r"sunbiz\.org|opencorporates|bizapedia|corporationwiki|flcompanies|floridacompanieslist", re.I)
SUFFIX = {"jr", "sr", "ii", "iii", "iv"}


def key(name: str | None) -> tuple[str, str] | None:
    if not name:
        return None
    parts = [p for p in re.sub(r"[^a-z ]", " ", name.lower()).split() if p not in SUFFIX]
    parts = [p for p in parts if len(p) > 1] or parts
    if len(parts) < 2:
        return None
    return parts[0], parts[-1]


def tokens(name: str | None) -> list[str]:
    return [p for p in re.sub(r"[^a-z ]", " ", (name or "").lower()).split() if p not in SUFFIX and len(p) > 1]


def accepted(company_id: int) -> set[tuple[str, str]]:
    row = next(t for t in TRUTH if t["id"] == company_id)
    return {k for k in (key(o["name"]) for o in row["accepted_owners"]) if k}


def matches(company_id: int, name: str | None) -> bool:
    """Same first name, and the accepted surname appears in the name given.

    Round 1 fix (logged in round1-notes.md): a two-surname name on the web ("first + both
    surnames") is the registry's "first + first surname"; matching only the LAST word called it wrong.
    """
    row = next(x for x in TRUTH if x["id"] == company_id)
    buyer = row.get("accepted_company_owner")
    if buyer and name and buyer.split()[0].lower() in name.lower():
        return True  # a company owns it (logged correction); naming the buyer is right
    t = tokens(name)
    if len(t) < 2:
        return False
    return any(t[0] == first and last in t[1:] for first, last in accepted(company_id))


def q_score(r: dict) -> int:
    if str(r.get("notes", "")).startswith("skipped") or r.get("result_count") == "skipped":
        return 0  # not run, excluded
    url = r.get("evidence_url") or ""
    if r.get("banned_only") or (url and BANNED.search(url)):
        return 1
    k = key(r.get("owner_name"))
    if matches(r["company_id"], r.get("owner_name")):
        return 5 if r.get("evidence_kind") == "quote" else 4
    if k or r.get("person_not_owner"):
        return 3
    return 2 if r.get("company_found") else 1


def wrong(r: dict) -> bool:
    k = key(r.get("owner_name"))
    return bool(k) and not matches(r["company_id"], r.get("owner_name")) and not (r.get("evidence_url") and BANNED.search(r["evidence_url"]))


def c_score(hits: int, n: int) -> int:
    if n == 0:
        return 0
    share = hits / n
    if share >= 1:
        return 5
    if share >= 5 / 6:
        return 4
    if share >= 4 / 6:
        return 3
    if share >= 2 / 6:
        return 2
    return 1


def classify(q: float, c: int) -> str:
    if q >= 4 and c >= 4:
        return "PRIMARY"
    if q >= 4 and c >= 3:
        return "ENRICHMENT"
    if q <= 2:
        return "KILL"
    return "REVIEW"


def main(name: str, files: list[str]):
    rows = []
    for f in files:
        rows += json.loads((HERE / f).read_text())
    by_pattern = defaultdict(list)
    for r in rows:
        by_pattern[r["pattern"]].append(r)

    lines = [f"# {name} scores", "", "| Pattern | Run on | Q (mean) | Owner found (Q4+) | C | Wrong names | Class |", "|---|---|---|---|---|---|---|"]
    classes = {}
    for p in sorted(by_pattern):
        scored = [(r, q_score(r)) for r in by_pattern[p]]
        scored = [(r, q) for r, q in scored if q > 0]
        n = len(scored)
        q = sum(s for _, s in scored) / n if n else 0
        hits = sum(1 for _, s in scored if s >= 4)
        c = c_score(hits, n)
        w = sum(1 for r, _ in scored if wrong(r))
        cls = classify(q, c) if n else "SKIPPED"
        classes[p] = cls
        lines.append(f"| {p} | {n} | {q:.2f} | {hits}/{n} | {c} | {w} | {cls} |")

    # Per company: did ANY pattern find an accepted owner? (the plain accuracy check)
    by_company = defaultdict(list)
    for r in rows:
        by_company[r["company_id"]].append(r)
    found = {cid: any(q_score(r) >= 4 for r in rs) for cid, rs in by_company.items()}
    tested = len(classes) - sum(1 for c in classes.values() if c == "SKIPPED")
    kept = sum(1 for c in classes.values() if c in ("PRIMARY", "ENRICHMENT"))
    stack = 100 * kept / tested if tested else 0
    plain = 100 * sum(found.values()) / len(found) if found else 0
    total_wrong = sum(1 for r in rows if q_score(r) > 0 and wrong(r))
    lines += [
        "",
        f"**Stack accuracy (repo formula, PRIMARY + ENRICHMENT over patterns tested):** {kept}/{tested} = {stack:.0f}%",
        f"**Plain accuracy (companies where any pattern found an accepted owner):** {sum(found.values())}/{len(found)} = {plain:.0f}%",
        f"**Confident wrong names across all runs:** {total_wrong}",
        "",
        "| Company | Tier | Found by |",
        "|---|---|---|",
    ]
    for cid in sorted(by_company):
        t = next(x for x in TRUTH if x["id"] == cid)
        pats = sorted({r["pattern"] for r in by_company[cid] if q_score(r) >= 4})
        lines.append(f"| {t['business']} | {t['tier']} | {', '.join(pats) or 'none'} |")
    out = "\n".join(lines) + "\n"
    (HERE / f"{name}-scores.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
