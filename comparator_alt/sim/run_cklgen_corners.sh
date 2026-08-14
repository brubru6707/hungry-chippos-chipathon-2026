#!/bin/bash
# run_cklgen_corners.sh — ALT-16 step 2: characterize the CKL generator
# (delay chain + AND gating) across corners and supplies.
#
# Measures, per condition:
#   trise : CK rising VDD/2 -> CKL rising VDD/2   (the integration delay)
#   tfall : CK falling VDD/2 -> CKL falling VDD/2 (must stay ~0.1-0.2ns:
#           the shutter closes WITH the reset, that's the AND's whole job)
#
# Targets (from the window map, WORKLOG 2026-08-05, and tracking reasoning):
#   TT trise ~ 0.95-1.20 ns; corners may spread ~0.6-1.6 ns and that is FINE
#   as long as it tracks (shrinks at ff, grows at ss). tfall < 0.3 ns always.
#
# Usage (after netlisting tb_ckl_gen.sch):
#   bash /foss/designs/comparator_alt/sim/run_cklgen_corners.sh /headless/.xschem/simulations/tb_ckl_gen.spice

set -e
NETLIST="$1"
OUTDIR="/foss/designs/comparator_alt/sim/cklgen_corners"
NGSPICE=/foss/tools/bin/ngspice
SUMMARY="$OUTDIR/cklgen_summary.txt"
mkdir -p "$OUTDIR"

if [ -z "$NETLIST" ] || [ ! -f "$NETLIST" ]; then
  echo "ERROR: pass the tb_ckl_gen netlist path (xschem Netlist first)."; exit 1
fi
if head -1 "$NETLIST" | grep -q "xschem version"; then
  echo "ERROR: that is the xschem schematic, not a SPICE netlist."; exit 1
fi

CORNERS="tt:typical:27 ss:ss:125 ff:ff:-40 sf:sf:27 fs:fs:27"
VDDS="3.0 3.3 3.6"

: > "$SUMMARY"
for c in $CORNERS; do
  ctag=${c%%:*}; rest=${c#*:}; sec=${rest%%:*}; temp=${rest#*:}
  for vdd in $VDDS; do
    half=$(awk "BEGIN{printf \"%.6f\", $vdd/2}")
    tag="${ctag}_v${vdd}"
    deck="$OUTDIR/deck_${tag}.spice"
    {
      sed -e '/^\.control/,/^\.endc/d' \
          -e '/^\.end[[:space:]]*$/d' \
          -e "/^\.lib/s/ typical[[:space:]]*$/ ${sec}/" \
          -e "s/^Vvdd.*/Vvdd  VDD  0 ${vdd}/" \
          -e "/^[Vv]ck/s/PULSE(0 3\.3/PULSE(0 ${vdd}/" \
          "$NETLIST"
      cat <<EOF
.temp ${temp}
.options reltol=1e-4 vntol=1e-9
.control
save v(ck) v(ckl)
tran 0.01n 25n
meas tran trise trig v(ck) val=${half} rise=1 targ v(ckl) val=${half} rise=1
meas tran tfall trig v(ck) val=${half} fall=1 targ v(ckl) val=${half} fall=1
echo RESULT ${tag} trise=\$&trise tfall=\$&tfall
.endc
.end
EOF
    } > "$deck"
    "$NGSPICE" -b "$deck" > "$OUTDIR/log_${tag}.txt" 2>&1 || true
    grep "^RESULT" "$OUTDIR/log_${tag}.txt" >> "$SUMMARY" || \
      echo "RESULT ${tag} NO-OUTPUT (see log)" >> "$SUMMARY"
  done
done

echo ""
echo "============== CKL GENERATOR: DELAY vs CORNER =============="
echo "netlist: $NETLIST"
column -t "$SUMMARY"
echo "============================================================="
echo "Want: TT trise ~1.05n; trise SHRINKS at ff / GROWS at ss (tracking);"
echo "tfall < 0.3n everywhere (AND-gated falling edge)."
