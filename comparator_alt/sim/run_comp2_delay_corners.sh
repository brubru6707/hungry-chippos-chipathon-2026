#!/bin/bash
# run_comp2_delay_corners.sh — COMP-ALT-10: two-stage comparator delay at
# TT + worst corners, plus CKL-window survival probes at SS and FF.
#
# Usage (inside the container):
#   bash /foss/designs/comparator_alt/sim/run_comp2_delay_corners.sh /headless/.xschem/simulations/tb_2stage.spice
#
# Builds 10 single-shot decks from the tb_2stage netlist (must be freshly
# netlisted from xschem, CKL=2.8n in the Vckl line):
#   TT (typical/ 27C/3.30V): od=0.5LSB and od=0.1mV        @ CKL=2.8n
#   SS (ss     /125C/2.97V): od=0.5LSB @ CKL=2.6/2.8/3.0n, od=0.1mV @ 2.8n
#   FF (ff     /-40C/3.63V): od=0.5LSB @ CKL=2.6/2.8/3.0n, od=0.1mV @ 2.8n
# Conventions per comparator/WORKLOG.md 2026-07-19 (COMP-5 delay flow):
# Vcm = VDD/2 of the corner, CK-trigger and VOUT thresholds = VDD/2,
# od fixed at 6.457mV (0.5 LSB of the nominal 3.3V scale), reltol=1e-4 vntol=1nV.
# VIN1 = Vcm - od so the measured (losing, falling) output is VOUT1.
#
# Delay = CK rising through VDD/2 -> VOUT1 falling through VDD/2.
# v1end/v2end at 18ns verify full resolution (expect v1~0, v2~VDD).

set -e
NETLIST="$1"
OUTDIR="/foss/designs/comparator_alt/sim/comp2_delay"
NGSPICE=/foss/tools/bin/ngspice
SUMMARY="$OUTDIR/comp2_delay_corners_summary.txt"
mkdir -p "$OUTDIR"

if [ -z "$NETLIST" ] || [ ! -f "$NETLIST" ]; then
  echo "ERROR: pass the path to the tb_2stage netlist (xschem: Netlist button first)."; exit 1
fi
if head -1 "$NETLIST" | grep -q "xschem version"; then
  echo "ERROR: that is the xschem schematic, not a SPICE netlist."; exit 1
fi
if ! grep -qi "^Vckl.*2\.8n" "$NETLIST"; then
  echo "WARNING: Vckl line in netlist does not contain 2.8n — was the schematic"
  echo "         updated and re-netlisted? CKL substitution may fail. Continuing..."
fi

gen_deck () { # tag lib_section temp vdd od ckl_ns
  local tag=$1 sec=$2 temp=$3 vdd=$4 od=$5 ckl=$6
  local vcm vin1
  vcm=$(awk "BEGIN{printf \"%.6f\", $vdd/2}")
  vin1=$(awk "BEGIN{printf \"%.6f\", $vdd/2 - $od}")
  local deck="$OUTDIR/deck_${tag}.spice"
  {
    sed -e '/^\.control/,/^\.endc/d' \
        -e '/^\.end[[:space:]]*$/d' \
        -e "/^\.lib/s/ typical[[:space:]]*$/ ${sec}/" \
        -e "s/^Vvdd.*/Vvdd  VDD  0 ${vdd}/" \
        -e "/^[Vv]ck/s/PULSE(0 3\.3/PULSE(0 ${vdd}/" \
        -e "s/^Vvin1.*/Vvin1 VIN1 0 ${vin1}/" \
        -e "s/^Vvin2.*/Vvin2 VIN2 0 ${vcm}/" \
        -e "/^[Vv]ckl/s/2\.8n/${ckl}n/" \
        "$NETLIST"
    cat <<EOF
.temp ${temp}
.options reltol=1e-4 vntol=1e-9
.control
save v(vout1) v(vout2) v(ck) v(ckl)
tran 0.01n 20n
meas tran tdelay trig v(ck) val=${vcm} rise=1 targ v(vout1) val=${vcm} fall=1
meas tran v1end find v(vout1) at=18n
meas tran v2end find v(vout2) at=18n
echo RESULT ${tag} delay=\$&tdelay v1end=\$&v1end v2end=\$&v2end
.endc
.end
EOF
  } > "$deck"
}

# ---- the matrix -------------------------------------------------------------
# tag                         section  temp  vdd   od        ckl
gen_deck tt_od0p5lsb_ckl2p8   typical   27   3.30  0.006457  2.8
gen_deck tt_od0p1mv_ckl2p8    typical   27   3.30  0.0001    2.8
gen_deck ss_od0p5lsb_ckl2p6   ss       125   2.97  0.006457  2.6
gen_deck ss_od0p5lsb_ckl2p8   ss       125   2.97  0.006457  2.8
gen_deck ss_od0p5lsb_ckl3p0   ss       125   2.97  0.006457  3.0
gen_deck ss_od0p1mv_ckl2p8    ss       125   2.97  0.0001    2.8
gen_deck ff_od0p5lsb_ckl2p6   ff       -40   3.63  0.006457  2.6
gen_deck ff_od0p5lsb_ckl2p8   ff       -40   3.63  0.006457  2.8
gen_deck ff_od0p5lsb_ckl3p0   ff       -40   3.63  0.006457  3.0
gen_deck ff_od0p1mv_ckl2p8    ff       -40   3.63  0.0001    2.8

# ---- run + collect ----------------------------------------------------------
: > "$SUMMARY"
for deck in "$OUTDIR"/deck_*.spice; do
  tag=$(basename "$deck" .spice); tag=${tag#deck_}
  echo "--- running $tag"
  "$NGSPICE" -b "$deck" > "$OUTDIR/log_${tag}.txt" 2>&1 || true
  line=$(grep "^RESULT" "$OUTDIR/log_${tag}.txt" || true)
  if [ -n "$line" ] && ! grep -q "delay=$" <<< "$line"; then
    echo "$line" >> "$SUMMARY"
  else
    echo "RESULT ${tag} FAILED-TO-RESOLVE (no VOUT1 fall; check log_${tag}.txt / waveforms)" >> "$SUMMARY"
  fi
done

echo ""
echo "================== COMP-ALT-10 DELAY SUMMARY =================="
cat "$SUMMARY"
echo "==============================================================="
echo "Spec: delay < 2ns from CK edge. v1end~0 and v2end~VDD confirm a"
echo "clean decision. FAILED lines at ckl2p8 = the design CKL does not"
echo "survive that corner; see which probe (2.6/3.0) works instead."
