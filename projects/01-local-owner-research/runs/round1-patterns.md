# Round 1 candidate patterns (written 2026-10-30, before any test)

Variables: `{company}` business name, `{city}` town, `{domain}` website domain (blank when the
business only has a Facebook page), `{category}` what they do.

**Banned sources** (they are the answer key, or copy it): sunbiz.org, opencorporates.com,
bizapedia.com, corporationwiki.com, flcompanies.com, floridacompanieslist.com, companies list sites
that republish state filings. Results from those are discarded before scoring.

| ID | Type | Pattern |
|----|------|---------|
| P01 | domain-anchored | `site:{domain} owner` |
| P02 | domain-anchored | `site:{domain} about OR "our story" OR "meet the"` |
| P03 | domain-anchored | `site:{domain} founder OR president OR "owned and operated"` |
| P04 | direct | `"{company}" owner {city}` |
| P05 | direct | `"{company}" "owned by"` |
| P06 | direct | `"{company}" founder OR president OR CEO` |
| P07 | natural language | `who owns {company} {city} FL` |
| P08 | platform | `"{company}" site:linkedin.com` |
| P09 | platform | `"{company}" site:bbb.org` |
| P10 | platform | `"{company}" site:facebook.com owner` |
| P11 | platform | `"{company}" site:yelp.com` |
| P12 | platform | `"{company}" site:nextdoor.com` |
| P13 | press | `"{company}" {city} owner interview OR news` |
| P14 | phrase | `"{company}" "family owned" OR "locally owned" {city}` |
| P15 | license board | `"{company}" site:myfloridalicense.com` |
| P16 | reviews | `"{company}" reviews "owner" response` |
| P17 | category | `"{company}" {city} {category} owner name` |
| P18 | domain string | `"{domain}" owner` |

## Scoring (fixed before the run)

Each pattern is run once per tuning company. The searching agent never sees the answers; it
returns the owner name it would report (or "not enough evidence"), the URL and the quote.
A script then scores it against `ground-truth/answers.json`:

- **Q (quality), per company:** 5 = names an accepted owner with a quote from the source;
  4 = names an accepted owner, weaker evidence (snippet only); 3 = names a person at the
  company who is not an accepted owner; 2 = finds the company but no person; 1 = nothing,
  the wrong company, or a banned source only.
- **Q for the pattern** = the mean over the tuning companies.
- **C (consistency)** = how many of the tuning companies scored Q 4 or 5, mapped to 1 to 5
  (6/6 = 5, 5/6 = 4, 4/6 = 3, 2-3/6 = 2, 0-1/6 = 1).
- **Class:** PRIMARY at Q ≥ 4 and C ≥ 4; ENRICHMENT at Q ≥ 4 and C ≥ 3; KILL at Q ≤ 2;
  otherwise REVIEW.
- **Wrong answers** (a confident name that is not an accepted owner) are counted separately.
  A process that guesses is worse than one that says "not enough evidence".
