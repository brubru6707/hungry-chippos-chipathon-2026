#!/bin/bash
# run_polarity_check.sh — COMP-ALT-12/13 final gate: polarity of the EXTRACTED
# layout netlist. LVS proves the graph matches; it cannot prove VOUT1 is the
# output that falls when VIN1 < VIN2 (a fully mirrored layout also matches).
# This 2-sim check proves it by measurement.
#
#   Case A: VIN1 = 1.64, VIN2 = 1.65  ->  VOUT1 must fall
#   Case B: VIN1 = 1.66, VIN2 = 1.65  ->  VOUT2 must fall
# TT / 27C / 3.3V, CK at 2n, CKL at 3.1n (5n width) — the design point.
#
# Usage:
#   bash run_polarity_check.sh <extracted_netlist_from_LVS>
#
# Handles the two known KLayout->ngspice conversion issues from the COMP-5
# flow (WORKLOG 2026-07-19): devices must be X-prefixed for GF180's
# subckt-based models, and KLayout's AS/AD/PS/PD/NRD/NRS annotations must be
# stripped (the models reject them).

set -e
EXTR="$1"
OUTDIR="/foss/designs/comparator_alt/sim/polarity_check"
NGSPICE=/foss/tools/bin/ngspice
mkdir -p "$OUTDIR"

if [ -z "$EXTR" ] || [ ! -f "$EXTR" ]; then
  echo "ERROR: pass the path of the extracted netlist from the LVS run."; exit 1
fi

# --- convert the extracted netlist for ngspice --------------------------------
CONV="$OUTDIR/comparator_2stage_extracted_sim.spice"
sed -E -e 's/^M/XM/' \
       -e 's/\b[AaPp][SsDd]=[^ ]+//g' \
       -e 's/\b[Nn][Rr][SsDd]=[^ ]+//g' \
    "$EXTR" > "$CONV"
echo "converted netlist: $CONV"

# --- discover the extracted subckt's port order --------------------------------
PORTS=$(grep -im1 "^\.subckt comparator_2stage" "$CONV" | sed -E 's/^\.[Ss][Uu][Bb][Cc][Kk][Tt] +comparator_2stage +//')
if [ -z "$PORTS" ]; then
  echo "ERROR: no .subckt comparator_2stage found in $EXTR"; exit 1
fi
echo "extracted ports: $PORTS"

# --- two decks, expected winner flips ------------------------------------------
for case in A B; do
  if [ "$case" = "A" ]; then vin1=1.64; expfall=vout1; other=vout2; else vin1=1.66; expfall=vout2; other=vout1; fi
  deck="$OUTDIR/deck_polarity_${case}.spice"
  {
    echo "* polarity check case ${case}: VIN1=${vin1} vs VIN2=1.65 -> ${expfall} must fall"
    echo ".param sw_stat_global=0 sw_stat_mismatch=0"
    echo ".include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice"
    echo ".lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical"
    cat "$CONV"
    echo "Xdut ${PORTS} comparator_2stage"
    echo "Vvdd  VDD  0 3.3"
    echo "Vvss  VSS  0 0"
    echo "Vvin1 VIN1 0 ${vin1}"
    echo "Vvin2 VIN2 0 1.65"
    echo "Vck   CK   0 PULSE(0 3.3 2n   100p 100p 8n 20n)"
    echo "Vckl  CKL  0 PULSE(0 3.3 3.1n 100p 100p 5n 20n)"
    echo ".control"
    echo "save v(vout1) v(vout2)"
    echo "tran 0.01n 20n"
    echo "meas tran v1late FIND v(vout1) at=7.8n"
    echo "meas tran v2late FIND v(vout2) at=7.8n"
    echo "echo RESULT case${case} expect_${expfall}_low v1late=\$&v1late v2late=\$&v2late"
    echo ".endc"
    echo ".end"
  } > "$deck"
  "$NGSPICE" -b "$deck" > "$OUTDIR/log_${case}.txt" 2>&1 || true
done

# --- verdict --------------------------------------------------------------------
echo ""
echo "================= POLARITY CHECK ================="
for case in A B; do
  line=$(grep "^RESULT" "$OUTDIR/log_${case}.txt" || echo "RESULT case${case} NO-OUTPUT (see log_${case}.txt)")
  echo "$line" | awk '{
    v1=""; v2="";
    for(i=2;i<=NF;i++){
      if($i ~ /^v1late=/) v1=substr($i,8);
      if($i ~ /^v2late=/) v2=substr($i,8);
    }
    verdict="UNKNOWN";
    if(v1!="" && v2!=""){
      if($2=="caseA"||$0 ~ /caseA/){ if(v1<0.7 && v2>2.6) verdict="PASS"; else if(v2<0.7 && v1>2.6) verdict="POLARITY-REVERSED"; else verdict="NO-DECISION?"; }
      else { if(v2<0.7 && v1>2.6) verdict="PASS"; else if(v1<0.7 && v2>2.6) verdict="POLARITY-REVERSED"; else verdict="NO-DECISION?"; }
    }
    print $0, "->", verdict;
  }'
done
echo "=================================================="
echo "PASS on both = the layout answers correctly in both directions."
echo "POLARITY-REVERSED = the differential pair is swapped in metal: fix"
echo "the twin connections, re-run LVS (it will still pass!), re-run this."
