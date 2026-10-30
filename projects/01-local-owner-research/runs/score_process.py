"""Score whole-process runs (round 2 on): one answer per company.

Outcomes: CORRECT (an accepted owner, or the owning company where a logged correction says so),
WRONG (a confident name that is not), ABSTAIN ("not enough evidence"). Accuracy is CORRECT over
companies; the wrong-answer rate is reported next to it, because a process that abstains is safer
than one that guesses.

Usage: python score_process.py <name> raw-A.json [raw-B.json ...]
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import score  # noqa: E402  (reuses the same name matching and ground truth)

HERE = Path(__file__).parent


def outcome(r: dict) -> str:
    # Agents sometimes annotate: "Rob (last name not found)". Score the name, not the note.
    name = re.sub(r"\s*\([^)]*\)", "", r.get("owner_name") or "").strip() or None
    if not name or r.get("confidence") == "not enough evidence":
        return "ABSTAIN"
    if score.matches(r["company_id"], name):
        return "CORRECT"
    # First name only, and it is an accepted owner's first name: not a full name, so not
    # correct, but not a wrong person either. Added at the holdout, logged in the case study.
    t = score.tokens(name)
    if len(t) == 1 and any(t[0] == first or first.startswith(t[0]) for first, _ in score.accepted(r["company_id"])):
        return "PARTIAL"
    return "WRONG"


def main(name: str, files: list[str]):
    rows = []
    for f in files:
        rows += json.loads((HERE / f).read_text())
    rows.sort(key=lambda r: r["company_id"])
    lines = [f"# {name} (whole process)", "", "| Company | Tier | Answer | Evidence | Outcome |", "|---|---|---|---|---|"]
    counts = {"CORRECT": 0, "WRONG": 0, "ABSTAIN": 0, "PARTIAL": 0}
    searches = fetches = 0
    for r in rows:
        t = next(x for x in score.TRUTH if x["id"] == r["company_id"])
        o = outcome(r)
        counts[o] += 1
        searches += int(r.get("searches") or 0)
        fetches += int(r.get("fetches") or 0)
        ans = r.get("owner_name") or "not enough evidence"
        ev = (r.get("evidence_url") or "-")[:60]
        lines.append(f"| {t['business']} | {t['tier']} | {ans} | {ev} | {o} |")
    n = len(rows)
    lines += [
        "",
        f"**Accuracy:** {counts['CORRECT']}/{n} = {100 * counts['CORRECT'] / n:.0f}%",
        f"**Wrong answers:** {counts['WRONG']}/{n}  ·  **Abstained:** {counts['ABSTAIN']}/{n}  ·  **First name only:** {counts['PARTIAL']}/{n}",
        f"**Precision (correct when it answered):** "
        + (f"{counts['CORRECT']}/{counts['CORRECT'] + counts['WRONG']}" if counts["CORRECT"] + counts["WRONG"] else "n/a"),
        f"**Searches:** {searches}  ·  **Page fetches:** {fetches}",
    ]
    out = "\n".join(lines) + "\n"
    (HERE / f"{name}-scores.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
