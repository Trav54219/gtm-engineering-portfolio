# PLAN.md
## Phases
1. Make the 3-domain input runnable — skill: direct — files: `projects/03-tech-stack-segment/hand_check_3.csv` (new); `scripts/markers.py` / `scripts/evidence.py` only if a command fails as written.
2. Write RUN.md (prereqs, commands, how to read the printout, verdict definitions, worked example) — skill: direct — files: `projects/03-tech-stack-segment/RUN.md`.
3. Dry-run RUN.md in a fresh temp clone and fix wording — skill: direct — files: RUN.md (and the phase 1 files if needed).

Known facts the Maker must use (from reading the files):
- `evidence.py <csv> <outdir>` reads only the `domain` column. For each domain it runs `dig +short TXT`, `dig +short MX`, and one HTTPS GET via curl_cffi (chrome impersonation, 25 s timeout). It writes `<outdir>/<domain>.txt` (STATUS line, `--- TXT`, `--- MX`) and `<domain>.html`, prints `domain status htmllen`. `out.mkdir(exist_ok=True)` has no parents=True, so the outdir parent must exist.
- `markers.py <csv> <outdir>` reads `domain`, `pass`, `Tech Stack`. MISMATCH: `sample_enriched.csv` has `tech_stack` and `found_by` and no `pass` or `Tech Stack`, so markers.py raises KeyError on it. `hand_check_25.csv` has `domain`, `pass`, `techsight_said`, so it also lacks `Tech Stack`. Only evidence.py runs on either file unchanged. Recommended fix: a new 3-row `hand_check_3.csv` with exactly `domain,pass,Tech Stack`, values copied from `hand_check_25.csv` (`pass`) and `techsight_said` (`Tech Stack`). That needs no script edit. Do not edit scripts unless something else breaks.
- Proposed 3 domains, each with a different verdict, all rows in `hand_check_25.csv`: `tenonhq.com` (wrong, deep), `freestonecapital.com` (missed, lite), `factory.ai` (unconfirmed, lite). Worked example in RUN.md: tenonhq.com, copied exactly (techsight said "HubSpot, LinkedIn Insight Tag"; verdict wrong; HubSpot right via go. CNAME, "LinkedIn Insight Tag" came from a linkedin-site-verification TXT record, no tag on page). Right is defined in words and pointed at coram.ai as a row to try next.
- Prereqs to name: macOS, Python 3.9+ (`python3 --version`), `pip3 install curl_cffi` (preferably in a venv: `python3 -m venv .venv && source .venv/bin/activate`), `dig` (ships with macOS; `command -v dig`), network access. Python 3.14 or odd versions: Prover records which version worked.
- Live-data drift: evidence.py hits live sites and DNS, so output today may differ from the 10-30 hand check (bot walls, changed records, dig dropping answers). RUN.md must say what to expect and what a differing result means, and must not claim byte-identical output. Pin expectations to stable signals (the `linkedin-site-verification` TXT record exists, no `snap.licdn.com` in the HTML).

## Mechanical gate
Run from WORKTREE:
- `test -f projects/03-tech-stack-segment/RUN.md`
- `python3 -m py_compile projects/03-tech-stack-segment/scripts/evidence.py projects/03-tech-stack-segment/scripts/markers.py`
- `git diff --stat main..HEAD` lists only files under `projects/03-tech-stack-segment/`.

## Checker Rubric
Artifacts to evaluate: `projects/03-tech-stack-segment/RUN.md`, `projects/03-tech-stack-segment/hand_check_3.csv`, the Prover's pasted output.
Each dimension scored 1-5 by the Checker.
- Runs as written: Every command in RUN.md, copied in order from a fresh clone on macOS, exits 0 and produces the files or output the guide says it will (proved by the Prover's real command output). 5 = all commands run unchanged | 3 = one command needs a fix a stranger could guess | 1 = a stranger is stuck.
- No hidden prerequisites: Every tool, package, version and input file the commands need is named with the exact install command before it is used (Python version, curl_cffi, dig, the 3-domain input CSV and its required `domain` and `pass` and `Tech Stack` columns). 5 = nothing unlisted | 1 = a stranger hits an error on an unlisted dependency.
- The verdict step is learnable: It defines right / missed / wrong / unconfirmed in plain words, names what does NOT count as evidence (a vendor name in page copy, a verification TXT record, a `<name>.my.salesforce.com` login that exists), and walks one worked example that matches a row in `hand_check_25.csv` exactly. No unexplained jargon (SPF, MX, TXT each explained once). 5 = a stranger could score a new row the same way I did | 1 = definitions missing.
PASS threshold: mean >= 4.0 and no line below 3. Max 3 cycles.

Checker note: the 5-minute claim is judged by the Prover's wall-clock for the whole guide.

## Human-judgment dimensions
Dimension 3 needs the user's taste: whether the worked example scores "the way I did". The Checker can compare it to the CSV row text; the user should confirm the "verification TXT record is not a tag" and "login subdomain is not evidence" rules read correctly. Note a tension: the README says a Klaviyo verification record counted as a miss for pax.com and inworld.ai, while a linkedin-site-verification record counted as wrong. RUN.md must state the rule that reconciles these (see Grill).

## Prover
Running-thing goal. In a fresh temp clone of branch `wt/p5-run-guide-hand-check` (e.g. `git clone --branch wt/p5-run-guide-hand-check <repo> $TMP/clone`), with no shared venv, follow RUN.md literally, in order, from the top, using a stopwatch. Paste the real output of each command: Python version, pip install, `command -v dig`, evidence.py run (3 lines: domain status length), `ls` of the evidence dir, markers.py printout, and the head of one `.txt` evidence file. Record exit codes, total wall-clock time, and any difference from what RUN.md predicts. Also state whether `python3 -m py_compile` and the diff-stat gate pass. Do not fix commands silently; report each failure.

## Grill
1. Is the Tech Stack column correct to fill from `techsight_said`? sample_enriched.csv calls it `tech_stack` and has no `pass`; `pass` is `lite` / `deep` only in hand_check_25.csv (and `found_by` is a different value set, e.g. `lite+lite-rerun`). Should RUN.md use hand_check_3.csv, or should markers.py accept both column names (a script edit)? Plan assumes the new CSV, no script edit.
2. Is a new `hand_check_3.csv` acceptable, or must the guide have the stranger build the CSV from existing files? (Scope allows the file.)
3. Which 3 domains? Plan proposes tenonhq.com (wrong), freestonecapital.com (missed), factory.ai (unconfirmed). Do you want a "right" one (coram.ai) instead of one of those?
4. The fixed point: live HTTP and DNS today may not reproduce 10-30 results (bot walls like arbor.co returning 202, 200-worker DNS drops, sites that changed). Is "close enough, here is what to check" an acceptable standard, or do you want a frozen evidence snapshot committed? (Snapshot would add files and defeat the live-fetch purpose.)
5. Verdict rule conflict: a `linkedin-site-verification` TXT record counted as wrong evidence for "LinkedIn Insight Tag", but `klaviyo-site-verification` records counted toward a Klaviyo miss on pax.com (alongside a Klaviyo key on the page) and inworld.ai. Is the rule "a verification record never proves a tag, but it can support a tool only when a second sign agrees"? Please confirm, or the worked example and the miss definition can contradict each other.
6. Where does "unconfirmed" end and "wrong" begin when a bot wall (status 202, empty HTML) hides the page? Plan treats "cannot check either way" as unconfirmed.
7. Does the verdict cover only sales/marketing scope (CRM, marketing automation, email marketing, chat, visitor ID, ad pixels), per the README? Analytics/hosting hits from markers.py (Google Tag Manager, WordPress, Next.js) must be called out as out of scope.
8. markers.py regexes are loose (e.g. `hubspot\.com/` matches page copy; `zoho` matched an image filename on lightning.ai). Should RUN.md list these false-positive traps, or only the three you named?
9. Does "5 minutes" include `pip install` and the clone? Plan counts from `cd` into the repo to final verdict, with install inside the clock.
10. Python version: curl_cffi wheels may lag very new Python releases on macOS. Which Python do you run? The plan names 3.9+ and asks the Prover to record the real version.
11. Network side effects: evidence.py sends live requests to three third-party sites. Fine for a public guide, or should RUN.md add a one-line notice?
12. Gate gap: `git diff --stat main..HEAD` proves scope but nothing mechanical proves the guide runs; only the Prover does. The Prover run is therefore the real gate. Does it need to run on a second machine or only a fresh clone on your Mac?
13. Is a `.venv` inside the repo okay? Plan puts it in a temp location or adds it to the user's shell only, never committed, because scope allows no other files.

## Proposed (needs approval)
- Make markers.py accept `tech_stack` / `techsight_said` / missing `pass` so it runs on `sample_enriched.csv` directly (script edit, out of the "can't run as written" strict reading for the guide's own input).
- Add `.gitignore` entry for `.venv` and `evidence/` (outside the allowed file list).
- Commit a frozen evidence snapshot for reproducibility checks.

## Turn budget
Phase 1: 8 turns. Phase 2: 15 turns. Phase 3: 12 turns. Total 35, plus Prover/Checker cycles (max 3).
