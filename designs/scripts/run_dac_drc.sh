#!/bin/bash
# Run gf180mcuD DRC (variant=A, mim_option=A/3LM) on a DAC layout GDS, from
# inside the iic-osic-tools container. Uses the TERMINAL run_drc.py flow per
# the project's KLayout-GUI-LVS-is-broken convention (see handoff/README.md);
# NOT the KLayout GUI DRC menu.
#
# gf180mcuD bug workaround: the generated main.drc for variant=A (3LM)
# references metal4_drawn/metal5_drawn/metal4_slot/metal5_slot/via3/via4,
# none of which exist in a 3-metal-layer stack -- run_drc.py's first pass
# crashes with "undefined method 'sized' for false:FalseClass". This is a
# rule-deck bug independent of the design under test (metal_top=30K+mim_
# option=A always forces METAL_LEVEL=3LM, which has no metal4/5 at all), not
# something introduced by our geometry. Workaround: let run_drc.py generate
# main.drc, patch the run-local copy only (never the golden PDK source) to
# replace those always-undefined identifiers with an empty region
# (`polygon_layer`), then invoke klayout directly on the patched deck with
# the same -rd switches run_drc.py would have used.
#
# usage: run_dac_drc.sh <gds_path> <topcell> <run_dir>
set -euo pipefail
GDS_PATH="$1"
TOPCELL="$2"
RUN_DIR="$3"

mkdir -p "$RUN_DIR"
cd "$RUN_DIR"

set +e
python /foss/pdks/gf180mcuD/libs.tech/klayout/tech/drc/run_drc.py \
  --path="$GDS_PATH" --variant=A --run_dir=. --topcell="$TOPCELL" \
  --run_mode=flat > drc_first_pass.log 2>&1
FIRST_RC=$?
set -e

if [ $FIRST_RC -ne 0 ] && [ -f main.drc ]; then
  echo "[run_dac_drc] first pass hit the known 3LM metal4/5 rule-deck bug; patching run-local main.drc" >&2
  sed -i -E 's/\b(metal4_drawn|metal5_drawn|metal4_slot|metal5_slot|via3|via4)\b/polygon_layer/g' main.drc
  klayout -b -r main.drc \
    -rd thr=2 -rd metal_top=30K -rd mim_option=A -rd metal_level=3LM \
    -rd verbose=false -rd feol=true -rd beol=true -rd offgrid=true \
    -rd conn_drc=true -rd density=false -rd split_deep=false -rd slow_via=false \
    -rd topcell="$TOPCELL" -rd input="$GDS_PATH" \
    -rd report="$RUN_DIR/${TOPCELL}_main.lyrdb" -rd run_mode=flat -rd table_name=main \
    > drc_patched_pass.log 2>&1
fi

REPORT="$RUN_DIR/${TOPCELL}_main.lyrdb"
if [ ! -f "$REPORT" ]; then
  echo "[run_dac_drc] ERROR: no report produced at $REPORT" >&2
  exit 1
fi

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
