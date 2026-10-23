# List build: US precision CNC machine shops (and tool/die, steel fabricators)

About 333 verified leads from one source query plus a funnel. Preview drafted, nothing in the sequencer until a send decision.

## Recipe

1. **Count first, free.** Keyword "cnc machining" + US + headcount 11 to 249 on a company search returned 1,479 rows. Two more keyword passes (precision machining, machine shop, 5-axis, swiss, contract machining), each excluding earlier keywords, added 1,692. About $0.36 per 1,700 rows.
2. **Funnel gate** (size, persona, already-seen) before any paid verification.
3. **Find owners and emails**, probing 10 rows across providers before a volume run.
4. **Persona check by hand.** A "VP Real Estate" got through the title filter.
5. **Fit check** on the specific first-line fact. A generic fact ("ISO 9001") gets the short variant of the copy, not a forced personalisation.

## Traps I hit

- The data provider's tool returned each result as a JSON string inside JSON. My first parse crashed twice, and each crashed page was still charged. Save the raw response before parsing.
- The CLI had no budget flag, and a cost field read 0 on some responses, so I cap by call count.
- The funnel gate drops rows with free-mail or role emails. For shops I'd owner-find, I rename the column instead of passing it.
- "Already seen" meant any earlier list, not just a live campaign. Distinguish the two in the ledger: 94 of 100 sampled leads had never been emailed, 6 were already in a campaign and stayed out.
- Another session spent from the same data balance. Attribute a balance drop from the ledger, not from the last step I ran.

## Spend

Search cost about $0.36 per 1,700 company rows and about $0.38 per 1,000 owner rows, with a $2 cap I set before starting. I don't have a verified total for the whole build, so I'm not quoting one.
