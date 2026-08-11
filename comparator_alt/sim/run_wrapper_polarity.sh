#!/bin/bash
# run_wrapper_polarity.sh — verify the comparator_alt WRAPPER presents the
# COMP-5 output convention required by docs/pin_contracts.md §1/§4:
#
#     VIN1 > VIN2  =>  VOUT1 falls   (glue SR latch reads: CMP_OUT=1 = keep)
#     VIN1 < VIN2  =>  VOUT2 falls   (CMP_OUT=0)
#
# NOTE: this is the OPPOSITE of the bare comparator_2stage convention — the
# wrapper's crossed outputs are what flips it. Running this script against a
# tb of the BARE comparator must FAIL both cases; against the wrapper tb it
# must PASS both. That asymmetry is itself the check that the crossing exists.
#
# Usage (inside the container, after netlisting tb_comparator_alt.sch):
#   bash run_wrapper_polarity.sh /headless/.xschem/simulations/tb_comparator_alt.spice

set -e
NETLIST="$1"
OUTDIR="/foss/designs/comparator_alt/sim/wrapper_polarity"
NGSPICE=/foss/tools/bin/ngspice
mkdir -p "$OUTDIR"

if [ -z "$NETLIST" ] || [ ! -f "$NETLIST" ]; then
  echo "ERROR: pass the tb_comparator_alt netlist path (xschem Netlist first)."; exit 1
fi
if head -1 "$NETLIST" | grep -q "xschem version"; then
  echo "ERROR: that is the xschem schematic, not a SPICE netlist."; exit 1
fi

# COMP-5 convention expectations:
#   case A: VIN1=1.64 < VIN2=1.65 -> wrapper VOUT2 must fall
#   case B: VIN1=1.66 > VIN2=1.65 -> wrapper VOUT1 must fall
for case in A B; do
  if [ "$case" = "A" ]; then vin1=1.64; expfall=2; else vin1=1.66; expfall=1; fi
  deck="$OUTDIR/deck_${case}.spice"
  {
    sed -e '/^\.control/,/^\.endc/d' \
        -e '/^\.end[[:space:]]*$/d' \
        -e "s/^Vvin1.*/Vvin1 VIN1 0 ${vin1}/" \
        -e "s/^Vvin2.*/Vvin2 VIN2 0 1.65/" \
        "$NETLIST"
    cat <<EOF
.options reltol=1e-4 vntol=1e-9
.control
save v(vout1) v(vout2)
tran 0.01n 20n
meas tran v1late FIND v(vout1) at=7.8n
meas tran v2late FIND v(vout2) at=7.8n
echo RESULT case${case} exp=${expfall} v1late=\$&v1late v2late=\$&v2late
.endc
.end
EOF
  } > "$deck"
  "$NGSPICE" -b "$deck" > "$OUTDIR/log_${case}.txt" 2>&1 || true
done

echo ""
echo "========== WRAPPER POLARITY (COMP-5 convention) =========="
echo "netlist : $NETLIST"
echo "DUT line: $(grep -Eim1 '^x[0-9]+ .*comparator' "$NETLIST")"
for case in A B; do
  line=$(grep "^RESULT" "$OUTDIR/log_${case}.txt" || echo "RESULT case${case} NO-OUTPUT (see log_${case}.txt)")
  echo "$line" | awk '{
    ex=""; v1=""; v2="";
    for(i=2;i<=NF;i++){
      if($i ~ /^exp=/)    ex=substr($i,5);
      if($i ~ /^v1late=/) v1=substr($i,8);
      if($i ~ /^v2late=/) v2=substr($i,8);
    }
    verdict="UNKNOWN";
    if(v1!="" && v2!=""){
      if(ex=="1"){ if(v1<0.7 && v2>2.6) verdict="PASS"; else if(v2<0.7 && v1>2.6) verdict="STILL-ALT-CONVENTION (crossing missing?)"; else verdict="NO-DECISION?"; }
      else       { if(v2<0.7 && v1>2.6) verdict="PASS"; else if(v1<0.7 && v2>2.6) verdict="STILL-ALT-CONVENTION (crossing missing?)"; else verdict="NO-DECISION?"; }
    }
    print $0, "->", verdict;
  }'
done
echo "==========================================================="
echo "PASS both = wrapper is glue-compatible per pin_contracts §1/§4."
