# Cycle log: p5-run-guide-hand-check

## Cycle 1 — 2026-10-30 (commit ef9922c)
Proof: works (PROOF-cycle1.txt: fresh clone, all rc=0, 4 s wall clock incl. venv + pip, Python 3.12.14)
- Runs as written: 5/5 — RUN.md:19-28 block matches what ran; GATE.txt test -f exit=0, py_compile exit=0, outside-scope files: none.
- No hidden prerequisites: 4/5 — RUN.md:9-13 names Python 3.9+, dig, network, CSV columns; curl_cffi installed at RUN.md:23. Docked: pip "upgrade available" notice looks like a warning; `grep -c` exits 1 on 0 matches (RUN.md:78) unexplained; RUN.md:13 says the CSV is "already in the repo" without showing its header line.
- The verdict step is learnable: 4/5 — definitions RUN.md:49-52, non-evidence list RUN.md:61-66, klaviyo vs linkedin verification rule RUN.md:65, TXT/SPF/MX explained RUN.md:36-39, worked example RUN.md:72 matches hand_check_25.csv:11. Docked: html length 45444 (evidence.py) vs 45426 (markers.py) unexplained; RUN.md:68 intercom.help rule not tied to any row in the 3-domain run; freestone walkthrough (RUN.md:85) skips OneTrust, DocuSign, Dropbox so a stranger doesn't see how out-of-scope tools are scored.
Reward: 4.33/5.0 (threshold 4.0)
Verdict: PASS
Weakest: No hidden prerequisites (4/5), tied with The verdict step is learnable (4/5)
Fix target: note pip notice + grep exit 1 are normal; explain the 45444 vs 45426 html length; show the CSV header; walk OneTrust/DocuSign/Dropbox as out of scope in the freestone example; tie or drop the intercom.help rule.
(Entry text written by the Checker; saved to file by the orchestrator because the Checker could not create the file.)

## Cycle 2 — 2026-10-30 (commit 74f7d74)
Proof: works (PROOF-cycle2.txt: fresh clone, all rc=0 except the expected grep exit 1, 3 s incl. install, Python 3.12.14)
- Runs as written: 5/5 — RUN.md:19-28 ran unchanged; GATE.txt test -f exit=0, py_compile exit=0, outside-scope none.
- No hidden prerequisites: 5/5 (was 4) — header `domain,pass,Tech Stack` quoted at RUN.md:13 (matches hand_check_3.csv:1); pip notice explained RUN.md:30; grep -c exit 1 explained RUN.md:80.
- The verdict step is learnable: 4/5 (unchanged score, gaps closed) — html length gap explained RUN.md:32 and confirmed by the Prover; freestone walkthrough RUN.md:87 now scores OneTrust/DocuSign/Dropbox/WordPress as out of scope, matching hand_check_25.csv:13. Still docked: intercom.help paragraph RUN.md:70 points outside the 3-domain run; RUN.md:79 cites a go. CNAME the script doesn't collect; no worked "right" example, only a pointer to coram.ai (RUN.md:89).
Reward: 4.67/5.0 (threshold 4.0)
Verdict: PASS
Weakest: The verdict step is learnable (4/5)
Fix target (optional): tie or drop RUN.md:70; add `dig +short go.tenonhq.com CNAME` so a stranger can verify RUN.md:79.
Orchestrator decision: stop after cycle 2 (PASS twice, 4.33 -> 4.67). Remaining fix target logged, not built.
