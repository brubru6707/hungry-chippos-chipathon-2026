#!/bin/bash
# make_debug_decks.sh — single-shot waveform debug decks (no Monte Carlo).
# Runs 45 ns (~2 clock cycles) and dumps preamp + latch waveforms to a text
# file per CKL delay, so the decision polarity can be inspected directly.
#
# Usage (inside the container):
#   bash make_debug_decks.sh <path-to-tb_2stage.spice> [delay1 delay2 ...]
# Then:
#   for f in /foss/designs/comparator_alt/sim/ckl_sweep/debug_*.spice; do
#     /foss/tools/bin/ngspice -b "$f"; done
#
# VIN1 keeps its PWL ramp: at t<45n it sits at ~1.640 V, i.e. VIN1 < VIN2
# by ~10 mV. Per the testbench's convention that is the case where VOUT1
# is expected to FALL each evaluation.

set -e
NETLIST="$1"
shift 1 2>/dev/null || true
DELAYS="${@:-2.7 3.0 3.3}"
OUTDIR="/foss/designs/comparator_alt/sim/ckl_sweep"
mkdir -p "$OUTDIR"

if head -1 "$NETLIST" | grep -q "xschem version"; then
  echo "ERROR: $NETLIST is an xschem schematic, not a SPICE netlist."; exit 1
fi

for d in $DELAYS; do
  tag="ckl$(echo $d | tr . p)"
  deck="$OUTDIR/debug_${tag}.spice"
  {
    sed -e "/^[Vv]ckl/s/3\.3n/${d}n/" \
        -e '/^\.control/,/^\.endc/d' \
        -e '/^\.end[[:space:]]*$/d' "$NETLIST"
    cat <<EOF
.control
save v(vout1) v(vout2) v(x1.dip1) v(x1.dip2) v(ck) v(ckl) v(vin1)
tran 0.02n 45n
wrdata ${OUTDIR}/debug_${tag}.txt v(vout1) v(vout2) v(x1.dip1) v(x1.dip2) v(ck) v(ckl)
echo wrote ${OUTDIR}/debug_${tag}.txt
.endc
.end
EOF
  } > "$deck"
  echo "wrote $deck   ($(grep -i '^Vckl' $deck))"
done
echo ""
echo "Run them with:"
echo "  for f in $OUTDIR/debug_*.spice; do /foss/tools/bin/ngspice -b \$f; done"
