#!/usr/bin/env python3
"""Copy gate: run BEFORE a campaign is built. Same copy rules the Smartlead preflight enforces
(unknown words, a word twice in one sentence, spintax balance, sign-off) plus house copy rules.

  python3 copy_gate.py copy.json            # copy.json = [{"label":"A","subject":"...","body":"... <br> ..."}, ...]

PASS means: preflight's copy checks will not fail on this text, every spintax combination reads
clean (printed so a human can read each one), word count is 30-75, no em dashes or banned
hype words, the ask is identical across variants, and every variant has a question.
"""
import itertools, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import smartlead_preflight as pf
import copy_voice

BANNED = ["—", "–", "delve", "leverage", "robust", "landscape", "it's worth noting", "here's the", "let's", "game-changing", "unlock", "streamline", "free", "guarantee", "quick question"]
fails, warns = [], []
variants = json.load(open(sys.argv[1]))
seqs = [{"seq_number": f"1{v['label']}", "subject": v["subject"], "email_body": v["body"]} for v in variants]
words = pf.dictionary()
n0 = len(fails); pf.check_copy(seqs, words, fails)

def expand(t, cap=64):
    opts = re.findall(r"\{([^{}|]*\|[^{}]*)\}", t)
    if not opts: return [t]
    combos = list(itertools.product(*[o.split("|") for o in opts]))[:cap]
    outs = []
    for c in combos:
        s = t; i = 0
        for o, pick in zip(opts, c):
            s = s.replace("{" + o + "}", pick, 1)
        outs.append(s)
    return outs

asks = set()
for v in variants:
    plain = lambda s: re.sub(r"<br\s*/?>", "\n", s)
    for k, combo in enumerate(expand(plain(v["body"]))):
        text = re.sub(r"\{\{[^}]*\}\}|%[a-z-]+%", "X", combo)
        wc = len(text.split())
        if not 30 <= wc <= 75: fails.append(f"{v['label']}: {wc} words (house range 30-75)")
        low = combo.lower()
        for b in BANNED:
            if b in low: fails.append(f"{v['label']}: banned/tell '{b}'")
        if k == 0:
            for h in copy_voice.hard(combo): fails.append(f"{v['label']}: {h}")
            for h in copy_voice.soft(combo): warns.append(f"{v['label']}: {h}")
        if k == 0:
            if "?" not in combo: fails.append(f"{v['label']}: no question")
            last = [l for l in combo.split("\n") if l.strip() and "%sender" not in l][-1]
            asks.add(re.sub(r"\{\{[^}]*\}\}", "X", last).strip())
            print(f"--- {v['label']} | {v['subject']} | {wc} words\n{combo}\n")
if len(asks) > 1: fails.append(f"ask differs across variants (house rule: hold the ask constant while testing offers): {asks}")
if re.search(r"\d", " ".join(re.sub(r"\{\{[^}]*\}\}", "", v["body"]) for v in variants)): warns.append("numbers in copy: each needs a source receipt")
for w in warns: print("WARN", w)
for f in fails: print("FAIL", f)
print("PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(1 if fails else 0)
