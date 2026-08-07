#!/bin/bash
# probe_ckl_retune.sh — focused probe: can a LATER fixed CKL fix the ss/3.0V
# low-input wrong-polarity cells without breaking the FF cliff?
# 12 single-shot runs, ~2 minutes:
#   A) ss/3.0V, VIN1 = 0.03*VDD and 0.30*VDD (the failing cells) at CKL = 3.2/3.6/4.0n
#   B) ff/3.6V, near-balance od=0.5LSB (cliff-sensitive case)     at CKL = 3.2/3.6/4.0n
#   C) ss/3.0V, near-balance od=0.5LSB (sanity at late strobe)    at CKL = 3.2/3.6/4.0n
# Verdicts as in the realistic screen (expected side aware, values at 7.5n...
# note: for CKL=4.0 the strobe window is 4.0-9.1n, so verdicts sample at 8.8n).
#
# Usage: bash probe_ckl_retune.sh /headless/.xschem/simulations/tb_2stage.spice

set -e
NETLIST="$1"
OUTDIR="/foss/designs/comparator_alt/sim/alt11_probe_retune"
NGSPICE=/foss/tools/bin/ngspice
mkdir -p "$OUTDIR"

if [ -z "$NETLIST" ] || [ ! -f "$NETLIST" ]; then echo "ERROR: pass netlist path"; exit 1; fi

gen () { # tag sec temp vdd vin1 ckl expfall
  local tag=$1 sec=$2 temp=$3 vdd=$4 vin1=$5 ckl=$6 ex=$7
  local half tlate
  half=$(awk "BEGIN{printf \"%.6f\", $vdd/2}")
  tlate=$(awk "BEGIN{printf \"%.1f\", $ckl + 4.8}")
  {
    sed -e '/^\.control/,/^\.endc/d' \
        -e '/^\.end[[:space:]]*$/d' \
        -e "/^\.lib/s/ typical[[:space:]]*$/ ${sec}/" \
        -e "s/^Vvdd.*/Vvdd  VDD  0 ${vdd}/" \
        -e "/^[Vv]ck/s/PULSE(0 3\.3/PULSE(0 ${vdd}/" \
        -e "/^[Vv]ckl/s/2\.8n/${ckl}n/" \
        -e "s/^Vvin1.*/Vvin1 VIN1 0 ${vin1}/" \
        -e "s/^Vvin2.*/Vvin2 VIN2 0 ${half}/" \
        "$NETLIST"
    cat <<EOF
.temp ${temp}
.options reltol=1e-4 vntol=1e-9
.control
save v(vout1) v(vout2) v(ck)
tran 0.01n 20n
meas tran v1late FIND v(vout1) at=${tlate}n
meas tran v2late FIND v(vout2) at=${tlate}n
echo RESULT ${tag} vdd=${vdd} exp=${ex} v1late=\$&v1late v2late=\$&v2late
.endc
.end
EOF
  } > "$OUTDIR/deck_${tag}.spice"
}

for ckl in 3.2 3.6 4.0; do
  # A) the failing realistic-drive cells at ss/3.0
  v1a=$(awk "BEGIN{printf \"%.6f\", 0.03*3.0}")
  v1b=$(awk "BEGIN{printf \"%.6f\", 0.30*3.0}")
  gen "ssA_f0p03_ckl${ckl}" ss 125 3.0 "$v1a" "$ckl" 1
  gen "ssA_f0p30_ckl${ckl}" ss 125 3.0 "$v1b" "$ckl" 1
  # B) FF cliff sentinel: fastest corner, near-balance
  v1c=$(awk "BEGIN{printf \"%.6f\", 3.6/2 - 3.6/512}")
  gen "ffB_bal_ckl${ckl}" ff -40 3.6 "$v1c" "$ckl" 1
  # C) ss/3.0 near-balance sanity
  v1d=$(awk "BEGIN{printf \"%.6f\", 3.0/2 - 3.0/512}")
  gen "ssC_bal_ckl${ckl}" ss 125 3.0 "$v1d" "$ckl" 1
done

for deck in "$OUTDIR"/deck_*.spice; do
  tag=$(basename "$deck" .spice); tag=${tag#deck_}
  "$NGSPICE" -b "$deck" > "$OUTDIR/log_${tag}.txt" 2>&1
done

echo ""
echo "================= CKL RETUNE PROBE ================="
for log in "$OUTDIR"/log_*.txt; do
  grep "^RESULT" "$log" | awk '{
    tag=$2; vdd=""; ex=""; v1=""; v2="";
    for(i=3;i<=NF;i++){
      if($i ~ /^vdd=/)    vdd=substr($i,5);
      if($i ~ /^exp=/)    ex=substr($i,5);
      if($i ~ /^v1late=/) v1=substr($i,8);
      if($i ~ /^v2late=/) v2=substr($i,8);
    }
    lo=0.2*vdd; hi=0.6*vdd;
    if(ex=="1"){ loser=v1; winner=v2 } else { loser=v2; winner=v1 }
    if(v1=="" || v2=="")            verdict="MEASFAIL";
    else if(loser<lo && winner>hi)  verdict="PASS";
    else if(loser>hi && winner<lo)  verdict="WRONGPOL";
    else if(loser>hi && winner>hi)  verdict="NODECIDE";
    else                            verdict="PARTIAL";
    printf "%-22s v1late=%-9s v2late=%-9s -> %s\n", tag, v1, v2, verdict;
  }'
done
echo "===================================================="
echo "Want: ssA rows -> PASS at some CKL; ffB rows -> PASS at that same CKL."
