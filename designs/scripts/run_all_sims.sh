#!/bin/bash
# REP-3: master regression runner. Regenerates every generated layout and
# re-runs the full physical sign-off suite (DRC + LVS on all blocks and
# the chip, plus chip density/antenna), printing one PASS/FAIL line per
# check. Heavy electrical sweeps (Gate 3: 256 ngspice runs) only with
# --full.
#
# Run INSIDE the container (see REPRODUCIBILITY.md section 1):
#   docker exec -e HOME=/headless -e USER=headless \
#     -e PATH=/foss/tools/klayout:/usr/local/bin:/usr/bin:/bin \
#     sar_sim bash /foss/designs/designs/scripts/run_all_sims.sh [--full]
set -u
cd /foss/designs
S=designs/scripts
FAILS=0

say() { printf '%-52s %s\n' "$1" "$2"; }

check_drc() {  # name gds topcell rundir
  local out
  out=$(bash $S/run_dac_drc.sh "$2" "$3" "$4" D 2>&1 | grep TOTAL_VIOLATIONS)
  if [ "$out" = "TOTAL_VIOLATIONS: 0" ]; then say "DRC $1" PASS
  else say "DRC $1" "FAIL ($out)"; FAILS=$((FAILS+1)); fi
}

check_lvs() {  # name gds topcell ref rundir
  bash $S/run_dac_lvs.sh "$2" "$3" "$4" "$5" D VSS >/dev/null 2>&1
  if grep -q 'Netlists match' "$5/lvs_run.log" 2>/dev/null; then say "LVS $1" PASS
  else say "LVS $1" FAIL; FAILS=$((FAILS+1)); fi
}

echo "== regenerate =="
python3 $S/gen_sar_layout.py >/dev/null 2>&1            && say "gen flat SAR" OK || { say "gen flat SAR" FAIL; FAILS=$((FAILS+1)); }
python3 $S/gen_sar_layout.py --fold 3 >/dev/null 2>&1   && say "gen folded SAR" OK || { say "gen folded SAR" FAIL; FAILS=$((FAILS+1)); }
python3 $S/gen_adc_glue_layout.py >/dev/null 2>&1       && say "gen adc_glue" OK || { say "gen adc_glue" FAIL; FAILS=$((FAILS+1)); }
python3 $S/gen_adc_chip_ref.py >/dev/null 2>&1          && say "gen chip LVS ref" OK || { say "gen chip LVS ref" FAIL; FAILS=$((FAILS+1)); }
python3 $S/gen_adc_chip_top.py >/dev/null 2>&1          && say "gen chip top (self-checks)" OK || { say "gen chip top (self-checks)" FAIL; FAILS=$((FAILS+1)); }

# run_dac_{drc,lvs}.sh cd into the run dir before invoking the deck --
# every path they receive must be ABSOLUTE
D=/foss/designs
echo "== block sign-off =="
check_drc "DAC"        $D/dac/layout/dac_top_floorplan.gds dac_top_floorplan /tmp/ras_dac_drc
check_lvs "DAC"        $D/dac/layout/dac_top_floorplan.gds dac_top_floorplan $D/dac/layout/dac_top_ref.spice /tmp/ras_dac_lvs
check_drc "comparator" $D/comparator/layout/strongarm.gds strongarm /tmp/ras_cmp_drc
check_drc "SAR folded" $D/sar_logic/layout/sar_folded.gds sar_logic /tmp/ras_sarf_drc
check_lvs "SAR folded" $D/sar_logic/layout/sar_folded.gds sar_logic $D/sar_logic/layout/refs/sar_logic_ref.spice /tmp/ras_sarf_lvs
check_drc "adc_glue"   $D/adc_top/layout/adc_glue.gds adc_glue /tmp/ras_glue_drc
check_lvs "adc_glue"   $D/adc_top/layout/adc_glue.gds adc_glue $D/adc_top/layout/refs/adc_glue_ref.spice /tmp/ras_glue_lvs

echo "== chip sign-off =="
check_drc "chip adc_top" $D/adc_top/layout/adc_chip_top.gds adc_top /tmp/ras_chip_drc
check_lvs "chip adc_top" $D/adc_top/layout/adc_chip_top.gds adc_top $D/adc_top/layout/refs/adc_top_ref.spice /tmp/ras_chip_lvs
mkdir -p /tmp/ras_chip_dens && (cd /tmp/ras_chip_dens && python /foss/pdks/gf180mcuD/libs.tech/klayout/tech/drc/run_drc.py \
  --path=/foss/designs/adc_top/layout/adc_chip_top.gds --variant=D --run_dir=. \
  --topcell=adc_top --run_mode=flat --density_only 2>&1 | grep -q '\[ERROR\]') \
  && { say "chip density" FAIL; FAILS=$((FAILS+1)); } || say "chip density" PASS
mkdir -p /tmp/ras_chip_ant && (cd /tmp/ras_chip_ant && python /foss/pdks/gf180mcuD/libs.tech/klayout/tech/drc/run_drc.py \
  --path=/foss/designs/adc_top/layout/adc_chip_top.gds --variant=D --run_dir=. \
  --topcell=adc_top --run_mode=flat --antenna_only 2>&1 | grep -q '\[ERROR\]') \
  && { say "chip antenna" FAIL; FAILS=$((FAILS+1)); } || say "chip antenna" PASS

if [ "${1:-}" = "--full" ]; then
  echo "== Gate 3 TT sweep (256 runs, hours) =="
  python3 $S/gen_adc_sweep_tt.py adc_top/sim/sweep_tt_regress typical
  (cd adc_top/sim/sweep_tt_regress && ls code_*.spice | xargs -P 8 -I{} sh -c 'ngspice -b {} > {}.log 2>&1')
  python3 $S/check_adc_sweep.py adc_top/sim/sweep_tt_regress && say "Gate 3 sweep" PASS \
    || { say "Gate 3 sweep" FAIL; FAILS=$((FAILS+1)); }
fi

echo
if [ $FAILS -eq 0 ]; then echo "ALL CHECKS PASS"; else echo "$FAILS CHECK(S) FAILED"; exit 1; fi
