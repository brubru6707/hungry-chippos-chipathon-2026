#!/usr/bin/env python3
"""REP-5: CI library check (runs on a plain GitHub runner with
`pip install klayout numpy` — no PDK, no container).

Scope (honest): this does NOT re-run DRC/LVS (those need the PDK decks
and run in the container, see REPRODUCIBILITY.md). It guards the
repo's *artifacts* against silent corruption/regression:
  1. every signed-off GDS loads, has the expected topcell and bbox;
  2. every native-element LVS reference has the exact device count its
     sign-off recorded (an X-call sneaking in would change the count);
  3. the Gate-3 sweep CSV still yields ENOB >= 7.0 through calc_enob;
  4. every script in designs/scripts compiles.
Run from the repo root: python3 designs/scripts/ci_library_check.py
"""
import glob
import os
import py_compile
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FAILS = []


def say(name, ok, detail=""):
    print("%-46s %s %s" % (name, "PASS" if ok else "FAIL", detail))
    if not ok:
        FAILS.append(name)


def check_gds():
    import klayout.db as db
    specs = [
        ("dac/layout/dac_top_floorplan.gds", "dac_top_floorplan", 443.0, 270.2),
        ("comparator/layout/strongarm.gds", "strongarm", 83.25, 49.63),
        ("sar_logic/layout/sar_cells.gds", "sar_logic", 1219.58, 45.66),
        ("sar_logic/layout/sar_folded.gds", "sar_logic", 457.93, 130.23),
        ("adc_top/layout/adc_glue.gds", "adc_glue", 42.54, 17.66),
        ("adc_top/layout/adc_chip_top.gds", "adc_top", 514.25, 549.7),
    ]
    for path, topname, w, h in specs:
        try:
            ly = db.Layout()
            ly.read(os.path.join(ROOT, path))
            top = ly.cell(topname)
            b = top.bbox()
            ok = (abs(b.width() * ly.dbu - w) < 0.5
                  and abs(b.height() * ly.dbu - h) < 0.5)
            say("gds %s" % path, ok,
                "" if ok else "(%.2fx%.2f)" % (b.width() * ly.dbu, b.height() * ly.dbu))
        except Exception as e:
            say("gds %s" % path, False, str(e)[:60])


def count_devices(path):
    n = 0
    for line in open(os.path.join(ROOT, path)):
        if re.match(r"^[MC]\S*\s", line.strip(), re.I) and not line.strip().startswith("*"):
            n += 1
    return n


def check_refs():
    for path, expect in [
        ("dac/layout/dac_top_ref.spice", 377),
        ("comparator/schematic/strongarm.spice", 11),
        ("sar_logic/layout/refs/sar_logic_ref.spice", 12),   # leaf/dff cards
        ("adc_top/layout/refs/adc_glue_ref.spice", 6),    # inv 2 + nor2 4
        ("adc_top/layout/refs/adc_top_ref.spice", 400),      # 76 M + 324 C
    ]:
        n = count_devices(path)
        say("ref %s" % path, n == expect, "(%d cards, expect %d)" % (n, expect))


def check_enob():
    out = subprocess.run(
        [sys.executable, os.path.join(ROOT, "designs/scripts/calc_enob.py"),
         "--transfer", os.path.join(ROOT, "adc_top/sim/sweep_tt_fine2/sweep_codes.csv"),
         "--vlo", "0.70", "--vhi", "3.25"],
        capture_output=True, text=True)
    m = re.search(r"ENOB = ([\d.]+)", out.stdout)
    ok = m is not None and float(m.group(1)) >= 7.0
    say("ENOB regression (>=7.0)", ok, m.group(0) if m else out.stderr[:60])


def check_compile():
    bad = []
    for f in glob.glob(os.path.join(ROOT, "designs/scripts/*.py")):
        try:
            py_compile.compile(f, doraise=True)
        except Exception:
            bad.append(os.path.basename(f))
    say("scripts compile", not bad, ",".join(bad))


def main():
    check_gds()
    check_refs()
    check_enob()
    check_compile()
    print()
    if FAILS:
        print("%d CHECK(S) FAILED" % len(FAILS))
        sys.exit(1)
    print("ALL LIBRARY CHECKS PASS")


if __name__ == "__main__":
    main()
