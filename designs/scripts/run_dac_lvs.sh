#!/bin/bash
# Run gf180mcuD LVS (default variant=D: metal_top=11K, mim_option=B,
# metal_level=5LM -- the real, signed-off chip stack) on a DAC layout GDS
# against a reference SPICE netlist, from inside the iic-osic-tools
# container. Uses the TERMINAL run_lvs.py flow per the project's
# KLayout-GUI-LVS-is-broken convention (see handoff/README.md); NOT the
# KLayout GUI LVS menu. Mirrors run_dac_drc.sh's structure/conventions.
#
# STANDING RULE: variant=D is the only variant used for DAC DRC/LVS from now
# on (see dac/WORKLOG.md, 2026-07-18 "Pre-array sanity check" entry).
#
# IMPORTANT netlist-syntax gotcha (do not re-derive): the reference netlist
# MUST use native SPICE primitive element syntax for the cap
# (`C1 p1 p2 cap_mim_2f0fF W=... L=... M=...`), NOT an `X`-subcircuit call
# (`XC1 p1 p2 cap_mim_2f0fF ...`). gf180mcu.lvs's SubcircuitModelsReader
# delegate only special-cases native `C`/`R` primitive cards
# (element(ele='C', ...) in custom_classes.lvs) -- an X-call to an
# undefined subcircuit is silently dropped, extracting to 0 devices on the
# reference side, which "passes" LVS only because BOTH sides show 0
# devices (a false pass, not a real check).
#
# usage: run_dac_lvs.sh <gds_path> <topcell> <netlist_path> <run_dir> [variant] [lvs_sub]
set -euo pipefail
GDS_PATH="$1"
TOPCELL="$2"
NETLIST_PATH="$3"
RUN_DIR="$4"
VARIANT="${5:-D}"
LVS_SUB="${6:-}"

mkdir -p "$RUN_DIR"
cd "$RUN_DIR"

cp "$GDS_PATH" "${TOPCELL}.gds"
python3 /foss/designs/designs/scripts/lvs_strip_gds_labels.py "${TOPCELL}.gds" > strip_labels.log 2>&1
rm "${TOPCELL}.gds"
LVS_GDS="${RUN_DIR}/${TOPCELL}_lvs.gds"

cp "$NETLIST_PATH" "${TOPCELL}_lvs.spice"
LVS_NETLIST="${RUN_DIR}/${TOPCELL}_lvs.spice"

LVS_SUB_ARGS=()
if [ -n "$LVS_SUB" ]; then
  LVS_SUB_ARGS=(--lvs_sub="$LVS_SUB")
fi

set +e
python /foss/pdks/gf180mcuD/libs.tech/klayout/tech/lvs/run_lvs.py \
  --layout="$LVS_GDS" \
  --netlist="$LVS_NETLIST" \
  --variant="$VARIANT" \
  --run_dir=. \
  --topcell="$TOPCELL" \
  --run_mode=flat \
  --schematic_simplify \
  "${LVS_SUB_ARGS[@]}" \
  > lvs_run.log 2>&1
LVS_RC=$?
set -e

echo "[run_dac_lvs] run_lvs.py exit code: $LVS_RC" >&2
grep -iE "congratulations|don't match|error" lvs_run.log >&2 || true

LVSDB="${RUN_DIR}/${TOPCELL}_lvs.lvsdb"
if [ ! -f "$LVSDB" ]; then
  echo "[run_dac_lvs] ERROR: no .lvsdb produced at $LVSDB" >&2
  exit 1
fi

python3 -c "
import klayout.db as db
l2n = db.LayoutVsSchematic()
l2n.read('$LVSDB')
# NOTE: l2n.netlist is a method (call it); l2n.reference is a plain
# attribute (do NOT call it) -- confirmed empirically against this
# container's klayout.db binding, inconsistent method/property naming.
layout_nl = l2n.netlist()
ref_nl = l2n.reference
for label, nl in (('LAYOUT', layout_nl), ('REFERENCE', ref_nl)):
    for circuit in nl.each_circuit():
        n = sum(1 for _ in circuit.each_device())
        print(f'{label} circuit={circuit.name} device_count={n}')
        for d in circuit.each_device():
            print(f'   device={d.expanded_name()} class={d.device_class().name}')
"
