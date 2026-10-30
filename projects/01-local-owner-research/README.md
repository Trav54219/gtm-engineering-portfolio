# Project 1: a research process I can prove

**Goal sentence:** Find the full name of the owner of a local service business.

**Result:** on 4 held-out businesses it named the right owner for **2 (50%)**, gave **zero wrong
names**, and said "not enough evidence" instead of guessing on the two tiny ones. Every large and
mid-size business in the test (6 of 6) came back right, including one that had been quietly bought
by a private-equity rollup. Tiny businesses: 0 of 6 full names. **Below the 90% line, so not
approved**; the limit is written down below.

Built with LeadGrow's [research-process-builder](https://github.com/LeadGrowGTM/research-process-builder).

## Scorecard

| | |
|---|---|
| Goal sentence | Find the full name of the owner of a local service business. |
| Test set | 10 Florida service businesses: 3 large (1,000+ Google reviews), 3 mid (50 to 400), 4 tiny (15 or fewer) |
| Known answers written first | 10, from the Florida corporate registry, timestamped 2026-10-30 10:45 ET, before any run |
| Split | 6 tuning, 4 holdout (1 large, 1 mid, 2 tiny), holdout never looked at while tuning |
| Rounds | 3. Round 1 tested 18 search patterns one at a time; rounds 2 and 3 ran the stacked process |
| Accuracy (tuning) | 50% → 67% → 67% |
| **Holdout (never tuned on)** | **2 of 4 = 50%**, 0 wrong names |
| Run-to-run spread | Same prompt run twice on the holdout: 50% both times. One tiny business moved between "first name only" and "not enough evidence" |
| Precision | 8 of 8: every full name it gave across rounds 2, 3 and the holdout was right |
| Cost per company | $0 in search (Keenable, free). About 28,000 to 39,000 model tokens and 3 searches + 2 page reads per company in the final process. Dollar cost: not measured |
| Killed patterns | 9 of 18: LinkedIn, BBB, Yelp, Facebook, Nextdoor, "owned by", "family owned", the about page and the license board via search. Each scored quality 2 or below across 6 companies |
| What broke | A large plumber had been bought by a PE rollup in Feb 2024. Every search found the founder, from his own press release and LinkedIn, still saying "owner". Fix: step 1 is now an acquisition check, and the answer is the buyer, with the founder as "former owner". Round 2 got it right |
| Human review | See below. Travis's own sign-off: **not done yet** |

## How it was tested

1. **Companies picked by a rule, not by hand.** 674 Florida HVAC, plumbing, roofing, handyman,
   pressure-washing, pool and lawn businesses from a free Maps pull. Tiered by review count,
   shuffled with a fixed seed (20261030), national franchises dropped. Walking the seeded order, a
   business was kept only if exactly one active registry entity matched it and named an owner.
   27 looked at, 10 kept.
2. **Answers from a source the process may not use.** The Florida Division of Corporations
   lists each company's officers. The process is banned from it and from every site that copies
   it (OpenCorporates, Bizapedia and the like), so it can't grade itself.
3. **The searching agent never saw the answers.** Every run was a fresh agent given only the
   process and the business. A separate script scored the output.
4. **Rules fixed before the run**, including what counts as a match. The three changes made
   after seeing results are logged (a two-surname name, the PE sale, "first name only" as its own
   outcome); none of them moved a holdout number.

## What it does well, and where it stops

- **Large and mid businesses: 6 of 6.** The winning sources were the company's own blog, a BBB
  profile, a local college press release, a county newspaper's fictitious-name notice and the
  buyer's acquisition announcement.
- **It doesn't guess.** Zero wrong names after round 1. In round 1, testing patterns one at a
  time, there were 8, all the PE founder.
- **Tiny businesses: 0 of 6 full names.** What was actually out there:
  - one Facebook-only business whose page names a late family member, not the owner
  - one whose Maps listing points to a different company's website (the phone check caught it:
    the site's number didn't match the listing)
  - one website that says "I own and operate…" signed with a first name only
  - nothing else on the open web

  For businesses this small, the honest output is "not enough evidence", and the real fix is a
  source this test banned on purpose: the state registry itself.

## What I'd change for production

Use the state registry as step 1 for tiny businesses (it's the only place their owner is written
down), keep the acquisition check ahead of it so a rollup's manager isn't reported as the owner, and
report "first name only" as its own state so a person can finish it with one call.

## Human review

What I checked by hand: the PE acquisition (buyer's announcement, White Wolf Capital's portfolio
page, Contractor magazine), why each tiny business failed (read every step of each run), and that
no run opened the answer files. What I still don't trust: the registry as ground truth for every
business (an officer isn't always the person running it), and a 4-company holdout, where one
company is 25 points.

## Files

- `process.md`: the final process, paste it into any agent
- `runs/round1-patterns.md`: the 18 patterns and the scoring rules, written before round 1
- `runs/round1-notes.md`: round 1 results, what broke, and the scorer fix
- `results/results.md`: every round and both holdout runs, owner names reduced to initials
- `runs/score.py`, `runs/score_process.py`: the scorers
- `sourcing/sunbiz_truth.py`: how the answer key was built
- Not published: the answer key, raw agent runs and the source lists. They name real
  small-business owners.
