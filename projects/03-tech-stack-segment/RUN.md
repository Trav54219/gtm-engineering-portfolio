# Reproduce the hand check for 3 domains

This guide reproduces the evidence behind the 25-row hand check in README.md for three domains, then shows how to turn it into a verdict. It takes about 5 minutes. The clock starts after you clone the repo and `cd` into it, and the installs are inside the 5 minutes.

Notice: `evidence.py` sends live requests (DNS lookups and one homepage fetch) to three third-party sites: tenonhq.com, freestonecapital.com and factory.ai.

## What you need

- macOS with Python 3.9 or newer. Check with `python3 --version`. The author ran 3.12.
- `dig`, the DNS lookup tool. It ships with macOS. Check with `command -v dig`; it should print `/usr/bin/dig`.
- Network access.
- One Python package, `curl_cffi`, installed below.
- The input file `projects/03-tech-stack-segment/hand_check_3.csv`, already in the repo. Its header line is `domain,pass,Tech Stack`, so it has three columns: `domain`, `pass` and `Tech Stack`. The values come from `hand_check_25.csv` (`pass` is `lite` or `deep`; `Tech Stack` is what the tool reported, called `techsight_said` there).

## Steps

Run these from the repo root. The virtual environment goes in a temp folder so nothing new lands in the repo.

```
cd projects/03-tech-stack-segment
python3 -m venv "${TMPDIR:-/tmp}/p3venv"
source "${TMPDIR:-/tmp}/p3venv/bin/activate"
pip install curl_cffi
mkdir -p "${TMPDIR:-/tmp}/p3ev"
python scripts/evidence.py hand_check_3.csv "${TMPDIR:-/tmp}/p3ev"
python scripts/markers.py hand_check_3.csv "${TMPDIR:-/tmp}/p3ev"
cat "${TMPDIR:-/tmp}/p3ev/tenonhq.com.txt"
```

`evidence.py` prints one line per domain: the domain, the HTTP status, and the length of the homepage HTML. It also writes `<domain>.txt` and `<domain>.html` into the evidence folder. Expect three lines with status 200 and a few seconds of run time. The `pip install` step may end with a notice that a new pip release is available. That is normal and safe to ignore. The last command prints the whole tenonhq.com evidence file. DNS returns the TXT lines in a varying order, and `dig` can drop a line, so the `linkedin-site-verification` line may be missing on one run. If it is, rerun the `evidence.py` line.

The `markers.py` header line also shows an `html=` length, and for freestonecapital.com it was 45426 where `evidence.py` printed 45444. The cause is line endings. `evidence.py` prints the length of the page as fetched, which had 18 Windows-style `\r\n` line endings. `markers.py` reads the saved file back in text mode, which turns each `\r\n` into `\n`, so it counts 18 fewer characters. The other two pages have no `\r`, so their numbers match. A small difference like this is expected.

`markers.py` prints, for each domain, the tool's answer (`techsight:`) and a list of vendor markers found in the evidence (`markers  :`). In `HubSpot[dns]`, `dns` means the marker is in the DNS records and `html4` means it appears 4 times in the homepage. `dns+html4` means both.

## Words you need

- DNS TXT record: a line of text a company publishes about its domain. It is used for email settings and for proving ownership to vendors.
- SPF: a TXT record starting `v=spf1` that lists which services may send email as the company. An `include:` for a vendor means that vendor sends mail for them.
- MX record: says which service receives the company's email (for example Google or Microsoft).
- Verification record: a TXT record such as `linkedin-site-verification=...` or `klaviyo-site-verification=...`. A vendor asks the company to publish it to prove it owns the domain.

## Scope

Only sales and marketing tools count: CRM, marketing automation, email marketing, chat, visitor identification and ad pixels. Analytics and hosting hits in the printout (Google Tag Manager, WordPress, Next.js, Webflow, Microsoft 365, Apple verification) are out of scope. Ignore them.

## Verdicts

Score each row against what the tool listed in `Tech Stack`, in scope only.

- Right: every tool listed is backed by evidence, and no in-scope tool with clear evidence was left out.
- Missed: what it listed is right, but it left out a tool that has clear evidence.
- Wrong: it listed a tool that is not there.
- Unconfirmed: the claim rests on evidence you cannot check either way. A bot wall (a page that returns status 202 or an empty page) with no DNS evidence is also unconfirmed.

What counts as evidence:

- A vendor script or pixel loaded by the page (`hs-scripts.com`, `snap.licdn.com`).
- An SPF `include:` for the vendor (`hubspotemail.net`, `servers.mcsv.net`).
- A DNS record that points a company subdomain at the vendor (for example a `go.` CNAME to HubSpot).
- When the page is hidden by a bot wall, DNS evidence still counts.

What does not count:

- A vendor name in page copy, such as a customer logo or a blog post. Example: tenonhq.com mentions "Tenon vs Pardot" in an article, which does not mean they use Pardot.
- Part of a filename. A "zoho" in an image filename on lightning.ai is not Zoho.
- A verification record. It shows the company has an account with that vendor. It never proves an on-page product such as a tag or pixel. So `klaviyo-site-verification` supports "uses Klaviyo", but `linkedin-site-verification` does not support "LinkedIn Insight Tag", because that needs the tag on the page.
- A `<name>.my.salesforce.com` login page that exists. It could belong to anyone with that name. For factory.ai it is the only evidence for Salesforce, so that row is unconfirmed.

One thing does count even though it looks like a link: a help-center link to the vendor counts as use of that vendor. Example from the 25-row check: posh.vip in `hand_check_25.csv` runs its help center on `intercom.help`, so Intercom counted as a missed tool.

## Worked example: tenonhq.com

The row in `hand_check_25.csv`: the tool said "HubSpot, LinkedIn Insight Tag", my verdict was wrong, and the note was: HubSpot right (go. CNAME to HubSpot); "LinkedIn Insight Tag" came from a linkedin-site-verification TXT record, not a tag; no tag on the page.

How to get there from the printout:

1. The tool listed two tools. Check each.
2. HubSpot: the markers show `HubSpot[dns]`, and the SPF line in the `.txt` file includes `22753661.spf08.hubspotemail.net`. That is evidence. HubSpot is right. (The `go.` CNAME is a DNS record on a subdomain that this script does not collect; it is what the original check used.)
3. LinkedIn Insight Tag: the `.txt` file has `linkedin-site-verification=...`, and the `markers.py` line has no `LinkedIn Insight` entry, because there is no `snap.licdn.com` in the page. A verification record does not prove a tag. You can confirm with `grep -c snap.licdn "${TMPDIR:-/tmp}/p3ev/tenonhq.com.html"`, which prints 0. `grep -c` exits with code 1 when the count is 0, so the shell may show a non-zero exit status here. That is the expected result, not an error.
4. One listed tool is not there, so the verdict is wrong.

Note the Pardot marker (`Pardot[html4]`) is page copy from the article, so it is not a missed tool.

## Try the other two

- freestonecapital.com (expected verdict: missed). Salesforce shows in SPF, so it is right. The `HubSpot[html1]` marker comes from the HubSpot WordPress plugin loading `js-na2.hs-scripts.com`. The tool did not list HubSpot, so it missed one. The other listed tools are not scored. OneTrust (cookie consent), DocuSign (e-signature) and Dropbox (file storage) are outside the sales and marketing scope, and WordPress is a hosting tool, so none of them count for or against the tool.
- factory.ai (expected verdict: unconfirmed). Salesforce appears nowhere in the markers. The only support is `factory.my.salesforce.com` existing, and a word like "factory" could be any company.
- Next row to try on your own: coram.ai, which should score right (HubSpot from SPF). Copy its row from `hand_check_25.csv` into a new CSV with the same three columns (`techsight_said` becomes `Tech Stack`) and rerun the steps.

## When your output differs from the 10-30 hand check

The checks hit live sites and live DNS, so today's output can differ from the original. Do not expect identical numbers. Sites change, bot walls appear, and `dig` sometimes drops answers. Check the stable signals first: the `linkedin-site-verification` record is present for tenonhq.com, and `snap.licdn.com` is absent from its HTML. If a status is not 200 or a page is empty, score from DNS alone and mark unconfirmed if DNS cannot settle it. If a DNS section is empty, rerun the script once.
