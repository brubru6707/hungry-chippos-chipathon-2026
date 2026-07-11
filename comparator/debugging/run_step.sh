#!/bin/bash
# usage: run_step.sh <stepname>
set -e
cd /Users/brrodrig/Documents/FUQ_WINDOWS/bat_cave/hungry-chippos-chipathon-2026/comparator/layout
cp strongarm.gds "backups/strongarm_backup_pre_${1}_$(date +%Y-%m-%d_%Hh%Mm%s).gds"
docker exec f53d67a84b8b bash -lc "
python3 /foss/designs/comparator/debugging/edit_step.py $1 2>&1 | tail -1
LVS_RUN_DIR=/foss/designs/comparator/layout/klayout_lvs_run_TMP
cp /foss/designs/comparator/layout/strongarm.gds \$LVS_RUN_DIR/strongarm.gds
cd \$LVS_RUN_DIR
python3 /foss/designs/designs/scripts/lvs_strip_gds_labels.py strongarm.gds >/dev/null
python /foss/pdks/gf180mcuD/libs.tech/klayout/tech/lvs/run_lvs.py \
  --layout=strongarm_lvs.gds --netlist=strongarm_lvs.spice --variant=D \
  --run_dir=. --topcell=strongarm --lvs_sub=VSS --run_mode=flat \
  --schematic_simplify 2>&1 | grep -E 'ERROR|CONGRATULATIONS' | head -1
python3 /foss/designs/comparator/debugging/dump_devices.py 2>/dev/null | grep -v '^\[INFO\]'"
