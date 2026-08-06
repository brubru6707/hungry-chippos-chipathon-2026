#!/bin/bash
# make_mc_ss30_deck.sh — build the COMP-ALT-11 "worst survivor" MC deck:
# full offset Monte Carlo (N=100) at ss / 125C / VDD=3.0V, ramp re-centered
# to that condition's mid-rail (1.5V).
#
# Edits applied to the tb_2stage netlist:
#   .lib typical -> ss ; .temp 125 ; VDD 3.3 -> 3.0 ; CK/CKL swing -> 3.0
#   ramp 1.64/1.66 -> 1.49/1.51 ; reference & offset zero 1.65 -> 1.50
#   (output threshold v(vout1)=1.5 is ALREADY VDD/2 at 3.0V — untouched)
#   output files tagged mc_ss30_*
#
# Usage:
#   bash make_mc_ss30_deck.sh /headless/.xschem/simulations/tb_2stage.spice
#   /foss/tools/bin/ngspice -b /foss/designs/comparator_alt/sim/mc_ss30.spice 2>&1 | tail -6

set -e
NETLIST="$1"
OUT="/foss/designs/comparator_alt/sim/mc_ss30.spice"

if [ -z "$NETLIST" ] || [ ! -f "$NETLIST" ]; then echo "ERROR: pass netlist path"; exit 1; fi
if head -1 "$NETLIST" | grep -q "xschem version"; then
  echo "ERROR: that is the xschem schematic, not a SPICE netlist."; exit 1
fi
if ! grep -q "mc_runs = 100" "$NETLIST"; then
  echo "NOTE: netlist has mc_runs != 100 (maybe 200 from the TT deep run) — deck keeps 100 anyway."
fi

sed -e "/^\.lib/s/ typical[[:space:]]*$/ ss/" \
    -e "/^\.control/i .temp 125" \
    -e "s/^Vvdd.*/Vvdd  VDD  0 3.0/" \
    -e "/^[Vv]ck/s/PULSE(0 3\.3/PULSE(0 3.0/" \
    -e "s/1\.64/1.49/g" \
    -e "s/1\.66/1.51/g" \
    -e "s/1\.65/1.50/g" \
    -e "s/mc_runs = 200/mc_runs = 100/" \
    -e "s/comp2_mc_/mc_ss30_/g" \
    "$NETLIST" > "$OUT"

echo "wrote $OUT"
echo "  ramp:      $(grep -m1 '^Vvin1' $OUT)"
echo "  reference: $(grep -m1 '^Vvin2' $OUT)"
echo "  supply:    $(grep -m1 '^Vvdd' $OUT)"
echo "  outputs -> /foss/designs/comparator_alt/results/mc_ss30_*"
echo ""
echo "Run:  /foss/tools/bin/ngspice -b $OUT 2>&1 | tail -6"
