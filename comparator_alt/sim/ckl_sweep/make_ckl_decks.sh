#!/bin/bash
# make_ckl_decks.sh — generate ngspice sweep decks from the xschem netlist of tb_2stage.sch
#
# Usage (inside the container):
#   bash make_ckl_decks.sh <path-to-tb_2stage.spice> [N] [delay1 delay2 ...]
#
#   <netlist>  the SPICE netlist xschem generated from tb_2stage.sch
#              (NOT the .sch file itself — ngspice can't read schematics)
#   [N]        Monte Carlo runs per deck, default 30
#   [delays]   CKL delays in ns, default: 2.7 3.0 3.3 3.6 3.9 4.2 4.5
#
# What it edits in each copy (and nothing else):
#   1. mc_runs = 100        ->  mc_runs = N
#   2. Vckl ... 3.3n ...    ->  Vckl ... <d>n ...   (the latch clock delay)
#   3. output file tag      ->  comp2_mc -> mc_ckl<d>_n<N>  (so runs don't overwrite each other)
#   4. the report echo's "ckl=3.3n" label -> "ckl=<d>n"
#   5. tran 10p 1u -> tran 1n 1u   (10p caps ngspice's internal timestep at 10ps,
#      forcing 100k+ steps/transient ~ 100x slower; the ramp moves 0.4mV per clock
#      cycle so 1n costs only ~uV of measurement precision)
#   6. save only v(vout1) v(vin1)  (all the .meas commands need; avoids storing
#      every node at every timepoint)

set -e

NETLIST="$1"
N="${2:-30}"
shift 2 2>/dev/null || shift $# # remaining args = delays
DELAYS="${@:-2.7 3.0 3.3 3.6 3.9 4.2 4.5}"

OUTDIR="/foss/designs/comparator_alt/sim/ckl_sweep"
mkdir -p "$OUTDIR"

if [ ! -f "$NETLIST" ]; then
  echo "ERROR: netlist not found: $NETLIST"
  echo "Generate it first: open tb_2stage.sch in xschem and press the Netlist button."
  exit 1
fi

# sanity: it must be a SPICE netlist, not an xschem schematic
if head -1 "$NETLIST" | grep -q "xschem version"; then
  echo "ERROR: $NETLIST is an xschem .sch schematic, not a SPICE netlist."
  echo "ngspice cannot read this. Netlist it from xschem first."
  exit 1
fi

# sanity: exactly one Vckl source line expected
NV=$(grep -ci "^Vckl" "$NETLIST" || true)
if [ "$NV" != "1" ]; then
  echo "WARNING: expected exactly 1 'Vckl' line in the netlist, found $NV. Check the deck by hand."
fi

for d in $DELAYS; do
  tag="ckl$(echo $d | tr . p)_n${N}"        # e.g. 2.7 -> ckl2p7_n30
  deck="$OUTDIR/deck_${tag}.spice"
  sed -e "s/mc_runs = 100/mc_runs = ${N}/" \
      -e "/^[Vv]ckl/s/3\.3n/${d}n/" \
      -e "s/ckl=3\.3n/ckl=${d}n/" \
      -e "s/comp2_mc/mc_${tag}/g" \
      -e "s/tran 10p 1u/tran 1n 1u/g" \
      -e "s/^\.control/.control\nsave v(vout1) v(vin1)/" \
      "$NETLIST" > "$deck"
  echo "wrote $deck"
  echo "   $(grep -i '^Vckl' $deck)"
done

echo ""
echo "Decks ready. Now run:  bash $OUTDIR/run_ckl_decks.sh"
