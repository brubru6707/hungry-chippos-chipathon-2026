#!/usr/bin/env python3
"""
Generate DAC binary-weighted cap-array layout for gf180mcuD (MIM Option A).

Unit cap: 50fF cap_mim (FuseTop=top plate, Metal2=bottom plate), 5um x 5um
(2.0 fF/um^2), with top/bottom-plate breakouts on Metal3:
  - top plate:    bare Metal3/FuseTop core overlap (5x5um, already >>
                   MT30.1a's 1.8um min) is itself the DAC_TOP landing
                   surface, with a Via2 "sea of vias" inside FuseTop
                   (MIM.4/MIM.9).
  - bottom plate: Metal2 slab under/around FuseTop (MIM.3 0.6um min
                   enclosure), with a 2x2 Via2 array south of FuseTop
                   by >=0.4um (MIM.5), enclosed by Metal2 by >=0.4um
                   (MIM.2), landing on a *separate* Metal3 pad kept
                   >=1.8um from the top-plate's own Metal3 island
                   (MT30.2/3/4 -- metal3 is process top_metal in the
                   3LM/mim_option=A stack, so it inherits the "thick
                   top metal" 1.8um width/spacing rules, not the
                   generic 0.28um M3.1/M3.2a).

Design rules used (from gf180mcuD klayout DRC deck, rule_decks/mim_a.drc,
via2.drc, metal2.drc, metal3.drc -- read directly, not guessed):
  MIM.1  bottom-plate metal2 <-> other metal2:              >= 1.2um
  MIM.2  bottom-plate via2 enclosed by metal2:               >= 0.4um
  MIM.3  fusetop enclosed by (metal2 int. fusetop):          >= 0.6um
  MIM.4  via2 (on top plate) enclosed by fusetop:            >= 0.4um
  MIM.5  fusetop <-> via2-that-connects-to-metal2:           >= 0.4um
  MIM.6  fusetop <-> unrelated fusetop:                      >= 0.6um
  MIM.7  fusetop must be inside cap_mk:                       0um enc.
  MIM.8a min fusetop (=cap) area:                             25um^2
  MIM.9  via2-on-fusetop to via2-on-fusetop spacing:         >= 0.5um
  MIM.10 via1 must NOT touch metal2/fusetop bottom plate (via2 only)
  V2.1   via2 size:                                    exactly 0.26um
  V2.2a  via2 <-> via2 spacing:                              >= 0.26um
  M2.1/M3.1 metal2/metal3 min width:                          0.28um
  M2.2a/M3.2a metal2/metal3 min spacing:                      0.28um
"""

import klayout.db as db

LAYER = {
    "metal2": (36, 0),
    "metal3": (42, 0),
    "via2": (38, 0),
    "fusetop": (75, 0),
    "cap_mk": (117, 5),
    "mim_l_mk": (117, 10),
}

# Unit cap geometry (um), core cap centered at local origin.
#
# NOTE on metal3 "thick top metal" (MT30.x) rules: variant=A (mim_option=A)
# forces METAL_LEVEL=3LM, which makes metal3 the process top_metal --
# subject to MT30.1a/.2/.3/.4 (>=1.8um min width *and* spacing between
# unrelated top_metal shapes) instead of the generic M3.1/M3.2a (0.28um)
# rules. That is why the bottom-plate breakout pad below is far larger /
# further away than the MIM.x rules alone would require: it must clear
# 1.8um from the top-plate's own metal3 island, and be >=1.8um in both
# dimensions itself (MT30.1a), and land >=2x2 vias (MT30.8).
FUSETOP_HALF = 2.5          # 5.0 x 5.0 um -> 25.0 um^2 -> 50fF @ 2.0fF/um^2
M2_MARGIN = 0.6              # MIM.3 min bottom-plate (metal2) enclosure of fusetop
VIA_SIZE = 0.26
TOPVIA_INSET = 0.4           # MIM.4: via2-on-fusetop enclosed by fusetop
TOPVIA_PITCH = 0.76          # 0.26 via + 0.5 spacing (MIM.9: sea-of-via-on-top-plate spacing)

BOTVIA_GAP = 0.4             # MIM.5: min gap from fusetop edge to bottom-plate via2
BOTVIA_ENC = 0.4             # MIM.2: min enclosure of bottom-plate via2 within metal2
BOTVIA_SPACING = 0.3         # V2.2a min is 0.26; extra margin
PAD_HALF_W = 1.0             # bottom-plate metal3 pad: 2.0um wide (>= MT30.1a 1.8um)
PAD_TOP_GAP = 1.9            # metal3-pad-to-top-plate-metal3 spacing (>= MT30.2/3/4 1.8um)
PAD_HEIGHT = 2.0             # >= MT30.1a 1.8um in the other dimension too
M2_SOUTH_MARGIN = 0.4        # extra slack beyond the strict MIM.2 minimum

PAD_Y1 = -(FUSETOP_HALF + PAD_TOP_GAP)          # pad north edge
PAD_Y0 = PAD_Y1 - PAD_HEIGHT                     # pad south edge
_via_span = 2 * VIA_SIZE + BOTVIA_SPACING
_pad_mid_y = (PAD_Y1 + PAD_Y0) / 2
BOTVIA_Y0 = _pad_mid_y - _via_span / 2
BOTVIA_Y1 = _pad_mid_y + _via_span / 2
assert (-FUSETOP_HALF) - BOTVIA_Y1 >= BOTVIA_GAP - 1e-9  # MIM.5 gap, fusetop edge to via2

M2_X_HALF = FUSETOP_HALF + M2_MARGIN
M2_Y_NORTH = FUSETOP_HALF + M2_MARGIN
M2_Y_SOUTH = min(PAD_Y0, BOTVIA_Y0 - BOTVIA_ENC) - M2_SOUTH_MARGIN


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

    # --- mim_l_mk marker strip along the fusetop bottom edge ---
    cell.shapes(li["mim_l_mk"]).insert(_box(cx - fh, cy - fh, cx + fh, cy - fh + 0.1, dbu))

    # --- Metal2 bottom plate slab: MIM.3 margin on north/east/west, extended
    #     south far enough to enclose the relocated bottom-plate via2 ---
    cell.shapes(li["metal2"]).insert(
        _box(cx - M2_X_HALF, cy + M2_Y_SOUTH, cx + M2_X_HALF, cy + M2_Y_NORTH, dbu)
    )

    # --- cap_mk: superset of fusetop (MIM.7) ---
    cell.shapes(li["cap_mk"]).insert(
        _box(cx - M2_X_HALF, cy + M2_Y_SOUTH, cx + M2_X_HALF, cy + M2_Y_NORTH, dbu)
    )

    # --- Top plate: Metal3 exactly over the fusetop core. No extra tab needed --
    #     this bare 5x5 surface (already >> MT30.1a's 1.8um min) is itself the
    #     DAC_TOP landing pad; adjacent unit cells' top plates merge directly
    #     into one contiguous mesh in the array (Step 2), so no MT30.2/3/4
    #     inter-tab spacing is incurred there.
    cell.shapes(li["metal3"]).insert(_box(cx - fh, cy - fh, cx + fh, cy + fh, dbu))

    # --- Top plate via2 "sea of vias" inside fusetop, inset by TOPVIA_INSET (MIM.4) ---
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
            cell.shapes(li["via2"]).insert(
                _box(vx0, vy0, vx0 + VIA_SIZE, vy0 + VIA_SIZE, dbu)
            )

    # --- Bottom plate: 2x2 via2 array (MT30.8) south of fusetop, outside by
    #     BOTVIA_GAP (MIM.5), enclosed by metal2 by BOTVIA_ENC (MIM.2) ---
    for vx0 in (cx - VIA_SIZE - BOTVIA_SPACING / 2, cx + BOTVIA_SPACING / 2):
        for vy0 in (cy + BOTVIA_Y0, cy + BOTVIA_Y0 + VIA_SIZE + BOTVIA_SPACING):
            cell.shapes(li["via2"]).insert(
                _box(vx0, vy0, vx0 + VIA_SIZE, vy0 + VIA_SIZE, dbu)
            )

    # --- Bottom plate: separate Metal3 pad (own island, >=1.8um from the top
    #     plate's metal3 per MT30.2/3/4, >=1.8um in both dims per MT30.1a) ---
    cell.shapes(li["metal3"]).insert(
        _box(cx - PAD_HALF_W, cy + PAD_Y0, cx + PAD_HALF_W, cy + PAD_Y1, dbu)
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
