#!/bin/bash
# Usage: sweep.sh OUTDIR "job phrase 1" "job phrase 2" ...   (one catalog query per phrase, 100 results each)
# Then: sort_prices.sh OUTDIR  -> cheapest-first list per job
out="$1"; shift; mkdir -p "$out"; i=0
for q in "$@"; do i=$((i+1)); treg catalog search "$q" --limit 100 > "$out/q$i.txt" 2>&1; echo "q$i: $q"; done
