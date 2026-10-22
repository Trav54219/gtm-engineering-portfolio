#!/bin/bash
# Cheapest-first per query file. COST column is per call/result/success: read the unit, they differ.
for f in "$1"/q*.txt; do echo "=== $(basename $f): $(head -1 $f | cut -c1-80)"
grep -E '^\s*(▸ )?[a-z0-9_.-]+\.[a-z0-9_.-]+ +(free|\$[0-9.]+)' "$f" | sed -E 's/^\s*(▸ )?//' | awk '{print $2"\t"$1"\t"substr($0, index($0,$3), 70)}' | sort -t$'\t' -k1,1 | head -${2:-15}; done
