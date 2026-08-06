#!/bin/bash
# collect_realistic.sh — re-run ONLY the collection/classification over the
# already-completed logs in alt11_screen_realistic/ (sims don't need re-running).
OUTDIR="/foss/designs/comparator_alt/sim/alt11_screen_realistic"
CSV="$OUTDIR/screen_results.csv"
GRID="$OUTDIR/screen_grid.txt"
CORNERS="tt:typical:27 ss:ss:125 ff:ff:-40 sf:sf:27 fs:fs:27"
VDDS="3.0 3.3 3.6"
FRACS="0.03 0.15 0.30 0.45 0.55 0.70 0.85 0.97"
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
echo "COMP-ALT-11 realistic-drive screen — VIN2=VDD/2 (as in the ADC), VIN1 swept over full range"
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
