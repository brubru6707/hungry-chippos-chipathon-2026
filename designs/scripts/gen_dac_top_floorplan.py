#!/usr/bin/env python3
"""Placement-only hierarchical floorplan for the 8-bit DAC.

This deliberately creates no interconnect geometry: it only instantiates the
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

    layout.write(OUT)
    b = top.bbox()
    print("wrote", OUT)
    print("top bbox um", *(round(v * DBU, 3) for v in (b.left, b.bottom, b.right, b.top)))


if __name__ == "__main__":
    main()
