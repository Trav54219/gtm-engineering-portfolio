# Project 4: a buyer language brief from Reddit

**The buyer's words, each with a link and a date, turned into five copy lines.** 51 threads
scanned by title, 19 inside a 90-day window, 8 read in full. 19 phrases copied word for word and
checked against the fetched text by script. Spend: about **$0.06**.

The 11pm sentence: *"I sent the emails, did the walkthrough, and still don't have a single
commercial account."*

Method from LeadGrow's [reddit-find](https://github.com/LeadGrowGTM/reddit-find). Reddit returned
403 to every direct request from my machine (old.reddit JSON, with and without a browser
fingerprint), so reddit-find's `discover` and `search` came back empty. That's the "thin result is
not an empty topic" trap the lesson warns about. I kept the tool's two-pass method and
pulled the same data through a paid Reddit endpoint on treg (ScrapeCreators, $0.0019 a call):
`scripts/scan.py` for pass one, one post-and-comments call per HIGH thread for pass two.

## The brief

**Market:** owners of small US commercial cleaning companies trying to win recurring office and
building contracts
**Subreddits:** r/CleaningBusiness, r/sweatystartup, r/smallbusiness
**Threads scanned:** 51 (11 searches), **in window:** 19, **marked HIGH:** 8, **read in full:** 8
**Window:** 90 days (2026-08-01 to 2026-10-30). All 8 read threads are dated 2026-08-12 to 2026-10-22.
**Filter:** HIGH = pain, venting or comparison with more than 50 upvotes or more than 30 comments.
5 met that as written. 3 more (marked HIGH* in `title_scan_90d.md`) have advice or win titles
but 63-81 comments, and I took them for the comments. Every SKIP has its reason in the table.

| Phrase (verbatim) | Type | Thread | Date |
|---|---|---|---|
| "I run emails automatically and literally have not gotten any actual clients…" | pain | [1wncres](https://www.reddit.com/r/cleaningbusiness/comments/1wncres/i_started_my_cleaning_company_in_2022_we_did_370k/) | 2026-09-22 |
| "I have had 1 walkthrough but they said my quote was out of their budget but wouldn’t tell me their budget…." | objection | [1wncres](https://www.reddit.com/r/cleaningbusiness/comments/1wncres/i_started_my_cleaning_company_in_2022_we_did_370k/) | 2026-09-22 |
| "they always jump ship for the next cheapest cleaning company" | objection | [1wncres](https://www.reddit.com/r/cleaningbusiness/comments/1wncres/i_started_my_cleaning_company_in_2022_we_did_370k/) | 2026-09-22 |
| "keep getting rejected for “business name not shown on legitimate assets”" | tool complaint (Google Business Profile) | [1wncres](https://www.reddit.com/r/cleaningbusiness/comments/1wncres/i_started_my_cleaning_company_in_2022_we_did_370k/) | 2026-09-22 |
| "I just started a remote cleaning business and yet to land even one client." | pain | [1wdv73v](https://www.reddit.com/r/cleaningbusiness/comments/1wdv73v/i_started_a_cleaning_business_in_2018_and_did/) | 2026-09-11 |
| "a job can keep you busy for years and you still barely break even once you factor in labour, supplies and travel." | pain | [1wdv73v](https://www.reddit.com/r/cleaningbusiness/comments/1wdv73v/i_started_a_cleaning_business_in_2018_and_did/) | 2026-09-11 |
| "we have some commercial leads come in but not many." | pain | [1wdv73v](https://www.reddit.com/r/cleaningbusiness/comments/1wdv73v/i_started_a_cleaning_business_in_2018_and_did/) | 2026-09-11 |
| "My commercial cleaning calculator seems to be pricing way too low" | tool complaint | [1w0b0un](https://www.reddit.com/r/cleaningbusiness/comments/1w0b0un/need_help_quoting_first_commercial_cleaning_job/) | 2026-08-28 |
| "Use Claude and its giving me some low numbers..." | tool complaint | [1w0b0un](https://www.reddit.com/r/cleaningbusiness/comments/1w0b0un/need_help_quoting_first_commercial_cleaning_job/) | 2026-08-28 |
| "i've been stressing out because I have the walk through tommorow" | trigger (walkthrough booked) | [1w0b0un](https://www.reddit.com/r/cleaningbusiness/comments/1w0b0un/need_help_quoting_first_commercial_cleaning_job/) | 2026-08-28 |
| "then you get call saying you're double the price of the company they went with." | objection | [1w0b0un](https://www.reddit.com/r/cleaningbusiness/comments/1w0b0un/need_help_quoting_first_commercial_cleaning_job/) | 2026-08-28 |
| "We do this 3 more times and I feel like I have a legitimate business." | trigger (first recurring contract) | [1vmg7rs](https://www.reddit.com/r/cleaningbusiness/comments/1vmg7rs/just_closed_my_first_recurring_commercial/) | 2026-08-12 |
| "it’s way more than I had by doing google ads, door to door and email marketing." | tool complaint | [1vmg7rs](https://www.reddit.com/r/cleaningbusiness/comments/1vmg7rs/just_closed_my_first_recurring_commercial/) | 2026-08-12 |
| "I have 2 more walk throughs in the next 2 weeks" | trigger | [1vmg7rs](https://www.reddit.com/r/cleaningbusiness/comments/1vmg7rs/just_closed_my_first_recurring_commercial/) | 2026-08-12 |
| "Cap. No daycare is paying 600 per week to clean 2x a week." | objection | [1vmg7rs](https://www.reddit.com/r/cleaningbusiness/comments/1vmg7rs/just_closed_my_first_recurring_commercial/) | 2026-08-12 |
| "I get calls and emails asking to clean our office all the time." | objection (from a buyer) | [1wnjwop](https://www.reddit.com/r/smallbusiness/comments/1wnjwop/how_to_resurrect_my_dads_20_year_old_company/) | 2026-09-22 |
| "nobody hires a cleaner on the first visit." | objection | [1wnjwop](https://www.reddit.com/r/smallbusiness/comments/1wnjwop/how_to_resurrect_my_dads_20_year_old_company/) | 2026-09-22 |
| "I ended all of it as it was getting too expensive." | tool complaint (ad agencies) | [1xcaza0](https://www.reddit.com/r/cleaningbusiness/comments/1xcaza0/im_getting_ready_to_relaunch_my_cleaning_business/) | 2026-10-22 |
| "More of a guess, really." | pain (pricing a bid) | [1x9ec0a](https://www.reddit.com/r/cleaningbusiness/comments/1x9ec0a/brand_new_to_this/) | 2026-10-18 |

Typos and punctuation are left as posted. No usernames.

## Five copy lines

1. Running emails and still "have not gotten any actual clients"?
   Source: [1wncres](https://www.reddit.com/r/cleaningbusiness/comments/1wncres/i_started_my_cleaning_company_in_2022_we_did_370k/), 2026-09-22
2. The office manager you're emailing gets "calls and emails asking to clean our office all the time." What would make yours the one they answer?
   Source: [1wnjwop](https://www.reddit.com/r/smallbusiness/comments/1wnjwop/how_to_resurrect_my_dads_20_year_old_company/), 2026-09-22
3. Last walkthrough end with "out of their budget but wouldn't tell me their budget"?
   Source: [1wncres](https://www.reddit.com/r/cleaningbusiness/comments/1wncres/i_started_my_cleaning_company_in_2022_we_did_370k/), 2026-09-22
4. Tried "google ads, door to door and email marketing" and still short on walkthroughs?
   Source: [1vmg7rs](https://www.reddit.com/r/cleaningbusiness/comments/1vmg7rs/just_closed_my_first_recurring_commercial/), 2026-08-12
5. Three more recurring contracts and you'd "have a legitimate business"?
   Source: [1vmg7rs](https://www.reddit.com/r/cleaningbusiness/comments/1vmg7rs/just_closed_my_first_recurring_commercial/), 2026-08-12

## Who is missing from this data

The buyer. Office and facility managers who hire cleaners don't post in these subreddits; the one
buyer-side line here ("calls and emails asking to clean our office all the time") is a single
small business owner in r/smallbusiness. Established janitorial firms with a sales team are missing too. The
posters skew to owners in their first year, two of the eight threads are mostly residential, and
a good share of the comments are vendors and coaches pitching software or calls. I left their
lines out. Pass two also only saw the first page of comments (22 to 25 per thread), not all of
them. I haven't checked any phrase against a sales call or a customer yet.

## What I'd note for anyone running this

- **A direct 403 looks exactly like "no subreddits found".** The tool printed "Try a broader
  topic" for every query. Reddit was blocking the machine, and the topic wasn't empty. Check the
  raw response before widening the search.
- **The 90-day window is thin in a niche this small.** 19 of 51 threads were inside it, and only 5
  met the HIGH rule as written. The strongest pain titles ("Lost our biggest customer", 244
  upvotes; "Why has commercial cleaning become the spammiest industry", 156 days old) were outside it. I
  kept the window and said so, and didn't stretch it.
- **My first scan run parsed nothing and still cost $0.02.** The wrapper returns `result`, not
  `body`. Fixed and re-run; the wasted 11 calls are in the total.

## Files

- `title_scan_90d.md`: the 19 in-window threads with HIGH or SKIP and the reason for each.
- `scripts/scan.py`: pass one.
- Not published: the raw thread text.

## Post (Legion community)

> **Market:** owners of small US commercial cleaning companies chasing recurring office contracts
> **Threads read:** 8 in full (51 scanned, 90-day window)
> **Best phrase I found (verbatim):** "I get calls and emails asking to clean our office all the time." (a business owner on the buying side)
> **The copy line it became:** The office manager you're emailing gets "calls and emails asking to clean our office all the time." What would make yours the one they answer?
> **Where I'd like feedback:** only 5 threads met the HIGH rule inside 90 days. In a small niche, do you widen the window or lower the score bar?
