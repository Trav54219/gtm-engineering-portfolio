"""Collect raw evidence for the hand check: DNS TXT, MX and homepage HTML.

Evidence only. The right/missed/wrong call is made by reading it, row by row.
Usage: python evidence.py sample.csv evidence/
"""
import csv
import subprocess
import sys
from pathlib import Path

from curl_cffi import requests

src, out = sys.argv[1], Path(sys.argv[2])
out.mkdir(exist_ok=True)

for row in csv.DictReader(open(src)):
    d = row["domain"]
    txt = subprocess.run(["dig", "+short", "TXT", d], capture_output=True, text=True).stdout
    mx = subprocess.run(["dig", "+short", "MX", d], capture_output=True, text=True).stdout
    try:
        r = requests.get(f"https://{d}", impersonate="chrome", timeout=25)
        html, status = r.text, r.status_code
    except Exception as e:  # dead site is evidence too
        html, status = "", f"error: {e}"
    (out / f"{d}.txt").write_text(f"STATUS {status}\n--- TXT\n{txt}\n--- MX\n{mx}\n")
    (out / f"{d}.html").write_text(html)
    print(d, status, len(html))
