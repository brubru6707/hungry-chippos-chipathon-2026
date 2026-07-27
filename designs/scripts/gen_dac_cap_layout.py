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
    "metal1": (34, 0),
    "via1": (35, 0),
    "metal2": (36, 0),
    "via2": (38, 0),
    "metal3": (42, 0),
    "via3": (40, 0),
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


#
# ---------------------------------------------------------------------------
# Step 3 (DAC-6 routing / DAC-7/8): DAC_TOP mesh, 8 bit rails, dummy GND.
#
# LAYER PLAN -- chosen so every crossing between *unrelated* nets is
# guaranteed to be on different GDS layers (no via placed there), so a
# same-layer short is impossible by construction. The only same-layer
# adjacency between different nets is lane-separated *parallel* routing
# within one channel, which real DRC spacing-checks below:
#   Metal5 : DAC_TOP mesh (top plates of all 255 active cells). Exclusive
#            layer -- nothing else ever touches metal5 inside the core.
#   Metal4 : B7 bit-rail mesh (128 cells, direct merge to each cell's own
#            Metal4 bottom-plate slab, no via -- topologically identical to
#            the DAC_TOP mesh, just on metal4/for B7 only) PLUS, in the two
#            *boundary* channels (left of col0, right of col15 -- these
#            carry no B7 spine since B7's mesh only spans the 15 internal
#            channels), two extra private-trunk lanes for B2/B4.
#   Metal3 : per-column "private" vertical trunks for B1/B3/B5/B6 (and
#            B1/B3/B4 portions at col0/15, B4 at col7/8), each reached from
#            its cell's Metal4 slab via one Via3. A metal3 trunk coexists in
#            the same channel as a Metal4 B7 spine with zero risk (distinct
#            layers, even at the same X). Also carries the center dummy's
#            GND vertical drop (its own dedicated lane in col7/8's channel).
#   Metal2 : horizontal cross-column backbones, one per non-B7 bit (+ GND),
#            each given its own fully exclusive row channel (no lane
#            sharing needed). Reached from a Metal3 trunk via one Via2, or
#            from a Metal4 col0/15 lane via Via3+Via2 through a small
#            intermediate Metal3 pad.
# All per-column bit membership is *derived from the actual placement*
# (`_col_bit_membership`), not hardcoded, so this stays correct if the
# pair-assignment algorithm in build_pair_assignment() ever changes.
# ---------------------------------------------------------------------------

TRACK_W = 0.28        # M2.1/M3.1/M4.1 min width, used for all long-haul wires
SPINE_W = 0.9          # DAC_TOP/B7 mesh spine width (>=0.28 margin to nbr slab
                        # on each side of the 1.5um channel: (1.5-0.9)/2=0.3)
LANE_PITCH = 0.75      # same-layer parallel-lane center-to-center spacing.
                        # Every lane gets a VIA_PAD-wide (0.44) enclosure
                        # pad at its own trunk-to-metal2 hop (every cell
                        # row), so the binding constraint isn't TRACK_W but
                        # a pad on one lane vs. the *trunk* edge of the
                        # lane next to it (which, for a full-height trunk
                        # like B7's, is present at every row): need pitch
                        # >= TRACK_W/2 + VIA_PAD/2 + 0.28 = 0.64; 0.75
                        # gives 0.11um margin (0.6 measured 0.24um gaps
                        # against the 0.28 minimum in an actual DRC run).
VIA_SZ = 0.26          # V2.1/V3.1/V4.1 via size
VIA_PAD = 0.44         # local via enclosure pad (>=0.34 avoids the
                        # "<0.34um end-of-line" bonus overlap rules; gives
                        # (0.44-0.26)/2=0.09 plain overlap, well over the
                        # 0.01um V*.3b/V*.4a minimum)

VIA_BETWEEN = {
    frozenset(("metal1", "metal2")): "via1",
    frozenset(("metal2", "metal3")): "via2",
    frozenset(("metal3", "metal4")): "via3",
    frozenset(("metal4", "metal5")): "via4",
}
METAL_STACK = ["metal1", "metal2", "metal3", "metal4", "metal5"]


def _chain_between(layer_a, layer_b):
    ia, ib = METAL_STACK.index(layer_a), METAL_STACK.index(layer_b)
    lo, hi = min(ia, ib), max(ia, ib)
    return METAL_STACK[lo:hi + 1]


def _rect(cell, layer_index, x0, y0, x1, y1, dbu):
    cell.shapes(layer_index).insert(_box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), dbu))


def _via_chain(cell, li, x, y, dbu, layers):
    """Drop vias connecting consecutive layers in `layers` (e.g.
    ['metal2','metal3','metal4']), each with a local VIA_PAD enclosure on
    both sides -- so a caller can bridge metal2 to metal4 with one call."""
    for a, b in zip(layers, layers[1:]):
        vname = VIA_BETWEEN[frozenset((a, b))]
        _rect(cell, li[vname], x - VIA_SZ / 2, y - VIA_SZ / 2, x + VIA_SZ / 2, y + VIA_SZ / 2, dbu)
        _rect(cell, li[a], x - VIA_PAD / 2, y - VIA_PAD / 2, x + VIA_PAD / 2, y + VIA_PAD / 2, dbu)
        _rect(cell, li[b], x - VIA_PAD / 2, y - VIA_PAD / 2, x + VIA_PAD / 2, y + VIA_PAD / 2, dbu)


def col_x(col):
    x, _ = grid_xy(0, col)
    return x


def row_y(row):
    _, y = grid_xy(row, 0)
    return y


def chan_x_range(left_idx):
    """x-range of the vertical channel between column `left_idx` and
    `left_idx+1` (left_idx=-1 is the boundary channel left of col0,
    left_idx=CORE_N-1 is the boundary channel right of the last column)."""
    xl = col_x(left_idx) + M4_X_HALF
    xr = col_x(left_idx + 1) - M4_X_HALF
    return xl, xr


def chan_y_range(top_idx):
    """y-range of the horizontal channel between row `top_idx` and
    `top_idx+1` (same -1/CORE_N-1 boundary convention as chan_x_range)."""
    yl = row_y(top_idx) + M4_Y_HALF
    yr = row_y(top_idx + 1) - M4_Y_HALF
    return yl, yr


def _mesh(cell, li, layer, dbu, cell_predicate, placements):
    """DAC_TOP/B7-style full mesh: one vertical spine (width SPINE_W,
    centered) per internal channel (between col c, c+1 for c=0..CORE_N-2),
    plus a core-height horizontal strap for every active cell satisfying
    cell_predicate(label), spanning from its left neighbor spine to its
    right neighbor spine (or just to its own core edge at the array's outer
    columns, which have only one neighbor spine)."""
    spine_x = {}
    y0 = row_y(0) - FUSETOP_HALF
    y1 = row_y(CORE_N - 1) + FUSETOP_HALF
    for c in range(CORE_N - 1):
        xl, xr = chan_x_range(c)
        x = (xl + xr) / 2.0
        spine_x[c] = x
        _rect(cell, li[layer], x - SPINE_W / 2, y0, x + SPINE_W / 2, y1, dbu)

    for label, cells in placements.items():
        if label == "DUMMY" or not cell_predicate(label):
            continue
        for (row, col) in cells:
            cx, cy = grid_xy(row, col)
            left = spine_x.get(col - 1)
            right = spine_x.get(col)
            x0 = left if left is not None else cx - FUSETOP_HALF
            x1 = right if right is not None else cx + FUSETOP_HALF
            _rect(cell, li[layer], x0, cy - FUSETOP_HALF, x1, cy + FUSETOP_HALF, dbu)


def _col_bit_membership(placements):
    """col -> sorted list of bit labels (excluding B0/DUMMY) present in that
    column, derived from the actual placement. B7 IS included -- unlike an
    earlier draft, B7 gets no special Metal4-mesh treatment (a Metal4 shape
    threading through an inter-cell channel is *always* within 1.2um of an
    unrelated cell's bottom-plate slab there -- MIMTM.1 requires 1.2um and
    the channel is only 1.5um wide total, so no nonzero-width Metal4 shape
    can satisfy it on both sides at once; confirmed by an actual DRC run
    that flagged 2677 MIMTM.1 violations against a first attempt at a
    Metal4 B7 mesh). B7 is therefore routed exactly like every other bit:
    a per-column Metal3 (or Metal1, for column0/15 overflow) trunk reached
    from the cell's own Metal4 slab by a single Via3 stub."""
    membership = {c: set() for c in range(CORE_N)}
    for label, cells in placements.items():
        if label in ("B0", "DUMMY"):
            continue
        for (row, col) in cells:
            membership[col].add(label)
    return {c: sorted(bits) for c, bits in membership.items()}


def _private_channel_idx(col):
    if col == 0:
        return -1
    if col == CORE_N - 1:
        return CORE_N - 1
    return col - 1


def _lane_offsets(n):
    """n evenly spaced x-offsets (um) centered on 0, LANE_PITCH apart."""
    if n == 1:
        return [0.0]
    start = -(n - 1) / 2.0 * LANE_PITCH
    return [start + i * LANE_PITCH for i in range(n)]


def _private_trunk_plan(col_bits):
    """col -> [(bit, layer, x_offset_from_channel_center), ...].

    A 1.5um channel safely accommodates only two Metal3 trunks once the
    Metal3 landing pad of each M2-to-M4 cell stub is included. Additional
    trunks use Metal1, isolated from the Metal2 backbones and from that
    mandatory Metal3 pad. GND stays on Metal3 so the buried dummy can join
    its frame without an extra layer change."""
    plan = {}
    for col, bits in col_bits.items():
        if not bits:
            continue
        if "GND" in bits:
            others = [b for b in bits if b != "GND"]
            # The buried-dummy tie is a horizontal Metal3 jog from this
            # trunk to the dummy's slab.  It spans the whole channel, so
            # no other Metal3 trunk may share this channel; use Metal1 for
            # every active-bit trunk here.
            m3_bits, m1_bits = ["GND"], others
        else:
            m3_bits, m1_bits = bits[:2], bits[2:]
        entries = [(b, "metal3", o) for b, o in zip(m3_bits, _lane_offsets(len(m3_bits)))]
        entries += [(b, "metal1", o) for b, o in zip(m1_bits, _lane_offsets(len(m1_bits)))]
        plan[col] = entries
    return plan


BACKBONE_ROW = {
    "B7": -1,   # top edge channel
    "B6": CORE_N - 1,  # bottom edge channel (=15)
    "B5": 9,
    "B4": 7,
    "B3": 5,
    "B2": 3,
    "B1": 1,
    "GND": 11,
    "B0": 13,
}


def _route_bit_rails(cell, li, placements, dbu):
    col_bits = _col_bit_membership(placements)
    col_bits[8] = col_bits.get(8, []) + ["GND"]  # buried dummy's GND lane
    plan = _private_trunk_plan(col_bits)

    top_edge_y = sum(chan_y_range(-1)) / 2.0
    bot_edge_y = sum(chan_y_range(CORE_N - 1)) / 2.0
    trunk_y0 = min(top_edge_y, bot_edge_y)
    trunk_y1 = max(top_edge_y, bot_edge_y)

    # trunk_x[col][bit] = (layer, absolute_x) -- used both to draw the
    # vertical trunk and to route each cell's stub + the backbone via-drop.
    trunk_x = {}
    for col, entries in plan.items():
        idx = _private_channel_idx(col)
        xl, xr = chan_x_range(idx)
        xc = (xl + xr) / 2.0
        trunk_x[col] = {}
        for bit, layer, off in entries:
            x = xc + off
            _rect(cell, li[layer], x - TRACK_W / 2, trunk_y0, x + TRACK_W / 2, trunk_y1, dbu)
            trunk_x[col][bit] = (layer, x)
    gnd_x = trunk_x[8]["GND"][1]

    # Per-cell stub: connect each private-bit cell's Metal4 slab edge to its
    # column's trunk. A channel commonly carries >1 lane (e.g. B7 + the
    # column's own bit, or up to 5 at col0/15), all funneling toward the
    # SAME slab edge -- so a lane that isn't the closest one to that edge
    # must physically cross the nearer lanes' full-height trunks on its way
    # out. Hopping the crossing portion onto Metal2 avoids a same-layer
    # short there: Metal2 is otherwise used only by the backbones, which
    # sit in the *gap* between two rows (chan_y_range), never at a cell's
    # own row_y -- so a stub's Metal2 jog (always at some cell's row_y)
    # can never coincide with a backbone. Reaches whichever side the trunk
    # is actually on -- left for every column except col15, whose private
    # channel (_private_channel_idx returns CORE_N-1) sits to its *right*.
    for label, cells in placements.items():
        if label in ("B0", "DUMMY"):
            continue
        for (row, col) in cells:
            cx, cy = grid_xy(row, col)
            layer, tx = trunk_x[col][label]
            leftward = tx < cx
            slab_edge = cx - M4_X_HALF if leftward else cx + M4_X_HALF
            sign = 1 if leftward else -1
            # Keep the Metal3 pad at the slab-side Via3/Via2 stack at
            # least M3.2a away from the pad that terminates the private
            # trunk.  0.3um put the two 0.44um pads only 0.235um apart for
            # some lanes; 0.7um provides a 0.635um physical gap.
            via_x = slab_edge + sign * 0.4
            _via_chain(cell, li, tx, cy, dbu, _chain_between(layer, "metal2"))
            # Connecting rect must be VIA_PAD-tall (not just TRACK_W), or it
            # only bridges the middle sliver of the two end pads (each
            # VIA_PAD=0.44 tall) -- leaving their top/bottom strips
            # disconnected by less than M2.2a's 0.28 min spacing, exactly
            # the failure an actual DRC run caught.
            _rect(cell, li["metal2"], tx - TRACK_W / 2, cy - VIA_PAD / 2,
                  via_x + sign * VIA_PAD / 2, cy + VIA_PAD / 2, dbu)
            _via_chain(cell, li, via_x, cy, dbu, _chain_between("metal2", "metal4"))

    # Cross-column backbones (Metal2), one dedicated row channel per bit.
    x_lo = chan_x_range(-1)[0] - 0.5
    x_hi = chan_x_range(CORE_N - 1)[1] + 0.5
    for bit, row_idx in BACKBONE_ROW.items():
        if bit == "B0":
            continue
        byl, byr = chan_y_range(row_idx)
        by = (byl + byr) / 2.0
        _rect(cell, li["metal2"], x_lo, by - TRACK_W / 2, x_hi, by + TRACK_W / 2, dbu)
        for col, entries in trunk_x.items():
            if bit not in entries:
                continue
            layer, tx = entries[bit]
            chain = _chain_between(layer, "metal2")
            _via_chain(cell, li, tx, by, dbu, chain)

    # B0 is the one unpaired active cell.  Give it its own Metal1 trunk in
    # the channel immediately to its right and a private Metal2 backbone;
    # it must not be left as an accidental degree-one connection to GND.
    (b0_row, b0_col), = placements["B0"]
    cx, cy = grid_xy(b0_row, b0_col)
    b0_channel = b0_col
    b0_slab_edge = cx + M4_X_HALF
    b0_via_x = b0_slab_edge - 0.4
    # Start B0's Metal1 trunk directly at its M4-to-M1 via stack inside the
    # B0 slab.  A previous M2 jog toward the central channel intersected the
    # same-row B7 cell's M2 stub, merging B0 and B7 despite passing DRC.
    b0_x = b0_via_x
    b0_yl, b0_yr = chan_y_range(BACKBONE_ROW["B0"])
    b0_y = (b0_yl + b0_yr) / 2.0
    _rect(cell, li["metal1"], b0_x - TRACK_W / 2, cy,
          b0_x + TRACK_W / 2, b0_y, dbu)
    _via_chain(cell, li, b0_x, cy, dbu, ["metal1", "metal2", "metal3", "metal4"])
    _rect(cell, li["metal2"], x_lo, b0_y - TRACK_W / 2,
          x_hi, b0_y + TRACK_W / 2, dbu)
    _via_chain(cell, li, b0_x, b0_y, dbu, ["metal1", "metal2"])

    return {"trunk_x": trunk_x, "gnd_x": gnd_x, "trunk_y0": trunk_y0, "trunk_y1": trunk_y1}


def _tie_top_to_bottom_local(cell, li, row, col, dbu):
    """Shorts one dummy cell's own top plate (Metal5 core) directly to its
    own bottom plate (Metal5 north pad, already Via4-tied to the Metal4
    slab) with a plain Metal5 strip bridging the PAD_GAP between them. No
    via needed (both already metal5) -- and no MIMTM.4/.5 exclusion-zone
    conflict, since unlike a sideways tab this uses the *existing* bottom-
    plate pad geometry rather than adding a new via near fusetop (a new
    via4 can't satisfy MIMTM.4 -inset- and MIMTM.5 -outset- simultaneously
    within this cell's 0.6um E/W margin -- confirmed infeasible by
    construction, hence routing the tie through the N pad instead, which
    already sits >=BOTVIA_GAP clear of fusetop by design)."""
    cx, cy = grid_xy(row, col)
    _rect(cell, li["metal5"], cx - PAD_HALF_W, cy + FUSETOP_HALF,
          cx + PAD_HALF_W, cy + PAD_Y1, dbu)


def _route_dummy_gnd(cell, li, placements, dbu, gnd_x, trunk_y0):
    """Ties both plates of every dummy cell (68-cell ring + the one buried
    in-core dummy) to a single GND net.

    Ring cells are NOT bridged with a raw Metal4 rectangle between
    neighbors (an earlier attempt at that re-triggered MIMTM.1: the
    recognized bottom-plate region "mimtm_virtual" is fusetop sized by only
    1.06um AND the metal4 slab, so for a ring cell whose slab already
    extends 0.6um past its own fusetop edge, a bridge into the channel
    beyond it creates a stretch of plain "topmin1_metal" that ISN'T
    anyone's mimtm_virtual, sitting well under 1.2um from the neighbor's --
    a structural conflict, not a sizing mistake, so no channel-spanning
    Metal4 shape works here regardless of width). Instead every ring cell
    (and the buried center dummy) gets a single Via3 stub -- exactly the
    private-bit-trunk pattern -- out to a Metal3 frame running just OUTSIDE
    the ring's own footprint (never inside any channel between two real
    cells), one dedicated lane per side, joined at the corners.
    """
    ring = sorted(placements.get("DUMMY", []))
    ring_incore = [(r, c) for (r, c) in ring if 0 <= r < CORE_N and 0 <= c < CORE_N]
    ring_outer = [(r, c) for (r, c) in ring if not (0 <= r < CORE_N and 0 <= c < CORE_N)]
    assert len(ring_incore) == 1, ring_incore
    center_rc = ring_incore[0]

    for (r, c) in ring:
        _tie_top_to_bottom_local(cell, li, r, c, dbu)

    top_y = row_y(-1) - M4_Y_HALF - 0.5
    bot_y = row_y(CORE_N) + M4_Y_HALF + 0.5
    left_x = col_x(-1) - M4_X_HALF - 0.5
    right_x = col_x(CORE_N) + M4_X_HALF + 0.5
    # Horizontal trunks extend TRACK_W/2 past left_x/right_x so each corner
    # overlap with the vertical trunks is a clean square, not an L-shaped
    # notch narrower than M3.1's min width.
    _rect(cell, li["metal3"], left_x - TRACK_W / 2, top_y - TRACK_W / 2, right_x + TRACK_W / 2, top_y + TRACK_W / 2, dbu)
    _rect(cell, li["metal3"], left_x - TRACK_W / 2, bot_y - TRACK_W / 2, right_x + TRACK_W / 2, bot_y + TRACK_W / 2, dbu)
    _rect(cell, li["metal3"], left_x - TRACK_W / 2, top_y, left_x + TRACK_W / 2, bot_y, dbu)
    _rect(cell, li["metal3"], right_x - TRACK_W / 2, top_y, right_x + TRACK_W / 2, bot_y, dbu)

    # Y_STUB_OFFSET (2.9um from the cell's own center): the via3 itself
    # (0.26um wide) must clear fusetop's edge (2.5) -- offset 2.6 put the
    # via's own inner edge at 2.47, *inside* fusetop, tripping MIMTM.10
    # ("via3 must not touch metal4 AND fusetop"). Must also stay under
    # mimtm_virtual's 1.06um-sized-fusetop reach (3.56, minus the via pad's
    # half-width) or recreate the "orphan metal4" MIMTM.1 trap the whole
    # ring-frame redesign exists to avoid. 2.9 clears both with margin.
    Y_STUB_OFFSET = 2.9
    for (r, c) in ring_outer:
        cx, cy = grid_xy(r, c)
        if r == -1:
            via_y = cy - Y_STUB_OFFSET
            _rect(cell, li["metal3"], cx - TRACK_W / 2, top_y, cx + TRACK_W / 2, via_y - VIA_PAD / 2, dbu)
            _via_chain(cell, li, cx, via_y, dbu, ["metal3", "metal4"])
        elif r == CORE_N:
            via_y = cy + Y_STUB_OFFSET
            _rect(cell, li["metal3"], cx - TRACK_W / 2, via_y + VIA_PAD / 2, cx + TRACK_W / 2, bot_y, dbu)
            _via_chain(cell, li, cx, via_y, dbu, ["metal3", "metal4"])
        elif c == -1:
            via_x = cx - M4_X_HALF + 0.4
            _rect(cell, li["metal3"], left_x, cy - TRACK_W / 2, via_x - VIA_PAD / 2, cy + TRACK_W / 2, dbu)
            _via_chain(cell, li, via_x, cy, dbu, ["metal3", "metal4"])
        else:  # c == CORE_N
            via_x = cx + M4_X_HALF - 0.4
            _rect(cell, li["metal3"], via_x + VIA_PAD / 2, cy - TRACK_W / 2, right_x, cy + TRACK_W / 2, dbu)
            _via_chain(cell, li, via_x, cy, dbu, ["metal3", "metal4"])

    # Buried center dummy: same Via3-stub pattern, straight to its own slab.
    rC, cC = center_rc
    cx, cy = grid_xy(rC, cC)
    via_x = cx - M4_X_HALF + 0.4
    _rect(cell, li["metal3"], gnd_x - TRACK_W / 2, cy - TRACK_W / 2,
          via_x + VIA_PAD / 2, cy + TRACK_W / 2, dbu)
    _via_chain(cell, li, via_x, cy, dbu, ["metal3", "metal4"])

    # Tie the GND metal3 trunk into the ring frame: both metal3, so a plain
    # extension of the trunk up to top_y merges with the frame directly --
    # no via needed. trunk_y0 is the trunk's own upper end (already reaches
    # the top-edge channel); this just continues it a bit further out.
    _rect(cell, li["metal3"], gnd_x - TRACK_W / 2, top_y, gnd_x + TRACK_W / 2, trunk_y0, dbu)


def build_routing(layout, top, placements):
    li = _mk_layers(layout)
    dbu = layout.dbu
    _mesh(top, li, "metal5", dbu, lambda label: True, placements)  # DAC_TOP
    info = _route_bit_rails(top, li, placements, dbu)
    _route_dummy_gnd(top, li, placements, dbu, info["gnd_x"], info["trunk_y0"])
    return info


def write_caps_only_reference(path, placements):
    """Write the flat, native-C-element LVS reference for the routed array.

    Native C syntax is deliberate: an X-instance of cap_mim_2f0fF is silently
    discarded by this PDK LVS reader and can produce a false 0-device pass.
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write("* Generated caps-only LVS reference for routed cap_array.\n")
        f.write("* 255 active caps: DAC_TOP to B0..B7; 69 dummies: GND to GND.\n")
        f.write("* Native C cards are mandatory for gf180mcu LVS extraction.\n")
        f.write(".subckt cap_array DAC_TOP B0 B1 B2 B3 B4 B5 B6 B7 GND\n")
        index = 0
        for bit in [f"B{i}" for i in range(8)]:
            for _ in placements[bit]:
                index += 1
                f.write(f"C{index} {bit} DAC_TOP cap_mim_2f0fF W=5e-6 L=5e-6 M=1\n")
        for _ in placements["DUMMY"]:
            index += 1
            f.write(f"C{index} GND GND cap_mim_2f0fF W=5e-6 L=5e-6 M=1\n")
        assert index == 324, index
        f.write(".ends cap_array\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "route":
        layout, top, placements = build_cap_array()
        build_routing(layout, top, placements)
        out = "/foss/designs/dac/layout/cap_array.gds"
        layout.write(out)
        print("wrote", out, "topcell", top.name)
    elif len(sys.argv) > 1 and sys.argv[1] == "ref":
        _, _, placements = build_cap_array()
        out = "/foss/designs/dac/layout/cap_array_caps_only_ref.spice"
        write_caps_only_reference(out, placements)
        print("wrote", out)
    elif len(sys.argv) > 1 and sys.argv[1] == "array":
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
