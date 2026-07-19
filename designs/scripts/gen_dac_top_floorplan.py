#!/usr/bin/env python3
"""Hierarchical floorplan for the 8-bit DAC.

This instantiates the
already DRC/LVS-clean cap array, NAND2s, sized bottom-plate drivers, SAMPLE_N
inverter, and top-plate TG.  The rail-coordinate constants are derived from
gen_dac_cap_layout.py's routed Metal2 backbone plan.
"""

import klayout.db as db


OUT = "/foss/designs/dac/layout/dac_top_floorplan.gds"
DBU = 0.001

# Metal2 backbone y coordinates, in the cap_array coordinate system.
# B7/B6 use the exterior row channels.  The other values use BACKBONE_ROW.
RAIL_Y = {
    "B7": -76.48, "B1": -57.36, "B2": -38.24, "B4": 0.00,
    "B3": -19.12, "B5": 19.12, "B0": 57.36, "B6": 76.48,
}


def point(x, y):
    return db.Point(int(round(x / DBU)), int(round(y / DBU)))


def add(top, cell, x, y):
    top.insert(db.CellInstArray(cell.cell_index(), db.Trans(point(x, y))))


# Top-level routing template.  Signal trunks are deliberately Manhattan.
# A route changes layer only through an explicit, generously-enclosed via
# stack.  This keeps different nets on separate tracks; the DRC deck does
# not know intended net names, so cross-net *geometric* separation is the
# only thing that prevents an accidental short.
VIA_SIZE = 0.26
VIA_PAD = 0.40
ROUTE_W = 0.50

# ---------------------------------------------------------------------
# Per-bit floorplan placement.  nand2 is a single shared cell (identical
# pin geometry on every instance); the driver (unit_switch_bit<n>) is
# individually sized per bit, so its pin offsets vary and were extracted
# directly from unit_switch_checkpoint.gds (see designs/scripts, the
# extraction is not re-derivable from bit4's numbers alone).
NAND2_X = lambda bit: -208.0 - 12.0 * bit
DRIVER_X = lambda bit: -94.0 - 12.0 * bit

# nand2 pin offsets, relative to its own placement origin -- identical for
# every bit since only one nand2 cell is instantiated 8 times.
NAND2_PINS = {
    "vdd": (-0.23, 3.00), "gnd": (-2.00, -10.75),
    "a": (0.34, -0.49), "b": (12.34, -0.49), "y": (15.00, -1.60),
}

# unit_switch_bit<n> pin offsets, relative to each instance's own placement
# origin.  VDD/GND/VOUT real copper is on M2/M2/M3 respectively; the gate
# input (labelled bN_bar in the child cell) lands on M3.  Bit 7 alone is
# m=2 sized (wider), hence its different VOUT x-offset.
DRV_PINS = {
    0: {"vdd": (-0.230, 2.930), "gnd": (-0.210, -6.052), "gate": (-1.530, -5.352), "vout": (2.920, -4.652)},
    1: {"vdd": (-0.230, 3.770), "gnd": (-0.210, -6.472), "gate": (-1.530, -5.772), "vout": (2.920, -5.072)},
    2: {"vdd": (-0.230, 5.450), "gnd": (-0.210, -7.312), "gate": (-1.530, -6.612), "vout": (2.920, -5.912)},
    3: {"vdd": (-0.230, 8.810), "gnd": (-0.210, -8.992), "gate": (-1.530, -8.292), "vout": (2.920, -7.592)},
    4: {"vdd": (-0.230, 15.530), "gnd": (-0.210, -12.352), "gate": (-1.530, -11.652), "vout": (2.920, -10.952)},
    5: {"vdd": (-0.230, 28.970), "gnd": (-0.210, -19.072), "gate": (-1.530, -18.372), "vout": (2.920, -17.672)},
    6: {"vdd": (-0.230, 55.850), "gnd": (-0.210, -32.512), "gate": (-1.530, -31.812), "vout": (2.920, -31.112)},
    7: {"vdd": (-0.230, 55.850), "gnd": (-0.210, -59.392), "gate": (-1.530, -58.692), "vout": (5.730, -57.992)},
}

# Global, shared routing constants.
RAIL_X = -62.85
SAMPLE_STACK_X = 84.0
SAMPLE_TRUNK_Y = -105.0
SAMPLE_N_PT = (88.33, -7.471)
B_LABEL_DX, B_LABEL_DY = 26.0, -16.0
# Raw-B tracks are keyed to their bit's own label row, but offset away from
# the row itself: the M2->M5 supply stack at the preceding NAND VDD drop has
# pads on M3 too.  A +5 um per-bit lane clears that stack while preserving
# each bit's unique channel row.
B_TRACK_Y = lambda bit: RAIL_Y[f"B{bit}"] + B_LABEL_DY + 5.0
JOG_OFFSET = -18.0
# Bit 0's SAMPLE_N tap uniquely needs to reach the highest y of any bit
# (RAIL_Y[B0]=57.36, the top rail row) and its straight-line path would
# sweep across every other routed bit's NAND_Y jog track on the way up.
# Routing it via a detour column to the left of all nand2 bodies (verified
# collision-free against the other 6 bits' tracks) avoids that; see
# dac/WORKLOG.md for the verification method.
DETOUR_X_0 = -290.0
SUPPLY_POUR_W = 2.0
NAND_VDD_M5_OFF, NAND_GND_M5_OFF = -9.0, -15.0
# The driver VDD riser must stay on the driver side of its own column.
# A -9 um VDD offset aliases the next bit's VOUT x-coordinate (for bits
# 3--5), so its M2->M5 stack lands in that neighbour's output strap and
# shorts B4/B5/B6 rails to VDD.  Its positive, per-bit-indexed tracks remain
# separated by the 12 um column pitch and clear every VOUT access.  GND's
# original left-side track is already distinct and remains there.
DRV_VDD_M5_OFF, DRV_GND_M5_OFF = 6.0, -15.0
VDD_SPINE_Y, GND_SPINE_Y = 124.0, -128.0


def _box(x0, y0, x1, y1):
    # GF180's manufacturing grid is 5nm.  Child access labels can be on a
    # finer GDS coordinate, so all newly drawn geometry is snapped here.
    grid = 0.005
    snap = lambda v: round(v / grid) * grid
    return db.Box(int(round(snap(min(x0, x1)) / DBU)), int(round(snap(min(y0, y1)) / DBU)),
                  int(round(snap(max(x0, x1)) / DBU)), int(round(snap(max(y0, y1)) / DBU)))


def _wire(top, layer, x0, y0, x1, y1, width=ROUTE_W):
    half = width / 2
    if x0 == x1:
        top.shapes(layer).insert(_box(x0 - half, y0, x1 + half, y1))
    elif y0 == y1:
        top.shapes(layer).insert(_box(x0, y0 - half, x1, y1 + half))
    else:
        raise ValueError("routing template only permits Manhattan segments")


def _via_stack(top, layers, vias, x, y, low, high, pad=VIA_PAD):
    """Connect inclusive metal levels low..high at one isolated landing."""
    for level in range(low, high + 1):
        top.shapes(layers[level]).insert(_box(x - pad / 2, y - pad / 2,
                                               x + pad / 2, y + pad / 2))
    for level in range(low, high):
        top.shapes(vias[level]).insert(_box(x - VIA_SIZE / 2, y - VIA_SIZE / 2,
                                             x + VIA_SIZE / 2, y + VIA_SIZE / 2))


def route_supply(top, layers, vias, bit, rail_y):
    """VDD/0 drops for one bit's nand2 + driver, straight to the M5 spine.

    nand2 has zero M2/M3/M4/M5 content anywhere in its footprint, and the
    driver's own M2 VDD/GND strap is a narrow (~2.5um) column right at its
    pin -- so a local jog of a few um clears it. The only real constraint
    is M5-to-M5 spacing between DIFFERENT bits' VDD vs 0 drops, which a
    fixed +6um offset (== half the achievable margin on this cell's 12um
    placement pitch) keeps >= the 0.28um M5 spacing rule with room to
    spare, using a narrow (2um) pour rather than a wide bus bar.
    """
    m1, m2, _m3, _m4, m5 = (layers[n] for n in range(1, 6))
    nx, dxv = NAND2_X(bit), DRIVER_X(bit)
    drops = (
        ("nand_vdd", (nx + NAND2_PINS["vdd"][0], rail_y + NAND2_PINS["vdd"][1]), 1,
         nx + NAND_VDD_M5_OFF, VDD_SPINE_Y),
        ("nand_gnd", (nx + NAND2_PINS["gnd"][0], rail_y + NAND2_PINS["gnd"][1]), 1,
         nx + NAND_GND_M5_OFF, GND_SPINE_Y),
        ("drv_vdd", (dxv + DRV_PINS[bit]["vdd"][0], rail_y + DRV_PINS[bit]["vdd"][1]), 2,
         dxv + DRV_VDD_M5_OFF, VDD_SPINE_Y),
        ("drv_gnd", (dxv + DRV_PINS[bit]["gnd"][0], rail_y + DRV_PINS[bit]["gnd"][1]), 2,
         dxv + DRV_GND_M5_OFF, GND_SPINE_Y),
    )
    for _name, (sx, sy), source_level, m5_x, spine_y in drops:
        _via_stack(top, layers, vias, sx, sy, source_level, 2)
        _wire(top, m2, sx, sy, m5_x, sy)
        _via_stack(top, layers, vias, m5_x, sy, 2, 5)
        half = SUPPLY_POUR_W / 2
        top.shapes(m5).insert(_box(m5_x - half, sy - half, m5_x + half, sy + half))
        _wire(top, m5, m5_x, sy, m5_x, spine_y, SUPPLY_POUR_W)


def route_b_label(top, layers, vias, bit, rail_y):
    """B<bit> (raw digital input, placed in the open channel just past the
    nand2 body) -> NAND2 A.  Its shared-channel trunk stays on the
    bit-unique M3 label lane, with direct via stacks only at the M2 label
    and M1 NAND pin.  M2 is reserved for the supply drops and must not be
    used for this cross-channel run."""
    m3 = layers[3]
    nx = NAND2_X(bit)
    nand_a = (nx + NAND2_PINS["a"][0], rail_y + NAND2_PINS["a"][1])
    b_label = (nx + B_LABEL_DX, rail_y + B_LABEL_DY)
    track_y = B_TRACK_Y(bit)
    _via_stack(top, layers, vias, b_label[0], b_label[1], 2, 3)
    _wire(top, m3, b_label[0], b_label[1], b_label[0], track_y)
    _wire(top, m3, b_label[0], track_y, nand_a[0], track_y)
    _wire(top, m3, nand_a[0], track_y, nand_a[0], nand_a[1])
    _via_stack(top, layers, vias, nand_a[0], nand_a[1], 1, 3)
    return b_label


def route_sample_n_tap(top, layers, vias, bit, rail_y, detour=False):
    """SAMPLE_N (shared trunk on M4, tapped by every bit's NAND2 B) -> that
    bit's NAND2 B.  M4 is empty in both nand2 and unit_switch_bit<n>, so a
    trunk running the length of the channel cannot hit any cell's own
    copper; the only remaining hazard is THIS wire vs. the other new
    routes sharing M4 (NAND_Y jog, VOUT->rail), verified collision-free
    for bits 0-6 with JOG_OFFSET=-18 (see route_nand_y_jog docstring).
    Bit 0 alone needs the DETOUR_X_0 dogleg: its own tap has to climb
    higher (to RAIL_Y[B0]) than any other bit, and a straight vertical
    at its native x would sweep across bits 1-6's NAND_Y jog tracks."""
    m4 = layers[4]
    nx = NAND2_X(bit)
    nand_b = (nx + NAND2_PINS["b"][0], rail_y + NAND2_PINS["b"][1])
    if detour:
        mid_y = nand_b[1] - 2.0
        _wire(top, m4, nand_b[0], SAMPLE_TRUNK_Y, DETOUR_X_0, SAMPLE_TRUNK_Y)
        _wire(top, m4, DETOUR_X_0, SAMPLE_TRUNK_Y, DETOUR_X_0, mid_y)
        _wire(top, m4, DETOUR_X_0, mid_y, nand_b[0], mid_y)
        _wire(top, m4, nand_b[0], mid_y, nand_b[0], nand_b[1])
    else:
        _wire(top, m4, nand_b[0], SAMPLE_TRUNK_Y, nand_b[0], nand_b[1])
    _via_stack(top, layers, vias, nand_b[0], nand_b[1], 1, 4)


def route_nand_y_jog(top, layers, vias, bit, rail_y):
    """NAND2 Y -> driver gate, on Metal4 at a per-bit height RAIL_Y+
    JOG_OFFSET.  M4 is empty in nand2/unit_switch_bit<n>, eliminating any
    cell-internal-strap collision (the original bit4-only routing used M3
    for this and got away with it purely because no other bit's M3
    content was present yet -- generalizing on M3 hits the drivers' own
    VOUT/gate M3 straps, which are drawn full-height on some bits).  The
    remaining hazard is this bit's own jog line/stubs vs. every OTHER
    bit's jog line/stubs and the SAMPLE_N trunk; JOG_OFFSET=-18 (mirroring
    bit4's original, already-verified value) was checked bit-by-bit for
    bits 0-6 and is collision-free. Bit 7's driver is exceptionally large
    (m=2) and needs its own dogleg -- deferred, see WORKLOG.
    """
    nx, dxv = NAND2_X(bit), DRIVER_X(bit)
    nand_y = (nx + NAND2_PINS["y"][0], rail_y + NAND2_PINS["y"][1])
    gate = (dxv + DRV_PINS[bit]["gate"][0], rail_y + DRV_PINS[bit]["gate"][1])
    jy = rail_y + JOG_OFFSET
    m4 = layers[4]
    _via_stack(top, layers, vias, nand_y[0], nand_y[1], 1, 4)
    _wire(top, m4, nand_y[0], nand_y[1], nand_y[0], jy)
    _wire(top, m4, nand_y[0], jy, gate[0], jy)
    _wire(top, m4, gate[0], jy, gate[0], gate[1])
    _via_stack(top, layers, vias, gate[0], gate[1], 3, 4)


def route_sample_n_source(top, layers, vias):
    """One-time descent from the SAMPLE_N/inv1 output pin down to the
    shared M4 trunk.  Drawn once, outside the per-bit loop -- every bit's
    route_sample_n_tap only draws its OWN branch off the trunk.  The M2->M4
    via stack lands at SAMPLE_STACK_X (84.0), not at the pin's own x
    (88.33): that x is inside/adjacent to the inv1 cell's own M3/M4
    footprint, and a via stack landing there is too close to it (M3.2a/
    M4.2a spacing violations) -- a short M2 jog first, matching bit4's
    original approach, sidesteps that entirely."""
    m2, m4 = layers[2], layers[4]
    sx, sy = SAMPLE_N_PT
    _wire(top, m2, sx, sy, SAMPLE_STACK_X, sy)
    _via_stack(top, layers, vias, SAMPLE_STACK_X, sy, 2, 4)
    _wire(top, m4, SAMPLE_STACK_X, sy, SAMPLE_STACK_X, SAMPLE_TRUNK_Y)


def route_vout_rail(top, layers, vias, bit, rail_y):
    """Driver VOUT -> that bit's cap-array rail.  The channel-crossing
    stretch (past every OTHER bit's driver) is Metal4 -- VOUT's own real
    copper is M3 (a tall strap reaching the full driver height on some
    bits), so a shared M3 trunk crossing the channel would run straight
    into other bits' M3 VOUT/gate straps (bit4's original single-bit
    routing used a same-layer M3 overlap trick that does not generalize
    for exactly this reason).  The wire drops to M2 at M4_TO_M2_HANDOFF_X,
    BEFORE entering cap_array's own footprint (bbox starts at x=-69.19):
    cap_array's M3 layer is not per-row like M2 is -- it merges into one
    ~250um^2 connected mesh spanning the array's entire bbox (confirmed by
    inspecting cap_array.gds in isolation, so it is not an artifact of this
    routing), almost certainly the shared VIN/shield distribution.  Any new
    M3 shape that reaches into the array's bbox joins that one mesh,
    which is exactly the B<n><->B<m> cross-bit short this checkpoint's
    distinctness checker is built to catch (it did, on the first attempt
    at this routing -- see dac/WORKLOG.md).  M2 in cap_array, by contrast,
    is one separate polygon PER RAIL ROW (verified), so an M2 approach
    landing at (RAIL_X, rail_y) only ever joins that one row's rail.
    The rail landing uses a widened pad: the cap array's own rail metal
    for at least one row (B3) has a small separate M2 tab sitting only
    ~0.08um from the row's main bar edge, tighter than the default
    0.4x0.4 pad can bridge without a residual min-spacing gap.
    """
    m2, m4 = layers[2], layers[4]
    dxv = DRIVER_X(bit)
    drv_out = (dxv + DRV_PINS[bit]["vout"][0], rail_y)
    rail = (RAIL_X, rail_y)
    handoff_x = -75.0
    _via_stack(top, layers, vias, drv_out[0], drv_out[1], 3, 4)
    _wire(top, m4, drv_out[0], rail_y, handoff_x, rail_y)
    _via_stack(top, layers, vias, handoff_x, rail_y, 2, 4)
    _wire(top, m2, handoff_x, rail_y, rail[0], rail_y)
    top.shapes(m2).insert(_box(rail[0] - 0.35, rail[1] - 0.35, rail[0] + 0.35, rail[1] + 0.35))


def route_bit(top, layers, vias, bit, detour_sample_n=False):
    rail_y = RAIL_Y[f"B{bit}"]
    route_supply(top, layers, vias, bit, rail_y)
    route_b_label(top, layers, vias, bit, rail_y)
    route_sample_n_tap(top, layers, vias, bit, rail_y, detour=detour_sample_n)
    route_nand_y_jog(top, layers, vias, bit, rail_y)
    route_vout_rail(top, layers, vias, bit, rail_y)


def main():
    layout = db.Layout()
    layout.dbu = DBU
    # read() preserves the component hierarchy; no flattening and no geometry
    # is added to any source component cell.
    # GDS PCell helper names recur across the independently-written source
    # files.  Rename colliding helper cells while reading, rather than merge
    # them (KLayout's default AddToCell would corrupt their device geometry).
    read_opt = db.LoadLayoutOptions()
    read_opt.cell_conflict_resolution = db.LoadLayoutOptions.RenameCell
    layout.read("/foss/designs/dac/layout/cap_array.gds", read_opt)
    layout.read("/foss/designs/dac/layout/unit_switch_checkpoint.gds", read_opt)
    layout.read("/foss/designs/dac/layout/dac_logic_checkpoint.gds", read_opt)

    top = layout.create_cell("dac_top_floorplan")
    cap = layout.cell("cap_array")
    nand2 = layout.cell("nand2")
    inv1 = layout.cell("inv1")
    tgate = layout.cell("tgate")
    assert all((cap, nand2, inv1, tgate))
    add(top, cap, 0, 0)

    # Eight y-aligned left-edge columns.  Each NAND2 is upstream (farther
    # left) of its correctly-sized rail driver.  Staggering B0/B6 horizontally
    # avoids their large-cell vertical envelope overlap while preserving the
    # driver-to-rail alignment and open routing channels between columns.
    # 12 um pitch gives each different-sized driver its own horizontal lane;
    # the closest backbone rows (B3/B4/B5) otherwise cause physical overlap.
    driver_x = {bit: DRIVER_X(bit) for bit in range(8)}
    for bit in range(8):
        y = RAIL_Y[f"B{bit}"]
        dx = driver_x[bit]
        # The NAND2 row is kept beyond the complete driver envelope, rather
        # than immediately beside its own driver: the B4 NAND2 otherwise
        # intrudes on the much taller B5 driver.  This intentionally reserves
        # the intervening channel for the later NAND-to-driver routes.
        add(top, nand2, NAND2_X(bit), y)
        add(top, layout.cell(f"unit_switch_bit{bit}"), dx, y)

    # TG at the right-side DAC_TOP mesh access; inv1 sits just above it,
    # leaving a direct SAMPLE_N channel to the TG and a broad VIN corridor.
    add(top, tgate, 88.0, 0.0)
    add(top, inv1, 112.0, 18.0)

    # This checkpoint keeps the global supply spines on M5.  The top-level
    # signal labels below are deliberately placed at the corresponding child
    # access points so the next routing pass has an explicit net-name map.
    li_m5 = layout.layer(81, 0)
    li_m1lbl = layout.layer(34, 10)
    li_m2lbl = layout.layer(36, 10)
    li_m3lbl = layout.layer(42, 10)
    li_m4lbl = layout.layer(46, 10)
    li_m5lbl = layout.layer(81, 10)
    def box(x0, y0, x1, y1):
        return db.Box(int(round(x0 / DBU)), int(round(y0 / DBU)),
                      int(round(x1 / DBU)), int(round(y1 / DBU)))
    def label(text, x, y, label_layer):
        """Put text on the PDK label purpose for the metal it contacts."""
        top.shapes(label_layer).insert(db.Text(text, int(round(x / DBU)), int(round(y / DBU))))

    # Wide, labelled supply spines.  The schematic global ground spelling is
    # exactly `0`, not GND/DVSS.
    # Left edge extended from -292 to -300: bit6's nand_gnd M5 drop lands
    # at NAND2_X(6)+NAND_GND_M5_OFF = -295, just past the original -292
    # edge (bit7's own drops, if routed later, will need -307).
    top.shapes(li_m5).insert(box(-300.0, 121.0, 112.0, 127.0))
    top.shapes(li_m5).insert(box(-300.0, -131.0, 112.0, -125.0))
    label("VDD", -280.0, 124.0, li_m5lbl)
    label("0", -280.0, -128.0, li_m5lbl)

    # Name every top-level interface net in the top cell.  Text is placed on
    # the child access point (or corresponding array rail) so a flat
    # extracted view makes accidental merges immediately visible.  Every
    # bit's raw digital input (B<n>) is labelled in the open channel just
    # past its own nand2 body (nand2_x+26, RAIL_Y-16); the cap-array rail
    # landing gets its own, distinct B<n>_RAIL label so the two never
    # collide even before this bit's B path is drawn.
    for name, x, y, label_layer in (
        ("VIN", 97.0, -8.271, li_m3lbl), ("SAMPLE", 106.33, -8.08, li_m2lbl),
        ("SAMPLE_N", 88.33, -7.471, li_m2lbl), ("DAC_TOP", 105.79, -8.98, li_m4lbl),
    ):
        label(name, x, y, label_layer)
    for bit in range(8):
        ry = RAIL_Y[f"B{bit}"]
        label(f"B{bit}_RAIL", RAIL_X, ry, li_m2lbl)
        label(f"B{bit}", NAND2_X(bit) + B_LABEL_DX, ry + B_LABEL_DY, li_m2lbl)

    layers = {
        1: layout.layer(34, 0), 2: layout.layer(36, 0), 3: layout.layer(42, 0),
        4: layout.layer(46, 0), 5: li_m5,
    }
    vias = {
        1: layout.layer(35, 0), 2: layout.layer(38, 0),
        3: layout.layer(40, 0), 4: layout.layer(41, 0),
    }

    # SAMPLE_N shared trunk: one continuous M4 bar at SAMPLE_TRUNK_Y,
    # spanning from the source descent (SAMPLE_STACK_X) out to DETOUR_X_0
    # (left of every routed bit's own nand_b tap column) so every bit's
    # vertical stub -- drawn individually in route_sample_n_tap -- lands
    # on the same wire instead of 7 disconnected stubs.
    route_sample_n_source(top, layers, vias)
    _wire(top, layers[4], SAMPLE_STACK_X, SAMPLE_TRUNK_Y, DETOUR_X_0, SAMPLE_TRUNK_Y)

    # Bits routed this checkpoint: 0-6 (4 was the pre-existing template;
    # 0,1,2,3,5,6 are new).  Bit 7's exceptionally large (m=2) driver needs
    # its own dogleg beyond this pass's verified track assignment -- see
    # dac/WORKLOG.md for what remains.
    for bit in (0, 1, 2, 3, 4, 5, 6):
        route_bit(top, layers, vias, bit, detour_sample_n=(bit == 0))

    layout.write(OUT)
    b = top.bbox()
    print("wrote", OUT)
    print("top bbox um", *(round(v * DBU, 3) for v in (b.left, b.bottom, b.right, b.top)))


if __name__ == "__main__":
    main()
