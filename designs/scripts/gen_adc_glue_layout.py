#!/usr/bin/env python3
"""
Generate the ADC top-level glue block (adc_glue) for gf180mcuD variant=D
-- the 6 glue gates of adc_top/schematic/adc_top.sch (INT-8, see
docs/pin_contracts.md section 4):

  x_inv_ck  : CK = INV(CLK)         (comparator strobe phase)
  x_inv_smp : SAMPLE = INV(RST_N)   (DAC_TOP reset phase)
  x_ib1/x_ib2 : identical inverter buffers on VOUT1/VOUT2 -- MUST be the
      same cell placed adjacently so the comparator sees state-independent
      symmetric loads (the INT-5 sticky-decision finding: a bare NAND SR
      latch presents state-dependent Miller input cap and biases near-rail
      decisions toward repeating the previous one)
  x_nq/x_nqb : buffered NOR SR decision latch
      CMP_OUT = NOR(V2B, QB), QB = NOR(V1B, CMP_OUT)

Reuses the SAR leaf cells (inv, nor2 -- LVS/DRC-proven under SAR-5/6) and
the SAR row machinery verbatim: _place_row + channel_route (one exclusive
M2 track per net, M3 drops) + _supply_straps, exactly like build_dff.
Instance/net names match adc_top/sim/adc_top_subckt.spice lines
x_inv_ck/x_inv_smp/x_ib1/x_ib2/x_nq/x_nqb.

Output: adc_top/layout/adc_glue.gds (topcell adc_glue).
LVS reference: adc_top/layout/refs/adc_glue_ref.spice (native M elements
-- X-calls to undefined subckts silently extract 0 devices = false pass).
"""

import sys

sys.path.insert(0, "/foss/designs/designs/scripts")

import klayout.db as db  # noqa: E402

from gen_sar_layout import (  # noqa: E402
    _place_row,
    _supply_straps,
    build_inv,
    build_nor2,
    channel_route,
    snap_to_grid,
)

# Leaf pin -> net, straight from adc_top_subckt.spice (inv: VDD vin vout
# VSS; nor2: VDD A B Z VSS). x_ib1 and x_ib2 side by side, then the two
# NOR gates -- the latch cluster stays compact and symmetric.
GLUE_INSTS = [
    ("x_inv_ck", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "CLK", "vout": "CK"}),
    ("x_inv_smp", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "RST_N", "vout": "SAMPLE"}),
    ("x_ib1", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "VOUT1", "vout": "V1B"}),
    ("x_ib2", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "VOUT2", "vout": "V2B"}),
    ("x_nq", "nor2", {"VDD": "VDD", "VSS": "VSS", "A": "V2B", "B": "QB", "Z": "CMP_OUT"}),
    ("x_nqb", "nor2", {"VDD": "VDD", "VSS": "VSS", "A": "V1B", "B": "CMP_OUT", "Z": "QB"}),
]

GLUE_PORTS = [
    ("CLK", "CLK"), ("CK", "CK"), ("RST_N", "RST_N"), ("SAMPLE", "SAMPLE"),
    ("VOUT1", "VOUT1"), ("VOUT2", "VOUT2"), ("CMP_OUT", "CMP_OUT"),
]


def build_adc_glue(layout, cells):
    top = layout.create_cell("adc_glue")
    pin_list, supply_pins, _right = _place_row(layout, top, cells, GLUE_INSTS)
    y_top, ex_next, _pads = channel_route(layout, top, pin_list, GLUE_PORTS, y_ch0=1.0)
    _supply_straps(layout, top, supply_pins, y_top, ex_next)
    snap_to_grid(top)
    return top


def main():
    layout = db.Layout()
    layout.dbu = 0.001
    cells = {
        "inv": build_inv(layout),
        "nor2": build_nor2(layout),
    }
    top = build_adc_glue(layout, cells)
    b = top.bbox()
    options = db.SaveLayoutOptions()
    options.write_context_info = False
    out = "/foss/designs/adc_top/layout/adc_glue.gds"
    layout.write(out, options)
    print("wrote %s topcell=%s size=%.2f x %.2f um" % (
        out, top.name, b.width() * layout.dbu, b.height() * layout.dbu))


if __name__ == "__main__":
    main()
