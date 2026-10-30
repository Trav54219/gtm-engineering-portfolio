"""Pass one: titles only. Subreddit search via treg (Reddit 403s this machine's direct requests).

Writes scan.json (raw posts) and scan.md (score, comments, date, title, link), newest window only.
"""
import json
import subprocess
import time
from datetime import datetime, timezone

SUBS = ["CleaningBusiness", "sweatystartup", "smallbusiness"]
QUERIES = {
    "CleaningBusiness": ["commercial contracts", "commercial accounts", "bids", "lowball", "finding clients", "lost contract", "walkthrough"],
    "sweatystartup": ["commercial cleaning", "janitorial"],
    "smallbusiness": ["commercial cleaning", "janitorial contract"],
}
WINDOW_DAYS = 90
now = datetime.now(timezone.utc)
posts = {}
n = 0
for sub in SUBS:
    for q in QUERIES[sub]:
        n += 1
        out = subprocess.run(
            ["python3", "/Users/travis/gtm-skills/utils/treg_call.py", "scrapecreators.x.v1-reddit-subreddit-search",
             "--query", f"subreddit={sub}", "--query", f"query={q}", "--query", "sort=top", "--query", "timeframe=year",
             "--job", f"p4-scan-{n}"],
            capture_output=True, text=True,
        ).stdout
        try:
            body = json.loads(out[out.index("{"):])
            body = body.get("result", body.get("body", body))
            got = body.get("posts", [])
        except Exception:
            print("FAILED", sub, q, out[:200])
            continue
        print(sub, q, len(got))
        for p in got:
            p["_query"] = f"{sub}: {q}"
            posts.setdefault(p["id"], p)
        time.sleep(0.5)

json.dump(list(posts.values()), open("scan.json", "w"), indent=1)
rows = []
for p in posts.values():
    d = datetime.fromisoformat(p["created_at_iso"].replace("Z", "+00:00"))
    age = (now - d).days
    rows.append((age, p))
rows.sort(key=lambda r: -r[1]["score"])
with open("scan.md", "w") as f:
    f.write(f"| in window | score | comments | date | sub | title | link |\n|---|---|---|---|---|---|---|\n")
    for age, p in rows:
        f.write(f"| {'yes' if age <= WINDOW_DAYS else 'no (' + str(age) + 'd)'} | {p['score']} | {p['num_comments']} | {p['created_at_iso'][:10]} | {p['subreddit']} | {p['title'].replace('|', '/')} | {p['url']} |\n")
print("unique posts", len(posts), "in window", sum(1 for a, _ in rows if a <= WINDOW_DAYS))
