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


if __name__ == "__main__":
    layout, top = build_unit_cell()
    out = "/foss/designs/dac/layout/cu_cell.gds"
    layout.write(out)
    print("wrote", out, "topcell", top.name)
