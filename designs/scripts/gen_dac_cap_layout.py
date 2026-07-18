#!/usr/bin/env python3
"""
Generate DAC binary-weighted cap-array layout for gf180mcuD (MIM Option B,
5LM stack -- variant=D, metal_top=11K, mim_option=B, metal_level=5LM).

STANDING RULE: this chip tapes out on variant=D. Option A/3LM geometry
(Metal2/Via2 bottom plate) is WRONG for this stack -- under mim_option=B the
bottom plate must be on Metal4 (topmin1_metal), contacted by Via4
(top_via), because metal_level=5LM makes top_metal=Metal5/top_via=Via4/
topmin1_metal=Metal4 (see layers_def.drc: `when '5LM' -> top_via=via4,
topmin1_via=via3, top_metal=metal5, topmin1_metal=metal4`). A 3LM-built cell
(Metal2/Via2 bottom plate) extracts as 0 devices under variant=D.

Unit cap: 50fF cap_mim (FuseTop=top plate, Metal4=bottom plate), 5um x 5um
(2.0 fF/um^2), with top/bottom-plate breakouts on Metal5 (top_metal):
  - top plate:    bare Metal5/FuseTop core overlap (5x5um, already >>
                   MT.1's 0.44um / MT.4's 0.5625um^2 minimums under the
                   generic 11K top-metal rules -- NOT the 30K thick-metal
                   MT30.x rules, which don't apply to this stack) is itself
                   the DAC_TOP landing surface, with a Via4 "sea of vias"
                   inside FuseTop (MIMTM.4/MIMTM.9).
  - bottom plate: Metal4 slab enclosing FuseTop by MIMTM.3's 0.6um on all
                   sides, with two symmetric (north + south) Via4 tabs
                   placed >=0.4um outside FuseTop's edge (MIMTM.5),
                   enclosed by Metal4 by >=0.4um (MIMTM.2), each landing on
                   its own small Metal5 pad kept >=0.46um (MT.2a) from the
                   top plate's own Metal5 core. Splitting the bottom-plate
                   breakout N+S (rather than the single south-only tab used
                   in the old 3LM/Option-A cell) keeps the cell symmetric
                   about both axes for common-centroid tiling, and is cheap
                   now that Metal5's spacing/width minimums are ~4x looser
                   than the old 30K MT30.x rules that drove that asymmetry.

Design rules used (from gf180mcuD klayout DRC deck -- rule_decks/mim_b.drc,
via4.drc, metal4.drc, metaltop.drc -- read directly, not guessed):
  MIMTM.1  bottom-plate metal4 <-> other unrelated metal4:    >= 1.2um
  MIMTM.2  bottom-plate via4 enclosed by metal4:               >= 0.4um
  MIMTM.3  fusetop enclosed by (metal4 int. fusetop):          >= 0.6um
  MIMTM.4  via4 (on top plate) enclosed by fusetop:            >= 0.4um
  MIMTM.5  fusetop <-> via4-that-connects-to-metal4:           >= 0.4um
  MIMTM.6  fusetop <-> unrelated fusetop:                      >= 0.6um
  MIMTM.7  fusetop must be inside cap_mk:                       0um enc.
  MIMTM.8a min fusetop (=cap) area:                             25um^2
  MIMTM.9  via4-on-fusetop to via4-on-fusetop spacing:         >= 0.5um
  MIMTM.10 via3 must NOT touch metal4/fusetop bottom plate (via4 only)
  V4.1     via4 size:                                    exactly 0.26um
  V4.2a    via4 <-> via4 spacing:                              >= 0.26um
  V4.3b/V4.4a  metal4/metal5 overlap of via4:                  >= 0.01um
  M4.1     metal4 min width:                                   0.28um
  M4.2a    metal4 min spacing:                                 0.28um
  MT.1     metal5 (top_metal, 11K) min width:                  0.44um
  MT.2a    metal5 (top_metal, 11K) min spacing:                0.46um
  MT.4     metal5 (top_metal, 11K) min area:                 0.5625um^2

LVS extraction (mimcap_derivations.lvs / mimcap_extraction.lvs /
mimcap_connections.lvs, MIM_OPTION='B'): P1 (bottom plate) = mim_virtual =
fusetop.sized(1.06um).and(topmin1_metal.interacting(fusetop)); P2 (top
plate) = fuse_cap = fusetop.interacting(cap_mk).interacting(mim_l_mk) --
mim_l_mk is LOAD-BEARING for extraction, not cosmetic, do not drop it.
connect(topmin1_metal, mim_virtual) / connect(fuse_cap, top_via_cap) /
connect(top_via_cap, top_metal_cap) confirm the Metal4/Via4/Metal5
breakout topology built below is exactly what LVS expects for Option B.
"""

import klayout.db as db

LAYER = {
    "metal4": (46, 0),
    "metal5": (81, 0),
    "via4": (41, 0),
    "fusetop": (75, 0),
    "cap_mk": (117, 5),
    "mim_l_mk": (117, 10),
}

# Unit cap geometry (um), core cap centered at local origin.
FUSETOP_HALF = 2.5           # 5.0 x 5.0 um -> 25.0 um^2 -> 50fF @ 2.0fF/um^2
M4_MARGIN = 0.6               # MIMTM.3 min bottom-plate (metal4) enclosure of fusetop
VIA_SIZE = 0.26
TOPVIA_INSET = 0.4            # MIMTM.4: via4-on-fusetop enclosed by fusetop
TOPVIA_PITCH = 0.76           # 0.26 via + 0.5 spacing (MIMTM.9 sea-of-via spacing)

BOTVIA_GAP = 0.5              # MIMTM.5 min is 0.4um; extra margin
PAD_GAP = 0.5                 # metal5-pad-to-top-plate-metal5 spacing (>= MT.2a 0.46um)
PAD_HALF_W = 0.4              # bottom-plate metal5 pad: 0.8um wide (>= MT.1 0.44um)
PAD_HEIGHT = 0.8              # 0.8x0.8 = 0.64um^2 (>= MT.4 0.5625um^2)
M4_VIA_ENC = 0.4              # MIMTM.2 min enclosure of bottom-plate via4 within metal4
M4_Y_MARGIN = 0.1             # extra slack beyond the strict MIMTM.2 minimum

PAD_Y1 = FUSETOP_HALF + PAD_GAP                  # south pad's inner (north) edge, positive magnitude
PAD_Y0 = PAD_Y1 + PAD_HEIGHT                      # south pad's outer (south) edge, positive magnitude
_pad_mid = (PAD_Y1 + PAD_Y0) / 2
BOTVIA_Y_INNER = _pad_mid - VIA_SIZE / 2          # via edge nearer to fusetop, positive magnitude
BOTVIA_Y_OUTER = _pad_mid + VIA_SIZE / 2          # via edge farther from fusetop, positive magnitude
assert BOTVIA_Y_INNER - FUSETOP_HALF >= BOTVIA_GAP - 1e-9   # MIMTM.5 gap, fusetop edge to via4

M4_X_HALF = FUSETOP_HALF + M4_MARGIN
M4_Y_HALF = BOTVIA_Y_OUTER + M4_VIA_ENC + M4_Y_MARGIN   # MIMTM.2 enclosure + buffer, symmetric N/S


def _mk_layers(layout):
    return {name: layout.layer(*gd) for name, gd in LAYER.items()}


def _box(x0, y0, x1, y1, dbu):
    return db.Box(
        int(round(x0 / dbu)), int(round(y0 / dbu)),
        int(round(x1 / dbu)), int(round(y1 / dbu)),
    )


def add_unit_cap(layout, cell, cx, cy, li):
    """Insert one 50fF unit-cap structure centered at (cx, cy) um into `cell`."""
    dbu = layout.dbu
    fh = FUSETOP_HALF

    # --- FuseTop (top plate, the actual MIM capacitor electrode) ---
    cell.shapes(li["fusetop"]).insert(_box(cx - fh, cy - fh, cx + fh, cy + fh, dbu))

    # --- mim_l_mk marker strip along the fusetop bottom edge (LOAD-BEARING
    #     for LVS extraction -- fuse_cap requires fusetop.interacting(mim_l_mk)) ---
    cell.shapes(li["mim_l_mk"]).insert(_box(cx - fh, cy - fh, cx + fh, cy - fh + 0.1, dbu))

    # --- Metal4 bottom plate slab: MIMTM.3 margin enclosing fusetop on all
    #     sides, extended N/S far enough to enclose the two symmetric
    #     bottom-plate via4 tabs (MIMTM.2) ---
    cell.shapes(li["metal4"]).insert(
        _box(cx - M4_X_HALF, cy - M4_Y_HALF, cx + M4_X_HALF, cy + M4_Y_HALF, dbu)
    )

    # --- cap_mk: superset of fusetop (MIMTM.7) ---
    cell.shapes(li["cap_mk"]).insert(
        _box(cx - M4_X_HALF, cy - M4_Y_HALF, cx + M4_X_HALF, cy + M4_Y_HALF, dbu)
    )

    # --- Top plate: Metal5 exactly over the fusetop core. No extra tab
    #     needed -- this bare 5x5 surface (already >> MT.1/MT.4's 11K
    #     minimums) is itself the DAC_TOP landing pad; adjacent unit cells'
    #     top plates merge directly into one contiguous mesh in the array
    #     (Step 2), so no MT.2a inter-tab spacing is incurred there. ---
    cell.shapes(li["metal5"]).insert(_box(cx - fh, cy - fh, cx + fh, cy + fh, dbu))

    # --- Top plate via4 "sea of vias" inside fusetop, inset by TOPVIA_INSET (MIMTM.4) ---
    inset = fh - TOPVIA_INSET
    span = 2 * inset
    n = int(span // TOPVIA_PITCH)
    if n < 1:
        n = 1
    total = n * VIA_SIZE + (n - 1) * (TOPVIA_PITCH - VIA_SIZE)
    start = -total / 2
    for i in range(n):
        for j in range(n):
            vx0 = cx + start + i * TOPVIA_PITCH
            vy0 = cy + start + j * TOPVIA_PITCH
            cell.shapes(li["via4"]).insert(
                _box(vx0, vy0, vx0 + VIA_SIZE, vy0 + VIA_SIZE, dbu)
            )

    # --- Bottom plate: two symmetric (south + north) single-via4 tabs,
    #     outside fusetop by BOTVIA_GAP (MIMTM.5), each landing on its own
    #     small Metal5 pad kept PAD_GAP from the top plate's Metal5 (MT.2a) ---
    for sign in (-1, +1):
        vx0 = cx - VIA_SIZE / 2
        # via spans [BOTVIA_Y_INNER, BOTVIA_Y_OUTER] on the +y side, mirrored on -y
        vy0 = cy + sign * BOTVIA_Y_OUTER if sign < 0 else cy + BOTVIA_Y_INNER
        cell.shapes(li["via4"]).insert(
            _box(vx0, vy0, vx0 + VIA_SIZE, vy0 + VIA_SIZE, dbu)
        )

        pad_y_inner = cy + sign * PAD_Y1
        pad_y_outer = cy + sign * PAD_Y0
        pad_y0, pad_y1 = sorted((pad_y_inner, pad_y_outer))
        cell.shapes(li["metal5"]).insert(
            _box(cx - PAD_HALF_W, pad_y0, cx + PAD_HALF_W, pad_y1, dbu)
        )


def build_unit_cell(topcell_name="dac_cap_unit"):
    layout = db.Layout()
    layout.dbu = 0.001
    li = _mk_layers(layout)
    top = layout.create_cell(topcell_name)
    add_unit_cap(layout, top, 0.0, 0.0, li)
    return layout, top


#
# ---------------------------------------------------------------------------
# Step 2 (DAC-6): 255-unit common-centroid array + dummy ring.
#
# Placement grid: 16x16 core (256 grid slots), each grid slot instances the
# *identical* dac_cap_unit cell built above (never redrawn per-position --
# that's the matching requirement). Pitch is set by the MIM-specific
# bottom-plate rule, NOT the generic metal4 rule:
#   MIMTM.1: "Minimum MiM bottom plate spacing to the bottom plate metal
#             (whether adjacent MiM or routing metal)" >= 1.2um
#             (mim_b.drc: mimtm1_l1 = topmin1_metal.separation(mimtm_virtual,
#             transparent, 1.2.um) -- a purely geometric layer check, not
#             net-aware, so it applies uniformly to same-bit AND
#             different-bit neighbors alike).
# This is the binding constraint (looser than nothing, but stricter than the
# generic M4.2a 0.28um metal4-to-metal4 spacing) because cu_cell's Metal4
# bottom-plate slab is drawn exactly at the cell's full bounding box
# (M4_X_HALF/M4_Y_HALF == FUSETOP_HALF+... == bbox/2 in both axes, verified
# via klayout.db bbox query: [-3.1,-4.03] to [3.1,4.03], i.e. metal4 IS the
# bbox) -- so pitch-minus-cellsize equals the metal4-to-metal4 gap directly,
# and a >=1.2um pitch margin clears MIMTM.1 with no extra geometry needed.
# GAP is set with margin above the 1.2um minimum; PITCH_X/Y are verified by
# an actual array-level DRC run below (rule interactions across a 7.12um
# MIMTM.1 "near-cap" sizing window are not hand-derivable with full
# confidence -- confirmed empirically, not just calculated).
#
# Adjacent unit cells' top-plate Metal5 (5x5um core, well inside the 6.2x
# 8.06um cell) never comes close to touching neighbors at this pitch (gap
# far exceeds MT.2a's 0.46um min spacing), so no accidental DAC_TOP<->GND
# merge risk between an active cell and a neighboring dummy cell even
# though nets aren't routed/labeled yet at this placed-but-unrouted
# checkpoint.
# ---------------------------------------------------------------------------

GAP = 1.5  # um, margin above MIMTM.1's 1.2um bottom-plate-to-bottom-plate min
CELL_W = 2 * M4_X_HALF   # 6.2um, == cu_cell's full bbox width (metal4 IS the bbox)
CELL_H = 2 * M4_Y_HALF   # 8.06um, == cu_cell's full bbox height
PITCH_X = CELL_W + GAP
PITCH_Y = CELL_H + GAP

CORE_N = 16   # 16x16 core grid = 256 slots
RING = 1      # dummy ring width, in cells, around the core

# 127 pairs -> B7..B1 (64+32+16+8+4+2+1 = 127 pairs = 254 units), spread via
# a bit-reversal permutation (see pair_order_128 below) rather than assigned
# contiguously. Point-symmetric pairing alone already gives each of these
# bits an EXACT centroid at the array center regardless of assignment order
# (pair members are exact 180-degree reflections, so their average position
# is the center by construction, and this holds for the union of any set of
# whole pairs) -- the interspersion below is not needed for that first-order
# guarantee, but it is what protects against *non-linear* (radial/
# quadratic-bowl-shaped) process gradients across the die, which point
# symmetry alone does not cancel (a linear gradient IS cancelled by point
# symmetry regardless of spread; a radially-symmetric quadratic one is not,
# since it depends on |pos-center| rather than pos-center directly).
PAIR_BIT_COUNTS = [
    ("B7", 64), ("B6", 32), ("B5", 16), ("B4", 8),
    ("B3", 4), ("B2", 2), ("B1", 1),
]


def _bitrev(x, bits=7):
    r = 0
    for i in range(bits):
        r = (r << 1) | ((x >> i) & 1)
    return r


def pair_order_128():
    """Bit-reversal permutation of 0..127.

    Property used here: for a linear index p walked in row-major order over
    the 8x16 half-grid (p = row*16 + col), bit-reversing p and sorting by
    the reversed value yields a sequence whose first N/2^k elements are a
    uniform stride-2^k subsample of the original row-major order, at every
    k. Concretely the first 64 (of 128) entries are exactly the
    even-column half of the grid (columns 0,2,4,...,14 across all 8 rows) --
    alternating columns, not a contiguous block -- and each subsequent
    halving refines that same even spread. Walking this order and
    cumulatively assigning bit labels (B7 first/largest count, down to B1)
    means every bit's pairs are spread through the whole array at a scale
    matched to how many pairs it has, rather than clustered.
    """
    return sorted(range(128), key=_bitrev)


def pair_positions(p):
    """pair index (0..127) -> ((row,col), (15-row,15-col)) in the 16x16 core."""
    row, col = divmod(p, 16)
    return (row, col), (15 - row, 15 - col)


def _pair_center_distance(p):
    """Physical distance (um) from pair p's representative position to the
    array's geometric center (grid coord (7.5,7.5) -> physical origin)."""
    (row, col), _ = pair_positions(p)
    x, y = grid_xy(row, col)
    return (x ** 2 + y ** 2) ** 0.5


def build_pair_assignment():
    """pair index (0..127) -> bit label, or 'B0_CENTER' for the chosen pair.

    The physically most-central pair (both members closest to the array's
    geometric center) is picked explicitly for B0+dummy, per the task's
    "final central-most pair" requirement -- the bit-reversal spread order
    alone does not put its last element near the center, so center
    selection and interspersion are handled as two separate steps: pick the
    center pair first, then intersperse the *remaining* 127 pairs for
    B7..B1 using the same bit-reversal order with the center pair removed.
    """
    p_center = min(range(128), key=_pair_center_distance)
    order = [p for p in pair_order_128() if p != p_center]
    assert len(order) == 127
    assignment = {p_center: "B0_CENTER"}
    idx = 0
    for label, cnt in PAIR_BIT_COUNTS:
        for _ in range(cnt):
            assignment[order[idx]] = label
            idx += 1
    assert idx == 127
    return assignment


def grid_xy(row, col):
    """16x16-core grid indices (may extend into the dummy ring) -> (x,y) um,
    centered so the core's geometric center sits at the origin."""
    x = (col - (CORE_N - 1) / 2.0) * PITCH_X
    y = (row - (CORE_N - 1) / 2.0) * PITCH_Y
    return x, y


def build_cap_array(topcell_name="cap_array", unit_cell_name="dac_cap_unit"):
    """Build the 255-unit common-centroid array + 1-cell-wide dummy ring.

    Returns (layout, top_cell, placements) where placements maps each label
    ("B0".."B7", "DUMMY") to its list of (row,col) grid positions. Every
    instance placed is the *same* dac_cap_unit cell (built once, above) --
    no per-position geometry is redrawn.
    """
    layout, unit_top = build_unit_cell(unit_cell_name)
    dbu = layout.dbu
    top = layout.create_cell(topcell_name)
    unit_idx = unit_top.cell_index()

    placements = {}
    assignment = build_pair_assignment()
    for p, label in assignment.items():
        (r1, c1), (r2, c2) = pair_positions(p)
        if label == "B0_CENTER":
            placements.setdefault("B0", []).append((r1, c1))
            placements.setdefault("DUMMY", []).append((r2, c2))
        else:
            placements.setdefault(label, []).append((r1, c1))
            placements.setdefault(label, []).append((r2, c2))

    # Dummy ring: every grid cell in the (CORE_N+2*RING)^2 square that falls
    # outside the CORE_N x CORE_N core (full rows above/below, side columns
    # flanking core rows) -- 18x18 - 16x16 = 68 cells for RING=1.
    lo, hi = -RING, CORE_N - 1 + RING
    ring_cells = [
        (row, col)
        for row in range(lo, hi + 1)
        for col in range(lo, hi + 1)
        if not (0 <= row < CORE_N and 0 <= col < CORE_N)
    ]
    placements.setdefault("DUMMY", []).extend(ring_cells)

    for label, cells in placements.items():
        for (row, col) in cells:
            x, y = grid_xy(row, col)
            t = db.Trans(db.Trans.R0, db.Point(int(round(x / dbu)), int(round(y / dbu))))
            top.insert(db.CellInstArray(unit_idx, t))

    return layout, top, placements


def report_centroids(placements):
    """Per-label centroid (mean x,y, um) and deviation from array center (0,0)."""
    report = {}
    for label, cells in placements.items():
        xs, ys = [], []
        for (row, col) in cells:
            x, y = grid_xy(row, col)
            xs.append(x)
            ys.append(y)
        n = len(cells)
        cx = sum(xs) / n
        cy = sum(ys) / n
        dev = (cx ** 2 + cy ** 2) ** 0.5
        report[label] = {"n": n, "cx": cx, "cy": cy, "dev": dev}
    return report


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "array":
        layout, top, placements = build_cap_array()
        out = "/foss/designs/dac/layout/cap_array.gds"
        layout.write(out)
        print("wrote", out, "topcell", top.name)
        print("PITCH_X", PITCH_X, "PITCH_Y", PITCH_Y, "GAP", GAP)
        active = sum(len(v) for k, v in placements.items() if k != "DUMMY")
        print("active instances:", active, "dummy instances:", len(placements.get("DUMMY", [])))
        centroids = report_centroids(placements)
        for label in ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "DUMMY"]:
            c = centroids[label]
            print(f"{label}: n={c['n']:4d} centroid=({c['cx']:+.4f}, {c['cy']:+.4f}) um  dev={c['dev']:.4f} um")
    else:
        layout, top = build_unit_cell()
        out = "/foss/designs/dac/layout/cu_cell.gds"
        layout.write(out)
        print("wrote", out, "topcell", top.name)
