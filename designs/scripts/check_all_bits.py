#!/usr/bin/env python3
"""Flat geometric continuity + cross-bit distinctness checker, generalizing
check_bit4_continuity.py to every bit routed so far.

Builds connected components directly from the drawn GDS geometry (merged
same-layer polygons bridged by overlapping via cuts spanning the two
adjacent metal pads), independent of the LVS/DRC toolchain's own net
naming.  For each routed bit's 4 nets + supply, confirms the named
endpoints fall in the same connected component (continuity).  Separately,
confirms that NO two nets that should be electrically distinct ever share
a component (cross-bit/cross-net distinctness -- this is where a
B4<->GND or B0<->B7 style short would show up).
"""
import sys
import klayout.db as db

GDS = sys.argv[1] if len(sys.argv) > 1 else \
    "/foss/designs/dac/layout/dac_top_floorplan.gds"
DBU = 0.001

ROUTED_BITS = [0, 1, 2, 3, 4, 5, 6]  # bit 7 deferred, not routed this pass

RAIL_Y = {0: 57.36, 1: -57.36, 2: -38.24, 3: -19.12, 4: 0.00,
          5: 19.12, 6: 76.48, 7: -76.48}
NAND2_X = lambda b: -208.0 - 12.0 * b
DRIVER_X = lambda b: -94.0 - 12.0 * b
GATE_DY = {0: -5.352, 1: -5.772, 2: -6.612, 3: -8.292, 4: -11.652,
           5: -18.372, 6: -31.812, 7: -58.692}
VOUTX = {0: 2.920, 1: 2.920, 2: 2.920, 3: 2.920, 4: 2.920, 5: 2.920,
         6: 2.920, 7: 5.730}
NAND_VDD_DY, NAND_GND_DY = 3.00, -10.75
DRV_VDD_DY = {0: 2.930, 1: 3.770, 2: 5.450, 3: 8.810, 4: 15.530,
              5: 28.970, 6: 55.850, 7: 55.850}
DRV_GND_DY = {0: -6.052, 1: -6.472, 2: -7.312, 3: -8.992, 4: -12.352,
              5: -19.072, 6: -32.512, 7: -59.392}
RAIL_X = -62.85

layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()

METAL = {1: (34, 0), 2: (36, 0), 3: (42, 0), 4: (46, 0), 5: (81, 0)}
VIA = {1: (35, 0), 2: (38, 0), 3: (40, 0), 4: (41, 0)}  # via{n} joins metal{n}<->metal{n+1}


def region(layer_num, datatype):
    li = layout.layer(layer_num, datatype)
    r = db.Region(top.begin_shapes_rec(li))
    r.merge()
    return r


metal_regions = {m: region(*ld) for m, ld in METAL.items()}
via_regions = {v: region(*ld) for v, ld in VIA.items()}

parent = {}


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb


polys = {m: list(r.each_merged()) for m, r in metal_regions.items()}
for m in polys:
    for i in range(len(polys[m])):
        parent[(m, i)] = (m, i)

for v, vr in via_regions.items():
    low, high = v, v + 1
    if low not in polys or high not in polys:
        continue
    for cut in vr.each_merged():
        cut_region = db.Region(cut)
        low_hits = [i for i, p in enumerate(polys[low]) if not cut_region.and_(db.Region(p)).is_empty()]
        high_hits = [i for i, p in enumerate(polys[high]) if not cut_region.and_(db.Region(p)).is_empty()]
        for li in low_hits:
            for hi in high_hits:
                union((low, li), (high, hi))


def comp_of(x_um, y_um, metal_level):
    pt = db.Point(int(round(x_um / DBU)), int(round(y_um / DBU)))
    for i, p in enumerate(polys[metal_level]):
        if p.inside(pt):
            return find((metal_level, i))
    return None


# ---------------------------------------------------------------------
# Per-bit named points, in top-level coordinates.
def bit_points(bit):
    ry, nx, dxv = RAIL_Y[bit], NAND2_X(bit), DRIVER_X(bit)
    return {
        "B_label": ((nx + 26.0, ry - 16.0), 2),
        "nand_a": ((nx + 0.34, ry - 0.49), 1),
        "nand_b": ((nx + 12.34, ry - 0.49), 1),
        "nand_y": ((nx + 15.00, ry - 1.60), 1),
        "gate": ((dxv - 1.530, ry + GATE_DY[bit]), 3),
        "drv_out": ((dxv + VOUTX[bit], ry), 3),
        "rail": ((RAIL_X, ry), 2),
        "nand_vdd": ((nx - 0.23, ry + NAND_VDD_DY), 1),
        "nand_gnd": ((nx - 2.00, ry + NAND_GND_DY), 1),
        "drv_vdd": ((dxv - 0.23, ry + DRV_VDD_DY[bit]), 2),
        "drv_gnd": ((dxv - 0.21, ry + DRV_GND_DY[bit]), 2),
    }


SAMPLE_N_PIN = ((88.33, -7.471), 2)
VDD_BACKBONE = ((-280.0, 124.0), 5)
GND_BACKBONE = ((-280.0, -128.0), 5)

all_pass = True

print("=== CONTINUITY (each bit's 4 signal nets + supply) ===")
for bit in ROUTED_BITS:
    pts = bit_points(bit)
    checks = [
        (f"B{bit} label", pts["B_label"], f"NAND2<{bit}> A pin", pts["nand_a"]),
        ("SAMPLE_N pin", SAMPLE_N_PIN, f"NAND2<{bit}> B pin", pts["nand_b"]),
        (f"NAND2<{bit}> Y pin", pts["nand_y"], f"driver<{bit}> gate pin", pts["gate"]),
        (f"driver<{bit}> VOUT pin", pts["drv_out"], f"B{bit} rail landing", pts["rail"]),
        (f"nand_vdd<{bit}>", pts["nand_vdd"], "VDD backbone", VDD_BACKBONE),
        (f"nand_gnd<{bit}>", pts["nand_gnd"], "GND backbone", GND_BACKBONE),
        (f"drv_vdd<{bit}>", pts["drv_vdd"], "VDD backbone", VDD_BACKBONE),
        (f"drv_gnd<{bit}>", pts["drv_gnd"], "GND backbone", GND_BACKBONE),
    ]
    for name_a, (pt_a, la), name_b, (pt_b, lb) in checks:
        ca, cb = comp_of(*pt_a, la), comp_of(*pt_b, lb)
        ok = ca is not None and ca == cb
        all_pass &= ok
        status = "PASS" if ok else "FAIL (separate/missing)"
        print(f"  {name_a} {pt_a}@M{la} <-> {name_b} {pt_b}@M{lb}: {status}")

print()
print("=== CROSS-BIT / CROSS-NET DISTINCTNESS ===")
# Build one representative component per intended-distinct net.
nets = {}
for bit in ROUTED_BITS:
    pts = bit_points(bit)
    nets[f"B{bit}"] = comp_of(*pts["B_label"][0], pts["B_label"][1])
    nets[f"NANDY{bit}"] = comp_of(*pts["nand_y"][0], pts["nand_y"][1])
    nets[f"RAIL{bit}"] = comp_of(*pts["drv_out"][0], pts["drv_out"][1])
nets["SAMPLE_N"] = comp_of(*SAMPLE_N_PIN[0], SAMPLE_N_PIN[1])
nets["VDD"] = comp_of(*VDD_BACKBONE[0], VDD_BACKBONE[1])
nets["GND"] = comp_of(*GND_BACKBONE[0], GND_BACKBONE[1])

names = list(nets)
shorts = []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b_ = names[i], names[j]
        ca, cb = nets[a], nets[b_]
        if ca is None or cb is None:
            continue
        if ca == cb:
            shorts.append((a, b_))

if shorts:
    all_pass = False
    print(f"  {len(shorts)} UNEXPECTED MERGE(S) FOUND:")
    for a, b_ in shorts:
        print(f"    {a} <-> {b_}")
else:
    print(f"  All {len(names)} nets ({', '.join(names)}) are pairwise distinct components. PASS")

print()
print("ALL PASS" if all_pass else "SOME CHECKS FAILED")
sys.exit(0 if all_pass else 1)
