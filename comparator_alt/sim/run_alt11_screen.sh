#!/bin/bash
# run_alt11_screen.sh — COMP-ALT-11 step 1: functional SCREEN of the full
# operating grid. Single-shot sims (no Monte Carlo) answer, for every
# combination: does the comparator make a clean, correct decision at 0.5 LSB
# overdrive, and how fast?
#
# Grid:
#   corners : tt (typical,27C) ss (125C) ff (-40C) sf (27C) fs (27C)
#             [skew corners run at 27C — they stress P:N ratio, not temp;
#              noted simplification]
#   VDD     : 3.0 / 3.3 / 3.6  (swept independently of corner, unlike ALT-10
#             where VDD moved together with process)
#   Vcm     : 0.4 0.7 1.0 1.3 1.65 2.0 2.4 2.8  (absolute volts)
#   od      : 0.5 LSB *of that VDD* = VDD/512 (LSB scales with supply)
#   CKL     : fixed at the 2.8n design value (that is what's under test)
#
# Per run, three measurements decide a verdict:
#   tdelay : CK rising VDD/2 -> VOUT1 falling VDD/2
#   v1min/v2min : minima of both outputs DURING the strobe window (2.8-7.8n)
#     v1min low  + v2min high -> PASS      (correct decision: VIN1<VIN2 so
#                                           VOUT1 must be the one that falls)
#     v1min high + v2min high -> NODECIDE  (latch never fired)
#     v1min high + v2min low  -> WRONGPOL  (decided the wrong way!)
#
# Usage (inside the container):
#   bash /foss/designs/comparator_alt/sim/run_alt11_screen.sh /headless/.xschem/simulations/tb_2stage.spice
# 120 decks, run 6 at a time; expect ~5-10 minutes total.

set -e
NETLIST="$1"
OUTDIR="/foss/designs/comparator_alt/sim/alt11_screen"
NGSPICE=/foss/tools/bin/ngspice
CSV="$OUTDIR/screen_results.csv"
GRID="$OUTDIR/screen_grid.txt"
mkdir -p "$OUTDIR"

if [ -z "$NETLIST" ] || [ ! -f "$NETLIST" ]; then
  echo "ERROR: pass the tb_2stage netlist path (xschem Netlist button first)."; exit 1
fi
if head -1 "$NETLIST" | grep -q "xschem version"; then
  echo "ERROR: that is the xschem schematic, not a SPICE netlist."; exit 1
fi

CKL_LBL=$(grep -im1 "^Vckl" "$NETLIST" | awk '{print $6}')
CORNERS="tt:typical:27 ss:ss:125 ff:ff:-40 sf:sf:27 fs:fs:27"
VDDS="3.0 3.3 3.6"
VCMS="0.4 0.7 1.0 1.3 1.65 2.0 2.4 2.8"

# ---- generate all decks -----------------------------------------------------
count=0
for c in $CORNERS; do
  ctag=${c%%:*}; rest=${c#*:}; sec=${rest%%:*}; temp=${rest#*:}
  for vdd in $VDDS; do
    for vcm in $VCMS; do
      od=$(awk "BEGIN{printf \"%.6f\", $vdd/512}")
      vin1=$(awk "BEGIN{printf \"%.6f\", $vcm - $od}")
      half=$(awk "BEGIN{printf \"%.6f\", $vdd/2}")
      tag="${ctag}_v${vdd}_cm${vcm}"
      deck="$OUTDIR/deck_${tag}.spice"
      {
        sed -e '/^\.control/,/^\.endc/d' \
            -e '/^\.end[[:space:]]*$/d' \
            -e "/^\.lib/s/ typical[[:space:]]*$/ ${sec}/" \
            -e "s/^Vvdd.*/Vvdd  VDD  0 ${vdd}/" \
            -e "/^[Vv]ck/s/PULSE(0 3\.3/PULSE(0 ${vdd}/" \
            -e "s/^Vvin1.*/Vvin1 VIN1 0 ${vin1}/" \
            -e "s/^Vvin2.*/Vvin2 VIN2 0 ${vcm}/" \
            "$NETLIST"
        cat <<EOF
.temp ${temp}
.options reltol=1e-4 vntol=1e-9
.control
save v(vout1) v(vout2) v(ck)
tran 0.01n 20n
meas tran tdelay trig v(ck) val=${half} rise=1 targ v(vout1) val=${half} fall=1
meas tran v1min MIN v(vout1) from=2.8n to=7.8n
meas tran v2min MIN v(vout2) from=2.8n to=7.8n
meas tran v1late FIND v(vout1) at=7.5n
meas tran v2late FIND v(vout2) at=7.5n
echo RESULT ${ctag} ${vdd} ${vcm} delay=\$&tdelay v1late=\$&v1late v2late=\$&v2late v1min=\$&v1min v2min=\$&v2min
.endc
.end
EOF
      } > "$deck"
      count=$((count+1))
    done
  done
done
echo "generated $count decks in $OUTDIR"

# ---- run, 6 at a time -------------------------------------------------------
n=0
for deck in "$OUTDIR"/deck_*.spice; do
  tag=$(basename "$deck" .spice); tag=${tag#deck_}
  "$NGSPICE" -b "$deck" > "$OUTDIR/log_${tag}.txt" 2>&1 &
  n=$((n+1))
  if [ $((n % 6)) -eq 0 ]; then wait; echo "  ...$n/$count done ($(date +%H:%M:%S))"; fi
done
wait
echo "all $count runs complete"

# ---- collect + classify -----------------------------------------------------
echo "corner,vdd,vcm,delay_s,v1late,v2late,v1min,v2min,verdict" > "$CSV"
for log in "$OUTDIR"/log_*.txt; do
  line=$(grep "^RESULT" "$log" || true)
  [ -z "$line" ] && continue
  echo "$line" | awk '{
    ctag=$2; vdd=$3; vcm=$4;
    delay=""; v1l=""; v2l=""; v1m=""; v2m="";
    for(i=5;i<=NF;i++){
      if($i ~ /^delay=/)  delay=substr($i,7);
      if($i ~ /^v1late=/) v1l=substr($i,8);
      if($i ~ /^v2late=/) v2l=substr($i,8);
      if($i ~ /^v1min=/)  v1m=substr($i,7);
      if($i ~ /^v2min=/)  v2m=substr($i,7);
    }
    lo=0.2*vdd; hi=0.6*vdd;
    if(v1l=="" || v2l=="")        verdict="MEASFAIL";
    else if(v1l<lo && v2l>hi)     verdict="PASS";      # correct: VOUT1 low, VOUT2 recovered high
    else if(v1l>hi && v2l<lo)     verdict="WRONGPOL";  # decided backwards
    else if(v1l>hi && v2l>hi)     verdict="NODECIDE";  # both still high at 7.5n
    else                          verdict="PARTIAL";   # genuinely ambiguous (slow/stalled)
    printf "%s,%s,%s,%s,%s,%s,%s,%s,%s\n", ctag, vdd, vcm, delay, v1l, v2l, v1m, v2m, verdict;
  }' >> "$CSV"
done

# ---- human-readable grid ----------------------------------------------------
{
echo "COMP-ALT-11 functional screen — verdict per Vcm point (od=0.5LSB(VDD), CKL=${CKL_LBL} from netlist)"
echo "P=PASS  .=NODECIDE  W=WRONGPOL  ?=PARTIAL/MEASFAIL"
echo ""
printf "%-4s %-5s |" "corn" "VDD"
for vcm in $VCMS; do printf " %5s" "$vcm"; done; echo ""
echo "-----------------------------------------------------------------"
for c in $CORNERS; do
  ctag=${c%%:*}
  for vdd in $VDDS; do
    printf "%-4s %-5s |" "$ctag" "$vdd"
    for vcm in $VCMS; do
      v=$(awk -F, -v c="$ctag" -v d="$vdd" -v m="$vcm" \
          '$1==c && $2==d && $3==m {print $9}' "$CSV")
      case "$v" in
        PASS) g="P";; NODECIDE) g=".";; WRONGPOL) g="W";;
        "") g="-";; *) g="?";;
      esac
      printf " %5s" "$g"
    done
    echo ""
  done
done
} | tee "$GRID"
echo ""
echo "Full numbers: $CSV   (delays, output minima per point)"
