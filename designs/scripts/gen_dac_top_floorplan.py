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


# Top-level routing template.  Signal trunks are deliberately Manhattan:
# Metal2 is horizontal and Metal3 is vertical.  A route changes layer only
# through an explicit, generously-enclosed via stack.  This keeps different
# nets on separate tracks; the DRC deck does not know intended net names.
VIA_SIZE = 0.26
VIA_PAD = 0.40
ROUTE_W = 0.50


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


def _via_stack(top, layers, vias, x, y, low, high):
    """Connect inclusive metal levels low..high at one isolated landing."""
    for level in range(low, high + 1):
        top.shapes(layers[level]).insert(_box(x - VIA_PAD / 2, y - VIA_PAD / 2,
                                               x + VIA_PAD / 2, y + VIA_PAD / 2))
    for level in range(low, high):
        top.shapes(vias[level]).insert(_box(x - VIA_SIZE / 2, y - VIA_SIZE / 2,
                                             x + VIA_SIZE / 2, y + VIA_SIZE / 2))


def route_bit_template(top, layers, vias, bit, rail_y, points):
    """Route one bit's NAND/driver chain using the fixed M2-H/M3-V template.

    ``points`` makes child access coordinates explicit, so this same function
    can be reused for every bit once its placement-specific tracks are chosen.
    Only bit 4 is invoked at this checkpoint.
    """
    m1, m2, m3, _m4, m5 = (layers[n] for n in range(1, 6))
    nand_vdd, nand_gnd = points["nand_vdd"], points["nand_gnd"]
    drv_vdd, drv_gnd = points["drv_vdd"], points["drv_gnd"]

    # Supply drops: M5 vertical feeds, each with its own M2-to-M5 stack.
    # NAND supply pins are M1; driver supply pins already terminate on M2.
    for name, source, spine_y, m5_x, source_level in (
        ("nand_vdd", nand_vdd, 124.0, -266.0, 1),
        ("nand_gnd", nand_gnd, -128.0, -276.0, 1),
        ("drv_vdd", drv_vdd, 124.0, -150.0, 2),
        ("drv_gnd", drv_gnd, -128.0, -158.0, 2),
    ):
        sx, sy = source
        _via_stack(top, layers, vias, sx, sy, source_level, 2)
        _wire(top, m2, sx, sy, m5_x, sy)
        _via_stack(top, layers, vias, m5_x, sy, 2, 5)
        top.shapes(m5).insert(_box(m5_x - 3.0, sy - 3.0, m5_x + 3.0, sy + 3.0))
        # Metal5 is a 6um-wide power fabric in this stack; keep each drop
        # at backbone width rather than creating a narrow top-metal stub.
        _wire(top, m5, m5_x, sy, m5_x, spine_y, 6.0)

    # B input and SAMPLE_N use separated exterior tracks below the cells.
    # NAND A/B are M1 terminals: land an M1-to-M3 stack directly over each
    # terminal, so the M1 pad (not an assumed nearby access coordinate) joins
    # the child pin with full via enclosure.
    b4_x, b4_y = points["b4_label"]
    nand_a = points["nand_a"]
    # B4's label is on the PDK label purpose; its signal landing is Metal2.
    _via_stack(top, layers, vias, b4_x, b4_y, 2, 3)
    _wire(top, m2, b4_x, -16.0, nand_a[0], -16.0)
    _wire(top, m2, nand_a[0], -16.0, nand_a[0], nand_a[1])
    _via_stack(top, layers, vias, nand_a[0], nand_a[1], 1, 2)

    sample_n = points["sample_n"]
    nand_b = points["nand_b"]
    sample_stack_x = 84.0
    _wire(top, m2, sample_n[0], sample_n[1], sample_stack_x, sample_n[1])
    _via_stack(top, layers, vias, sample_stack_x, sample_n[1], 2, 3)
    _wire(top, m3, sample_stack_x, sample_n[1], sample_stack_x, -105.0)
    _wire(top, m2, sample_stack_x, -105.0, nand_b[0], -105.0)
    _wire(top, m3, nand_b[0], -105.0, nand_b[0], nand_b[1])
    _via_stack(top, layers, vias, nand_b[0], nand_b[1], 1, 3)

    # NAND output to driver gate: a local low-metal route below bit 4.
    nand_y = points["nand_y"]
    drv_gate = points["drv_gate"]
    _via_stack(top, layers, vias, nand_y[0], nand_y[1], 1, 3)
    _wire(top, m3, nand_y[0], nand_y[1], nand_y[0], -18.0)
    _wire(top, m2, nand_y[0], -18.0, drv_gate[0], -18.0)
    _wire(top, m3, drv_gate[0], -18.0, drv_gate[0], drv_gate[1])

    # Driver VOUT is Metal3.  The B4 backbone is Metal2, so the M3 leg must
    # finish in a real M2-to-M3 landing stack on the existing backbone.
    drv_out = points["drv_out"]
    rail_x, rail_y = points["rail"]
    _via_stack(top, layers, vias, drv_out[0], drv_out[1], 2, 3)
    _wire(top, m3, drv_out[0], drv_out[1], drv_out[0], 17.0)
    _wire(top, m2, drv_out[0], 17.0, rail_x, 17.0)
    _wire(top, m3, rail_x, 17.0, rail_x, rail_y)
    _via_stack(top, layers, vias, rail_x, rail_y, 2, 3)


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
    driver_x = {bit: -94.0 - 12.0 * bit for bit in range(8)}
    for bit in range(8):
        y = RAIL_Y[f"B{bit}"]
        dx = driver_x[bit]
        # The NAND2 row is kept beyond the complete driver envelope, rather
        # than immediately beside its own driver: the B4 NAND2 otherwise
        # intrudes on the much taller B5 driver.  This intentionally reserves
        # the intervening channel for the later NAND-to-driver routes.
        add(top, nand2, -208.0 - 12.0 * bit, y)
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
    top.shapes(li_m5).insert(box(-292.0, 121.0, 112.0, 127.0))
    top.shapes(li_m5).insert(box(-292.0, -131.0, 112.0, -125.0))
    label("VDD", -280.0, 124.0, li_m5lbl)
    label("0", -280.0, -128.0, li_m5lbl)

    # Name every top-level interface net in the top cell.  Text is placed on
    # the child access point (or corresponding array rail) so a flat
    # extracted view makes accidental merges immediately visible.
    for name, x, y, label_layer in (
        ("VIN", 97.0, -8.271, li_m3lbl), ("SAMPLE", 106.33, -8.08, li_m2lbl),
        ("SAMPLE_N", 88.33, -7.471, li_m2lbl), ("DAC_TOP", 105.79, -8.98, li_m4lbl),
        ("B0", -62.85, 57.36, li_m2lbl), ("B1", -62.85, -57.36, li_m2lbl),
        ("B2", -62.85, -38.24, li_m2lbl), ("B3", -62.85, -19.12, li_m2lbl),
        ("B5", -62.85, 19.12, li_m2lbl),
        ("B6", -62.85, 76.48, li_m2lbl), ("B7", -62.85, -76.48, li_m2lbl),
        # B4 raw digital input and the cap-array B4 rail are intentionally
        # different nets; the driver output alone joins the latter.
        ("B4", -230.0, -16.0, li_m2lbl), ("B4_RAIL", -62.85, 0.0, li_m2lbl),
        ("B4NAND", -200.0, -18.0, li_m2lbl),
    ):
        label(name, x, y, label_layer)

    # Bit-4 is the routing proof/template.  Keep every other bit untouched
    # until this connectivity pattern has been independently replicated.
    layers = {
        1: layout.layer(34, 0), 2: layout.layer(36, 0), 3: layout.layer(42, 0),
        4: layout.layer(46, 0), 5: li_m5,
    }
    vias = {
        1: layout.layer(35, 0), 2: layout.layer(38, 0),
        3: layout.layer(40, 0), 4: layout.layer(41, 0),
    }
    route_bit_template(top, layers, vias, 4, RAIL_Y["B4"], {
        # Absolute access coordinates = placed child origin + verified label
        # location in the respective child layout.
        "nand_vdd": (-256.23, 3.00), "nand_gnd": (-258.00, -10.75),
        "nand_a": (-255.66, -0.49), "nand_b": (-243.66, -0.49),
        "nand_y": (-241.00, -1.60),
        "drv_vdd": (-142.23, 15.53), "drv_gnd": (-142.21, -12.352),
        "drv_gate": (-143.53, -11.652), "drv_out": (-139.08, -10.952),
        "b4_label": (-230.0, -16.0), "rail": (-62.85, RAIL_Y["B4"]),
        "sample_n": (88.33, -7.471),
    })

    layout.write(OUT)
    b = top.bbox()
    print("wrote", OUT)
    print("top bbox um", *(round(v * DBU, 3) for v in (b.left, b.bottom, b.right, b.top)))


if __name__ == "__main__":
    main()
