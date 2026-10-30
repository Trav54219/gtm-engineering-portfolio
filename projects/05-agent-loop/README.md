# Project 5: an agent loop that checks itself

**One small task, built by one agent and graded by another that never saw the builder's notes.**
Cycle 1 scored 4.33 out of 5 and passed. The Checker still found three gaps the Maker didn't
flag. Cycle 2 fixed them and scored 4.67. I approved the plan and the ship separately, and the
loop opened [PR #1](https://github.com/Trav54219/gtm-engineering-portfolio/pull/1) without
merging it.

## The task and the rubric

Task: write `projects/03-tech-stack-segment/RUN.md`, a guide that lets a stranger with a fresh
clone rerun the Project 3 hand check on 3 domains and score each row right, missed, wrong or
unconfirmed in 5 minutes or less.

Rubric, each line scored 1 to 5. Pass = average 4.0 or more, no line below 3, at most 3 cycles.

1. **Runs as written.** Every command, copied in order from a fresh clone, exits 0 and produces
   what the guide says it will. Proved by real command output, not a claim.
2. **No hidden prerequisites.** Every tool, package, version and input file is named with its
   install command before it's used.
3. **The verdict step is learnable.** Plain definitions, a list of what does not count as
   evidence, and one worked example that matches a row in `hand_check_25.csv` exactly. A stranger
   should score a new row the same way I did.

## Who did what

| Role | Who | Boundary |
|---|---|---|
| Goal, rubric, grill answers, yes #1 (plan), yes #2 (ship) | me | |
| Planner | agent | read and write only; wrote the plan and 13 grill questions |
| Maker | agent | built in its own branch `wt/p5-run-guide-hand-check`, never touched main |
| Prover | agent | followed RUN.md in a fresh clone and pasted real output |
| Checker | agent, different model | no shell, never shown the Maker's notes, scored file and line evidence, took the lower score when unsure |
| Shipper | agent | pushed and opened the PR only after yes #2; never merges |

I also re-ran the gate myself each cycle (`run-record/GATE.txt`), so the Checker wasn't trusting
output the Maker pasted.

## Score sheet

| Dimension | Cycle 1 | Cycle 2 |
|---|---|---|
| Runs as written | 5 | 5 |
| No hidden prerequisites | 4 | 5 |
| The verdict step is learnable | 4 | 4 |
| **Average** | **4.33 (pass)** | **4.67 (pass)** |

Proof both cycles: a fresh clone, every command exit 0 (the one `grep -c` exits 1 on a zero
count, which the guide now says is expected), 4 seconds then 3 seconds including the install,
Python 3.12.14. Full output in `run-record/PROOF-cycle*.txt`.

## What the Checker caught that the Maker missed

The Maker reported cycle 1 as done with a clean dry run. The Checker, working only from the
artifact and the Prover's output, docked "no hidden prerequisites" and "the verdict step is
learnable" for things a stranger would trip on:

- Two normal outputs look like failures: pip's "new release available" notice, and `grep -c`
  exiting 1 when it counts zero.
- The same page reported two sizes, 45,444 in one script and 45,426 in the other, with no
  explanation. In cycle 2 the Maker traced it instead of guessing: the second script reads the
  saved file back, which turns 18 Windows line endings into plain ones.
- The freestonecapital.com example skipped three tools in its list (OneTrust, DocuSign,
  Dropbox), so a stranger couldn't see that out-of-scope tools aren't scored.
- The input file's header line wasn't shown.

All four were fixed in cycle 2. "No hidden prerequisites" went from 4 to 5. The verdict step
stayed at 4: the Checker still wants a worked "right" example and a way to check one DNS record
the script doesn't collect. Both are logged in `run-record/CYCLE_LOG.md` and not built. I stopped
at two passes.

The grill was useful too. The Planner found a contradiction in my own hand-check rules: a
LinkedIn verification record counted as wrong evidence for the LinkedIn tag, while a Klaviyo
verification record counted toward a Klaviyo miss. The rule I wrote down to settle it: a
verification record proves an account with that vendor, never a tag on the page.

## Setup, honestly

The official loop-engineer plugin needs Bun, no-mistakes, tasks-axi and treehouse. None of those
are on my Mac, and I didn't install them. I ran the same loop with my own local version: the five
role agents as Claude Code subagents, git worktrees instead of treehouse, and `gh` for the PR.
Same roles, same blind Checker, same two yeses. Run times for the agents weren't measured, and
neither was cost.

## Files

- `run-record/HARNESS.md`: goal, rubric, scope, gate, the grill answers and when I approved them.
- `run-record/PLAN.md`, `run-record/BRIEF.md`: the Planner's output, including the 13 grill questions.
- `run-record/CYCLE_LOG.md`: both cycles, every score with file and line evidence.
- `run-record/GATE.txt`: my own re-run of the gate (cycle 2).
- `run-record/PROOF-cycle1.txt`, `run-record/PROOF-cycle2.txt`: the Prover's real output.
- `run-record/PROGRESS.md`: the Maker's notes, which the Checker was never shown.
- The deliverable itself: [PR #1](https://github.com/Trav54219/gtm-engineering-portfolio/pull/1), open, not merged.

## Post (Legion community)

> **Task:** a RUN.md that lets a stranger rerun my tech-stack hand check on 3 domains and score each row in 5 minutes.
> **Rubric (3 lines):** runs as written from a fresh clone; no hidden prerequisites; the verdict step is learnable with one worked example that matches my real check.
> **Cycle 1 score / final score:** 4.33 / 4.67
> **What the checker caught:** a page size reported two ways (45,444 vs 45,426) with no explanation, plus two normal outputs that look like errors. The builder had called it done.
> **Where I'd like feedback:** cycle 1 already passed. Do you stop at the first pass, or run one more cycle on what the checker flagged?
