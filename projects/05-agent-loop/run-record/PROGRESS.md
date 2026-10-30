## Phase 1: 3-domain input CSV - COMPLETE
Files: projects/03-tech-stack-segment/hand_check_3.csv
Gate: `python3 -m py_compile .../evidence.py .../markers.py` -> exit 0
PROOF:
  evidence.py then markers.py ran on it: "tenonhq.com 200 94222 / freestonecapital.com 200 45444 / factory.ai 200 233858", markers printed 3 blocks
Commit: 96a91cb - Add 3-row input CSV for the hand-check run guide

## Phase 2: RUN.md - COMPLETE
Files: projects/03-tech-stack-segment/RUN.md
Gate: `test -f RUN.md` -> exit 0; diff-stat main..HEAD lists only projects/03-tech-stack-segment/ files
PROOF:
  RUN.md 91 lines, no em dashes (grep clean)
Commit: 976d02b - Add RUN.md: reproduce the 3-domain hand check and score verdicts

## Phase 3: dry run in fresh clone - COMPLETE
Files: RUN.md
Gate: commands extracted from RUN.md run with bash -e in fresh clone, exit 0, 4.1s (python 3.12.14, curl_cffi 0.17.0, dig /usr/bin/dig)
PROOF:
  Same 3 status lines and markers as above. Difference found: in the clone run the linkedin-site-verification TXT line was missing from `head -8` (dig order/drop drift). Fixed: guide now cats the whole file and says to rerun if the line is absent.
  Script edits: none. Scope stayed in projects/03-tech-stack-segment/.
Note: worked example says HubSpot evidence is the SPF hubspotemail.net include; the go. CNAME from the CSV note is not collected by evidence.py (stated in RUN.md).
Commit: ef9922c - RUN.md: show full evidence file, note TXT order drift

## Cycle 2 fix: RUN.md checker items - COMPLETE
Files: projects/03-tech-stack-segment/RUN.md
Gate: fresh clone of the branch, steps from RUN.md rerun -> exit 0
PROOF:
  tenonhq.com 200 94222 / freestonecapital.com 200 45444 / factory.ai 200 233858
  markers html=: 94222 / 45426 / 233858. Cause verified: freestonecapital.com html has 18 \r (45444-18=45426); markers.py read_text() turns \r\n into \n. Other two have 0 \r.
  grep -c snap.licdn tenonhq.com.html -> prints 0, exit 1 (documented as expected). pip printed "new release available" notice (documented as ignorable).
  hand_check_3.csv header: domain,pass,Tech Stack. No em dashes. No script edits.
Commit: see git log - RUN.md: explain pip notice, grep exit 1, html length gap, out-of-scope tools
Note: trailer uses Co-Authored-By: Claude Sonnet 5.5 (per the current attribution instruction); cycle 1 used Opus 5.5.
