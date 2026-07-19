#!/usr/bin/env bash
# ============================================================
# StrongARM delay sweeps (schematic-level, parameterized).
# Generates ngspice decks from the .spice.template files and runs them
# in the iic-osic-tools container. Vcm, the CK trigger threshold and the
# VOUT target threshold are ALL set to VDD/2 for the corner in use -
# never hardcoded 1.65V (SS runs at VDD=2.97 -> VDD/2=1.485).
#
# Usage:
#   ./run_comp_delay_sweeps.sh od  <corner> <temp> <vdd> <tag> "<od list>"
#   ./run_comp_delay_sweeps.sh vcm <corner> <temp> <vdd> <tag> <od> "<vcm list>"
# Examples:
#   ./run_comp_delay_sweeps.sh od ss 125 2.97 ss_2v97 "6.457e-3 1e-3 0.1e-3"
#   ./run_comp_delay_sweeps.sh vcm ss 125 2.97 ss_vcm 6.457e-3 "0.3 0.6 0.9"
# Results land in comp_delay_<tag>.txt / comp_vcm_<tag>.txt next to this
# script. gen_tb_*.spice are generated artifacts - do not edit.
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

CONTAINER=iic-osic-tools_xvnc_uid_501
NGSPICE=/foss/tools/bin/ngspice
SIMDIR=/foss/designs/comparator/sim

mode=$1; corner=$2; temp=$3; vdd=$4; tag=$5
vth=$(awk -v v="$vdd" 'BEGIN{printf "%.6g", v/2}')

common_subst() {
  sed -e "s/@CORNER@/$corner/g" -e "s/@TEMP@/$temp/g" -e "s/@VDD@/$vdd/g" \
      -e "s/@VTH@/$vth/g" -e "s/@TAG@/$tag/g"
}

case "$mode" in
  od)
    odlist=$6
    common_subst < tb_comp_delay_param.spice.template \
      | sed -e "s/@ODLIST@/$odlist/g" > "gen_tb_${tag}.spice"
    ;;
  vcm)
    od=$6; vcmlist=$7
    common_subst < tb_comp_vcm_sweep.spice.template \
      | sed -e "s/@OD@/$od/g" -e "s/@VCMLIST@/$vcmlist/g" > "gen_tb_${tag}.spice"
    ;;
  *)
    echo "unknown mode '$mode' (want od|vcm)" >&2; exit 1
    ;;
esac

echo "== $mode sweep: corner=$corner temp=$temp VDD=$vdd (VDD/2=$vth) tag=$tag =="
if [ -d /foss/designs ]; then
  cd "$SIMDIR" && "$NGSPICE" -b "gen_tb_${tag}.spice"
else
  docker exec "$CONTAINER" bash -c "cd $SIMDIR && $NGSPICE -b gen_tb_${tag}.spice"
fi
