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

ROUTED_BITS = list(range(8))

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

# Extracted top-level pin accesses for the placed inv1/TG instances.  The
# third tuple member is the actual access metal, not a label-purpose guess.
TG = {
    "sample_n": ((88.33, -7.471), 2), "sample": ((106.33, -8.08), 2),
    "vin": ((97.00, -8.271), 3), "dac_top": ((105.79, -8.98), 4),
}
INV1 = {
    "vdd": ((111.77, 21.79), 2), "gnd": ((111.79, 11.518), 2),
    "vin": ((110.47, 12.218), 3), "vout": ((114.94, 12.918), 3),
}
SAMPLE_LABEL = TG["sample"]
VIN_LABEL = TG["vin"]
DAC_TOP_MESH = ((0.0, 0.0), 5)

layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()

METAL = {1: (34, 0), 2: (36, 0), 3: (42, 0), 4: (46, 0), 5: (81, 0)}
VIA = {1: (35, 0), 2: (38, 0), 3: (40, 0), 4: (41, 0)}  # via{n} joins metal{n}<->metal{n+1}
# A via4 cut inside FuseTop is the MIM top-plate contact, not an M4--M5
# interconnect.  The Metal4 bottom electrode geometrically lies under that
# plate, so treating such cuts as ordinary vias would short every bottom
# rail to the DAC_TOP M5 mesh in this geometry-only model.
FUSETOP = (75, 0)
# A cut is a connection only when it is actually enclosed by both of its
# adjacent metals.  In particular, do *not* infer a connection merely from
# an upper metal polygon passing above a lower-metal route.  10 nm is the
# smallest relevant generic enclosure in the 5LM deck and is deliberately
# below every route pad used by this generator (0.40 um pads on 0.26 um
# cuts); the PDK DRC remains the authority for the full rule set.
MIN_CUT_ENC_UM = 0.01


def region(layer_num, datatype):
    li = layout.layer(layer_num, datatype)
    r = db.Region(top.begin_shapes_rec(li))
    r.merge()
    return r


metal_regions = {m: region(*ld) for m, ld in METAL.items()}
via_regions = {v: region(*ld) for v, ld in VIA.items()}
fusetop_region = region(*FUSETOP)

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

def enclosed_hits(cut, metal_polys):
    """Return polygons that legally enclose *cut*, not ones it merely touches."""
    cut_region = db.Region(cut)
    inset = int(round(MIN_CUT_ENC_UM / DBU))
    return [i for i, poly in enumerate(metal_polys)
            if cut_region.inside(db.Region(poly).sized(-inset))]


for v, vr in via_regions.items():
    low, high = v, v + 1
    if low not in polys or high not in polys:
        continue
    for cut in vr.each_merged():
        if v == 4 and not db.Region(cut).and_(fusetop_region).is_empty():
            continue
        low_hits = enclosed_hits(cut, polys[low])
        high_hits = enclosed_hits(cut, polys[high])
        for li in low_hits:
            for hi in high_hits:
                union((low, li), (high, hi))


def comp_of(x_um, y_um, metal_level):
    pt = db.Point(int(round(x_um / DBU)), int(round(y_um / DBU)))
    for i, p in enumerate(polys[metal_level]):
        if p.inside(pt):
            return find((metal_level, i))
    return None


if "--pristine-cap-array" in sys.argv:
    # The routed array's eight M2 backbone rows are accessible through its
    # center at x=0.  This mode intentionally has no top-level routing or
    # labels in scope: it is the regression for the cap-array false merge.
    rail_components = {f"B{bit}": comp_of(0.0, RAIL_Y[bit], 2)
                       for bit in range(8)}
    print("=== PRISTINE CAP_ARRAY RAIL DISTINCTNESS ===")
    for name, comp in rail_components.items():
        print(f"  {name} rail @ (0.0, {RAIL_Y[int(name[1:])]:.2f}) M2: comp={comp}")
    valid = all(comp is not None for comp in rail_components.values())
    distinct = len(set(rail_components.values())) == 8
    print("  8 distinct rail components: " + ("PASS" if valid and distinct else "FAIL"))
    sys.exit(0 if valid and distinct else 1)


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


VDD_BACKBONE = ((-280.0, 124.0), 5)
GND_BACKBONE = ((-280.0, -128.0), 5)

all_pass = True

print("=== GLOBAL CONTINUITY ===")
global_checks = [
    ("SAMPLE label", SAMPLE_LABEL, "inv1 input", INV1["vin"]),
    ("SAMPLE label", SAMPLE_LABEL, "TG NFET gate", TG["sample"]),
    ("inv1 output", INV1["vout"], "TG PFET gate", TG["sample_n"]),
    ("VIN label", VIN_LABEL, "TG VIN terminal", TG["vin"]),
    ("TG DAC_TOP terminal", TG["dac_top"], "DAC_TOP M5 mesh", DAC_TOP_MESH),
    ("inv1 VDD", INV1["vdd"], "VDD backbone", VDD_BACKBONE),
    ("inv1 0", INV1["gnd"], "GND backbone", GND_BACKBONE),
]
for name_a, (pt_a, la), name_b, (pt_b, lb) in global_checks:
    ca, cb = comp_of(*pt_a, la), comp_of(*pt_b, lb)
    ok = ca is not None and ca == cb
    all_pass &= ok
    status = "PASS" if ok else "FAIL (separate/missing)"
    print(f"  {name_a} {pt_a}@M{la} <-> {name_b} {pt_b}@M{lb}: {status}")

print("\n=== PER-BIT CONTINUITY (each bit's 4 signal nets + supply) ===")
for bit in ROUTED_BITS:
    pts = bit_points(bit)
    checks = [
        (f"B{bit} label", pts["B_label"], f"NAND2<{bit}> A pin", pts["nand_a"]),
        ("inv1 output", INV1["vout"], f"NAND2<{bit}> B pin", pts["nand_b"]),
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
nets["SAMPLE"] = comp_of(*SAMPLE_LABEL[0], SAMPLE_LABEL[1])
nets["SAMPLE_N"] = comp_of(*INV1["vout"][0], INV1["vout"][1])
nets["VIN"] = comp_of(*VIN_LABEL[0], VIN_LABEL[1])
nets["DAC_TOP"] = comp_of(*TG["dac_top"][0], TG["dac_top"][1])
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
    print(f"  All {len(names)} nets / {len(names) * (len(names) - 1) // 2} pairs "
          f"({', '.join(names)}) are pairwise distinct components. PASS")

print()
print("ALL PASS" if all_pass else "SOME CHECKS FAILED")
sys.exit(0 if all_pass else 1)
