#!/usr/bin/env python3
"""VDD/GND reach check for bit-4's NAND2 and driver cells, reusing the
same flat geometric connectivity builder as check_bit4_continuity.py."""
import sys

src = open("/foss/designs/designs/scripts/check_bit4_continuity.py").read()
src = src.split("checks = [")[0]
ns = {}
exec(compile(src, "chk", "exec"), ns)
comp_of = ns["comp_of"]

checks = [
    ("nand_vdd pin", (-256.23, 3.00), 1, "VDD backbone", (-280.0, 124.0), 5),
    ("nand_gnd pin", (-258.00, -10.75), 1, "GND backbone", (-280.0, -128.0), 5),
    ("drv_vdd pin", (-142.23, 15.53), 2, "VDD backbone", (-280.0, 124.0), 5),
    ("drv_gnd pin", (-142.21, -12.352), 2, "GND backbone", (-280.0, -128.0), 5),
]
all_pass = True
for name_a, pt_a, layer_a, name_b, pt_b, layer_b in checks:
    ca = comp_of(*pt_a, layer_a)
    cb = comp_of(*pt_b, layer_b)
    ok = ca is not None and ca == cb
    all_pass = all_pass and ok
    status = "PASS (same net)" if ok else "FAIL"
    print(f"{name_a} {pt_a}@M{layer_a} <-> {name_b} {pt_b}@M{layer_b}: "
          f"comp_a={ca} comp_b={cb} -> {status}")

print()
print("ALL PASS" if all_pass else "SOME CHECKS FAILED")
sys.exit(0 if all_pass else 1)
