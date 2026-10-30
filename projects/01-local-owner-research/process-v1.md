# find local business owner (v1, round 2 candidate)

Goal: the full name of the owner of a local service business, or the company that owns it,
or "not enough evidence".

## inputs
- `{company}` business name exactly as listed
- `{city}`, `{state}` (state = FL in this test)
- `{domain}` website domain, or blank when the business only has a Facebook page
- `{facebook}` Facebook page URL, if any
- `{category}` what they do

## never use
sunbiz.org and sites that republish state corporate filings (opencorporates, bizapedia,
corporationwiki, flcompanies, floridacompanieslist). They are the answer key in this test.

## steps (stop at the first step that settles it)

1. **Acquisition check.** search `"{company}" acquired OR acquisition OR "joins" OR "partners with"`.
   If a credible source (buyer's site, trade press, deal database) says the business was bought,
   the answer is the BUYER, with the date. Report the founder separately as "former owner".
   Stop.
2. **Leadership search.** search `"{company}" founder OR president OR CEO`.
3. **Owner + town.** search `"{company}" owner {city}`.
4. **The business's own site** (skip if no `{domain}`): search `site:{domain} owner` then
   `site:{domain} founder OR president OR "owned and operated"`.
5. **Category + town.** search `"{company}" {city} {category} owner name`.
6. **Tiny-business sources** (if steps 2-5 found nobody): fetch `{facebook}` (or search
   `"{company}" {city} facebook`) and read the About / Intro; search
   `"{company}" {city} reviews "owner"` and look for owner replies signed with a name.

At each step, before reporting a name: **fetch the page** that names them and copy the exact
sentence. A snippet alone is not enough. If the page says "former", "founded" with a later sale,
or a different company, keep going.

## output
- owner: full name, or the owning company, or "not enough evidence"
- title as the source states it
- evidence_url + exact quote
- confidence: confirmed (2+ independent sources agree) / likely (1 fetched source) /
  not enough evidence
- former_owner: if step 1 found a sale

Never guess. A wrong name costs more than no name.
