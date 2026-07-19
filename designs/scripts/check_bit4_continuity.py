#!/usr/bin/env python3
"""Flat geometric continuity checker for the bit-4 routing template.

Builds connected components directly from the drawn GDS geometry (merged
same-layer polygons bridged by overlapping via cuts spanning the two
adjacent metal pads), independent of the LVS/DRC toolchain's own net
naming. For each of the 4 bit-4 nets, confirms the two named endpoints
(a label or child-cell pin coordinate) fall in the same connected
component -- i.e. are one net, not two separate floating pieces.
"""
import sys
import klayout.db as db

GDS = sys.argv[1] if len(sys.argv) > 1 else \
    "/foss/designs/dac/layout/dac_top_floorplan.gds"
DBU = 0.001

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

# Union-Find over (metal_level, polygon_index) nodes.
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

checks = [
    ("B4 label", (-230.0, -16.0), 2, "NAND2<4> A pin", (-255.66, -0.49), 1),
    ("SAMPLE_N pin", (88.33, -7.471), 2, "NAND2<4> B pin", (-243.66, -0.49), 1),
    ("NAND2<4> Y pin", (-241.00, -1.60), 1, "driver<4> input pin", (-143.53, -11.652), 3),
    ("driver<4> VOUT pin", (-139.08, 0.0), 3, "B4 rail landing", (-62.85, 0.00), 2),
]

all_pass = True
for name_a, pt_a, layer_a, name_b, pt_b, layer_b in checks:
    ca = comp_of(*pt_a, layer_a)
    cb = comp_of(*pt_b, layer_b)
    status = "PASS (same net)" if ca is not None and ca == cb else "FAIL (separate/missing)"
    if ca is None or cb is None or ca != cb:
        all_pass = False
    print(f"{name_a} {pt_a}@M{layer_a} <-> {name_b} {pt_b}@M{layer_b}: "
          f"comp_a={ca} comp_b={cb} -> {status}")

print()
print("ALL PASS" if all_pass else "SOME CHECKS FAILED")
sys.exit(0 if all_pass else 1)
