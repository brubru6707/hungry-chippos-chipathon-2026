#!/bin/bash
# run_alt11_screen_realistic.sh — COMP-ALT-11 step 1b: the REALISTIC-drive
# grid. Same corners and supplies as the pure-Vcm screen, but the inputs are
# driven the way the assembled ADC drives them:
#   VIN2 (reference) = VDD/2, hard-wired — as in the SAR architecture
#   VIN1 (DAC_TOP)   = swept over the FULL input range, 3%..97% of VDD
# The pure-Vcm screen (run_alt11_screen.sh) stress-tested both-inputs-low, a
# condition the ADC cannot physically produce (one input is a wire to VDD/2);
# its W region documents comparator physics. THIS grid tests every condition
# the ADC can produce. All-P here = "correct decision for any ADC input, all
# corners, all supplies — no restrictions."
#
# Expected polarity flips with the input side:
#   VIN1 < VDD/2  ->  VOUT1 must fall
#   VIN1 > VDD/2  ->  VOUT2 must fall
# The verdict logic knows which side to expect (exp=1 / exp=2 in RESULT).
#
# Usage (inside the container):
#   bash /foss/designs/comparator_alt/sim/run_alt11_screen_realistic.sh /headless/.xschem/simulations/tb_2stage.spice
# 120 decks, 6 at a time, ~5-10 minutes.

set -e
NETLIST="$1"
OUTDIR="/foss/designs/comparator_alt/sim/alt11_screen_realistic"
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
FRACS="0.03 0.15 0.30 0.45 0.55 0.70 0.85 0.97"   # VIN1 as a fraction of VDD

# ---- generate all decks -----------------------------------------------------
count=0
for c in $CORNERS; do
  ctag=${c%%:*}; rest=${c#*:}; sec=${rest%%:*}; temp=${rest#*:}
  for vdd in $VDDS; do
    half=$(awk "BEGIN{printf \"%.6f\", $vdd/2}")
    for f in $FRACS; do
      vin1=$(awk "BEGIN{printf \"%.6f\", $f*$vdd}")
      # which output must fall?
      exp=$(awk "BEGIN{print ($f < 0.5) ? 1 : 2}")
      fallout="vout${exp}"
      tag="${ctag}_v${vdd}_f${f}"
      deck="$OUTDIR/deck_${tag}.spice"
      {
        sed -e '/^\.control/,/^\.endc/d' \
            -e '/^\.end[[:space:]]*$/d' \
            -e "/^\.lib/s/ typical[[:space:]]*$/ ${sec}/" \
            -e "s/^Vvdd.*/Vvdd  VDD  0 ${vdd}/" \
            -e "/^[Vv]ck/s/PULSE(0 3\.3/PULSE(0 ${vdd}/" \
            -e "s/^Vvin1.*/Vvin1 VIN1 0 ${vin1}/" \
            -e "s/^Vvin2.*/Vvin2 VIN2 0 ${half}/" \
            "$NETLIST"
        cat <<EOF
.temp ${temp}
.options reltol=1e-4 vntol=1e-9
.control
save v(vout1) v(vout2) v(ck)
tran 0.01n 20n
meas tran tdelay trig v(ck) val=${half} rise=1 targ v(${fallout}) val=${half} fall=1
meas tran v1late FIND v(vout1) at=7.5n
meas tran v2late FIND v(vout2) at=7.5n
echo RESULT ${ctag} ${vdd} ${f} exp=${exp} delay=\$&tdelay v1late=\$&v1late v2late=\$&v2late
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
echo "corner,vdd,vin1_frac,expected_fall,delay_s,v1late,v2late,verdict" > "$CSV"
for log in "$OUTDIR"/log_*.txt; do
  line=$(grep "^RESULT" "$log" || true)
  [ -z "$line" ] && continue
  echo "$line" | awk '{
    ctag=$2; vdd=$3; frac=$4;
    ex=""; delay=""; v1=""; v2="";
    for(i=5;i<=NF;i++){
      if($i ~ /^exp=/)    ex=substr($i,5);
      if($i ~ /^delay=/)  delay=substr($i,7);
      if($i ~ /^v1late=/) v1=substr($i,8);
      if($i ~ /^v2late=/) v2=substr($i,8);
    }
    lo=0.2*vdd; hi=0.6*vdd;
    # loser = the output expected to fall; winner = the other one
    if(ex=="1"){ loser=v1; winner=v2 } else { loser=v2; winner=v1 }
    if(v1=="" || v2=="")               verdict="MEASFAIL";
    else if(loser<lo && winner>hi)     verdict="PASS";
    else if(loser>hi && winner<lo)     verdict="WRONGPOL";
    else if(loser>hi && winner>hi)     verdict="NODECIDE";
    else                               verdict="PARTIAL";
    printf "%s,%s,%s,%s,%s,%s,%s,%s\n", ctag, vdd, frac, ex, delay, v1, v2, verdict;
  }' >> "$CSV"
done

# ---- human-readable grid ----------------------------------------------------
{
echo "COMP-ALT-11 realistic-drive screen — VIN2=VDD/2 (as in the ADC), VIN1 full range, CKL=${CKL_LBL} from netlist"
echo "columns = VIN1 as fraction of VDD; expected winner flips at 0.5"
echo "P=PASS  .=NODECIDE  W=WRONGPOL  ?=PARTIAL/MEASFAIL"
echo ""
printf "%-4s %-5s |" "corn" "VDD"
for f in $FRACS; do printf " %5s" "$f"; done; echo ""
echo "-----------------------------------------------------------------"
for c in $CORNERS; do
  ctag=${c%%:*}
  for vdd in $VDDS; do
    printf "%-4s %-5s |" "$ctag" "$vdd"
    for f in $FRACS; do
      v=$(awk -F, -v c="$ctag" -v d="$vdd" -v m="$f" \
          '$1==c && $2==d && $3==m {print $8}' "$CSV")
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
echo "Full numbers: $CSV"
