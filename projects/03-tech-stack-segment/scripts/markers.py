"""Print the GTM-vendor markers in each row's raw evidence, next to what techsight said.

The markers are pointers for the reader, not verdicts: a vendor name in page copy
(a customer logo, a blog post) is not the company using that tool.
"""
import csv
import re
import sys
from pathlib import Path

VENDORS = {
    "HubSpot": r"hs-scripts\.com|js\.hsforms|hsforms\.net|hubspotemail\.net|hs-analytics|js\.hs-banner|hubspot-developer|hubspot\.com/",
    "Salesforce": r"my\.salesforce\.com|force\.com|salesforce\.com/|_spf\.salesforce|exacttarget|sfmc",
    "Pardot": r"pardot|pi\.pardot|go\.pardot|aspmx\.pardot|mcae",
    "Marketo": r"munchkin|marketo|mktoweb|mktdplp|mktocdn",
    "Zoho": r"zoho",
    "Pipedrive": r"pipedrive",
    "ActiveCampaign": r"activecampaign|activehosted",
    "Klaviyo": r"klaviyo",
    "Mailchimp": r"mailchimp|mcsv\.net|list-manage|chimpstatic",
    "Intercom": r"intercom",
    "Drift": r"js\.driftt|drift\.com",
    "Qualified": r"qualified\.com",
    "RB2B": r"rb2b",
    "Apollo": r"apollo\.io|assets\.apollo",
    "ZoomInfo": r"zoominfo|ws\.zoominfo",
    "6sense": r"6sc\.co|6sense",
    "Clearbit": r"clearbit",
    "Segment": r"segment\.com|segment\.io|cdn\.segment",
    "LinkedIn Insight": r"snap\.licdn\.com|px\.ads\.linkedin",
    "Facebook Pixel": r"fbevents\.js|connect\.facebook\.net",
    "Google Tag Manager": r"googletagmanager\.com/gtm",
    "Google Analytics": r"googletagmanager\.com/gtag|google-analytics\.com",
    "Google Workspace (MX)": r"aspmx\.l\.google\.com|googlemail\.com",
    "Microsoft 365 (MX)": r"mail\.protection\.outlook\.com",
    "iCloud Mail (MX)": r"mail\.icloud\.com",
    "Apple verif TXT": r"apple-domain-verification",
    "Mailgun": r"mailgun",
    "Sendgrid": r"sendgrid",
    "Amazon SES": r"amazonses",
    "Webflow": r"webflow",
    "Framer": r"framerusercontent|framer\.com",
    "WordPress": r"wp-content|wp-includes",
    "Next.js": r"/_next/static",
}

sample, ev = sys.argv[1], Path(sys.argv[2])
for row in csv.DictReader(open(sample)):
    d = row["domain"]
    dns = (ev / f"{d}.txt").read_text()
    html = (ev / f"{d}.html").read_text()
    status = dns.splitlines()[0]
    hits = []
    for name, pat in VENDORS.items():
        in_dns = bool(re.search(pat, dns, re.I))
        n_html = len(re.findall(pat, html, re.I))
        if in_dns or n_html:
            hits.append(f"{name}[{'dns' if in_dns else ''}{'+' if in_dns and n_html else ''}{'html' + str(n_html) if n_html else ''}]")
    print(f"=== {d} ({row['pass']}) {status} html={len(html)}")
    print("  techsight:", row["Tech Stack"])
    print("  markers  :", ", ".join(hits))
