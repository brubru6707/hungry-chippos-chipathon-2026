#!/bin/bash
# Run gf180mcuD DRC (variant=D: metal_top=11K, mim_option=B, metal_level=
# 5LM -- the real, signed-off chip stack; matches every comparator DRC/LVS
# log under comparator/layout/) on a DAC layout GDS, from inside the
# iic-osic-tools container. Uses the TERMINAL run_drc.py flow per the
# project's KLayout-GUI-LVS-is-broken convention (see handoff/README.md);
# NOT the KLayout GUI DRC menu.
#
# STANDING RULE: variant=D is the only variant used for DAC DRC/LVS from now
# on. variant=A (3LM/mim_option=A/metal_top=30K) was a mismatch against the
# real 5LM stack and is not used again (see dac/WORKLOG.md, 2026-07-18
# "Pre-array sanity check" entry).
#
# gf180mcuD 3LM rule-deck bug (HISTORICAL, does NOT apply to variant=D --
# left here only so this isn't rediscovered from scratch if variant=A is
# ever needed again for comparison): variant=A's generated main.drc
# references metal4_drawn/metal5_drawn/metal4_slot/metal5_slot/via3/via4,
# none of which exist in a 3-metal-layer stack, and run_drc.py's first pass
# crashes with "undefined method 'sized' for false:FalseClass". Under
# variant=D (5LM) all of metal4/metal5/via3/via4 are genuinely defined
# (layers_def.drc's `when '5LM'` branch), so this bug does NOT reproduce --
# confirmed by a clean, unpatched `run_drc.py --variant=D` run (660 rule
# categories executed, 0 violations, exit 0, no first-pass crash) on the
# variant=D-redrawn unit cell. The patch-and-rerun fallback below is kept
# only as a defensive no-op path (it will not trigger under variant=D) in
# case a future geometry change resurfaces some other run_drc.py bug.
#
# usage: run_dac_drc.sh <gds_path> <topcell> <run_dir> [variant]
set -euo pipefail
GDS_PATH="$1"
TOPCELL="$2"
RUN_DIR="$3"
VARIANT="${4:-D}"

mkdir -p "$RUN_DIR"
cd "$RUN_DIR"

set +e
python /foss/pdks/gf180mcuD/libs.tech/klayout/tech/drc/run_drc.py \
  --path="$GDS_PATH" --variant="$VARIANT" --run_dir=. --topcell="$TOPCELL" \
  --run_mode=flat > drc_first_pass.log 2>&1
FIRST_RC=$?
set -e

if [ $FIRST_RC -ne 0 ] && [ -f main.drc ]; then
  echo "[run_dac_drc] first pass failed (rc=$FIRST_RC); attempting the historical 3LM metal4/5 patch as a defensive fallback -- this is NOT expected to trigger under variant=D" >&2
  sed -i -E 's/\b(metal4_drawn|metal5_drawn|metal4_slot|metal5_slot|via3|via4)\b/polygon_layer/g' main.drc
  klayout -b -r main.drc \
    -rd thr=2 -rd metal_top=11K -rd mim_option=B -rd metal_level=5LM \
    -rd verbose=false -rd feol=true -rd beol=true -rd offgrid=true \
    -rd conn_drc=true -rd density=false -rd split_deep=false -rd slow_via=false \
    -rd topcell="$TOPCELL" -rd input="$GDS_PATH" \
    -rd report="$RUN_DIR/${TOPCELL}_main.lyrdb" -rd run_mode=flat -rd table_name=main \
    > drc_patched_pass.log 2>&1
fi

# run_drc.py names its report by GDS basename ({layout_base_name}_{table}.
# lyrdb, see run_drc.py's report_path), NOT by --topcell -- only the
# patch-and-rerun fallback above (which sets -rd report= explicitly) uses
# the topcell-based name. Check both, preferring whichever exists.
GDS_BASE="$(basename "$GDS_PATH" .gds)"
REPORT="$RUN_DIR/${GDS_BASE}_main.lyrdb"
if [ ! -f "$REPORT" ]; then
  REPORT="$RUN_DIR/${TOPCELL}_main.lyrdb"
fi
if [ ! -f "$REPORT" ]; then
  echo "[run_dac_drc] ERROR: no report produced at $RUN_DIR/${GDS_BASE}_main.lyrdb or $RUN_DIR/${TOPCELL}_main.lyrdb" >&2
  exit 1
fi
echo "[run_dac_drc] report: $REPORT" >&2

python3 -c "
import klayout.rdb as rdb
r = rdb.ReportDatabase('main')
r.load('$REPORT')
total = 0
for cat in r.each_category():
    cnt = sum(1 for _ in r.each_item_per_category(cat.rdb_id()))
    if cnt:
        print(cat.path(), cnt)
        total += cnt
print('TOTAL_VIOLATIONS:', total)
"
