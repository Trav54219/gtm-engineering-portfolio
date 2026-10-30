# HARNESS: p5-run-guide-hand-check

PROFILE=generic
REPO=<repo>
WORKTREE=<worktree>
BRANCH=wt/p5-run-guide-hand-check
RUN_DIRECTORY=<run-dir>

## [TASK]

Write `projects/03-tech-stack-segment/RUN.md`: a guide that lets a stranger with a fresh clone of
this repo reproduce the Project 3 hand-check evidence for 3 domains (`scripts/evidence.py` then
`scripts/markers.py`) and turn the printout into a right / missed / wrong / unconfirmed verdict,
in 5 minutes or less.

## Rubric (each scored 1-5 by the Checker; pass = average >= 4.0 and no line below 3)

1. **Runs as written.** Every command in RUN.md, copied in order from a fresh clone on macOS,
   exits 0 and produces the files or output the guide says it will (proved by the Prover's real
   command output). 5 = all commands run unchanged; 3 = one command needs a fix a stranger could
   guess; 1 = a stranger is stuck.
2. **No hidden prerequisites.** Every tool, package, version and input file the commands need is
   named with the exact install command before it is used (Python version, curl_cffi, dig, the
   3-domain input CSV and its required `domain` and `pass` and `Tech Stack` columns). 5 = nothing
   unlisted; 1 = a stranger hits an error on an unlisted dependency.
3. **The verdict step is learnable.** It defines right / missed / wrong / unconfirmed in plain words,
   names what does NOT count as evidence (a vendor name in page copy, a verification TXT record,
   a `<name>.my.salesforce.com` login that exists), and walks one worked example that matches a
   row in `hand_check_25.csv` exactly. No unexplained jargon (SPF, MX, TXT each explained once).
   5 = a stranger could score a new row the same way I did; 1 = definitions missing.

## Approved scope

1. Create `projects/03-tech-stack-segment/RUN.md`.
2. Allowed: a small input CSV for the 3 example domains under `projects/03-tech-stack-segment/`
   if the guide needs one, and minimal fixes to `scripts/evidence.py` / `scripts/markers.py` only if
   a command can't run as written (e.g. a missing column). No other files.
3. Not in scope: changing README.md numbers, the hand-check CSV, or any other project.

## Gate

- `test -f projects/03-tech-stack-segment/RUN.md`
- `python3 -m py_compile projects/03-tech-stack-segment/scripts/evidence.py projects/03-tech-stack-segment/scripts/markers.py`
- `git diff --stat main..HEAD` touches only files under `projects/03-tech-stack-segment/`.

## Prover

Running-thing goal: the Prover follows RUN.md in a fresh temp clone of the branch and pastes the
real output of each command.

## Grill answers (APPROVED by Travis 2026-10-30 12:08 ET, plan yes #1)

1-2. Use a new `hand_check_3.csv` (domain, pass, Tech Stack copied from hand_check_25.csv). No script edit.
3. Keep tenonhq.com (wrong), freestonecapital.com (missed), factory.ai (unconfirmed). Worked example: tenonhq.com.
4. Live fetch. RUN.md says results can drift from 10-30 and what to check when they do. No frozen snapshot.
5. Rule: a verification TXT record proves the company has an ACCOUNT with that vendor. It never proves an on-page product (a tag or pixel). So `klaviyo-site-verification` supports "uses Klaviyo"; `linkedin-site-verification` does not support "LinkedIn Insight Tag" (that needs the tag on the page).
6. Bot wall with no other evidence = unconfirmed. DNS evidence still counts when the page is hidden.
7. Scope = sales and marketing tools only. Analytics/hosting hits are called out as out of scope.
8. List the false-positive traps actually seen: vendor names in page copy (tenonhq "Tenon vs Pardot"), image filenames (lightning.ai "zoho"), help-center links count as use (posh.vip intercom.help).
9. Clock starts after `git clone` + `cd`; installs are inside the 5 minutes.
10. Prover records the real Python version.
11. Add a one-line notice that evidence.py sends live requests to 3 sites.
12. Fresh clone on this Mac only.
13. venv outside the repo (temp dir). Nothing new committed besides RUN.md and hand_check_3.csv.

All three "Proposed (needs approval)" items in PLAN.md: rejected, out of scope.
