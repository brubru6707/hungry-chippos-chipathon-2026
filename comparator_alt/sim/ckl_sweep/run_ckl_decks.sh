#!/bin/bash
# run_ckl_decks.sh — run every deck in this folder through ngspice IN PARALLEL
# and collect the sigma results into one summary table.
#
# Usage (inside the container):
#   bash /foss/designs/comparator_alt/sim/ckl_sweep/run_ckl_decks.sh
#
# All decks run simultaneously (they write to distinct files, so this is safe).
# Wall time ~= the time of ONE deck (about 6-8 min at N=30).

NGSPICE=/foss/tools/bin/ngspice
OUTDIR="/foss/designs/comparator_alt/sim/ckl_sweep"
SUMMARY="$OUTDIR/ckl_sweep_summary.txt"

cd "$OUTDIR"

shopt -s nullglob
decks=(deck_*.spice)
if [ ${#decks[@]} -eq 0 ]; then
  echo "No decks found in $OUTDIR — run make_ckl_decks.sh first."
  exit 1
fi

echo "Launching ${#decks[@]} ngspice jobs in parallel ($(date +%H:%M:%S))..."
for deck in "${decks[@]}"; do
  tag="${deck#deck_}"; tag="${tag%.spice}"
  "$NGSPICE" -b "$deck" > "log_${tag}.txt" 2>&1 &
  echo "  started $deck (pid $!)"
done

wait
echo "All jobs done ($(date +%H:%M:%S)). Collecting results..."

: > "$SUMMARY"
for deck in "${decks[@]}"; do
  tag="${deck#deck_}"; tag="${tag%.spice}"
  # the MC loop echoes a summary block into the log; pull it out
  result=$(grep -A2 "Two-stage offset MC" "log_${tag}.txt" | grep -v "^==" | tr '\n' ' ')
  if [ -n "$result" ]; then
    echo "$tag : $result" >> "$SUMMARY"
  else
    echo "$tag : NO RESULT — check $OUTDIR/log_${tag}.txt" >> "$SUMMARY"
  fi
done

echo ""
echo "================= SWEEP SUMMARY ================="
cat "$SUMMARY"
echo "================================================="
echo "(full per-run detail in $OUTDIR/log_*.txt and /foss/designs/comparator/mc_*_report.txt)"
