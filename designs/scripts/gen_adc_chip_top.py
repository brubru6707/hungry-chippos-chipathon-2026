#!/usr/bin/env python3
"""
INT-8 / Gate 5: assemble the full ADC chip block (topcell adc_top) for
padring slot BV (550 x 1110 um) from the four proven sub-blocks:

  dac/layout/dac_top_floorplan.gds   (dac_top_floorplan, 443.0 x 270.2, M1..M5)
  comparator/layout/strongarm.gds    (strongarm, 83.25 x 49.63, M1/M2 only, dbu=0.005!)
  sar_logic/layout/sar_folded.gds    (sar_logic 3-row fold, 457.93 x 130.23, poly..M4)
  adc_top/layout/adc_glue.gds        (adc_glue, 42.54 x 17.66, poly..M3)

Floorplan (chip um, origin = slot lower-left):
  SAR   mirrored about the y axis (fold port column faces WEST), bbox
        x 85..542.93, y 39.77..170; ports = M4 pads at x 91.59..101.99.
  band  y 170..280: glue (x 339.3..381.84, y 209.6..227.3) + comparator
        (x 419.99..503.24, y 194.87..244.5) + all inter-block lanes.
  DAC   x 80..523, y 280..550.2 (translate +390, +416.87).
  pins  13 labeled M5 pads on the south edge (padring hookup happens at
        chipathon integration; labels are the contract).

Routing model (correct by construction, verified by the built-in
checkers below, then by DRC/LVS):
  - every chip-level wire belongs to exactly one net and is drawn from
    the explicit tables in build_routes(); no autorouting.
  - one exclusive lane (y for horizontals / x for verticals) per net and
    layer region; crossings only ever pair different layers. The lane
    orderings follow the port-escape rule: a horizontal at lane y must
    not cross a foreign vertical whose span contains y - see the
    derivation comments at each table.
  - DAC entries use probed-free corridors (assert_clear regions):
    B0..B7 enter from the WEST edge on M3 at pin_y-1.0 (the driver-area
    corridor that is empty on M3), with a 1 um M3 stub up at pin x
    merging into each B net's own M3 riser. SAMPLE/DAC_TOP/VIN use the
    east side: the only free east window is local y 13.5..21.2 (M4+M5);
    VIN ties to VSS right at the DAC's east GND comb (local x 131.8..133).
  - self-checks before writing:
      (1) attach-point coverage: every attach lands on metal of the
          intended block net (point-inside probes);
      (2) corridor clearance: every route shape keeps >= min spacing to
          all BLOCK shapes on its layer, except whitelisted attach boxes;
      (3) cross-net clearance among chip-level routes (same layer,
          different nets, >= min spacing).

Run inside the container (needs HOME/USER + klayout on PATH for the
follow-up DRC only; this script itself is pure klayout.db):
  docker exec -e HOME=/headless -e USER=headless sar_sim \
    python3 /foss/designs/designs/scripts/gen_adc_chip_top.py
"""

import sys

import klayout.db as db

DBU = 0.001

# ----------------------------------------------------------------------
# layers
M1, M2, M3, M4, M5 = (34, 0), (36, 0), (42, 0), (46, 0), (81, 0)
V1, V2, V3, V4 = (35, 0), (38, 0), (40, 0), (41, 0)
M5LBL = (81, 10)
METALS = {1: M1, 2: M2, 3: M3, 4: M4, 5: M5}
VIAS = {1: V1, 2: V2, 3: V3, 4: V4}

W = 0.5        # default route width (proven by the DAC top-level routes)
W_COL = 0.4    # port-column verticals: the SAR fold ports sit at a
               # 0.79-0.80 um pitch, so 0.5 um wires would leave only a
               # 0.29 um gap (< M4/M5 0.30 min space) between neighbors
W3 = 0.32      # M3 DAC-entry lane width (matches block-internal M3)
VIA_PAD = 0.4  # via landing pad (0.26 um cut + 0.07 enclosure each side)
# Mn.2a-style min spacing per layer; M5 = MetalTop@11K has MT.1=0.44um
# min width / MT.2a=0.46um min spacing (metaltop.drc), much stricter
# than M1..M4 -- every M5 wire is >= 0.5 wide and 0.46-spaced
SPACING = {1: 0.31, 2: 0.30, 3: 0.30, 4: 0.30, 5: 0.46}

# ----------------------------------------------------------------------
# placements
SAR_MX = 542.93   # chip_x = SAR_MX - local_x (mirror about y axis)
SAR_DY = 170.0    # chip_y = local_y + SAR_DY
DAC_DX, DAC_DY = 390.0, 416.87
CMP_DX, CMP_DY = 460.0, 215.13
GLUE_DX, GLUE_DY = 339.3, 219.0

# Padframe variant BV, from adc_top/padframe_defs/BV/A13_BV.def:
# DIEAREA (0 0) (110000 222000) at 200 dbu/um. The 0/0 boundary must equal
# this exactly -- the gds audit rejects a boundary sized to our drawn
# extent ("one bounding box on layer 0/0 that matches a defined block
# size"). BH (1110 x 550) is the other offered variant, but our drawn
# height is 549.7 and reaches y=550.2, so it would not fit BH without
# moving every block down.
SLOT_W, SLOT_H = 550.0, 1110.0

# SAR fold port column (local fold coords from sar_folded.gds labels)
SAR_PORTS_LOCAL = {
    "VDD": (440.94, -3.0), "VSS": (441.74, -0.9),
    "BIT_7": (442.54, -44.66), "BIT_6": (443.34, -46.05),
    "BIT_5": (444.13, -47.45), "BIT_4": (444.94, -88.77),
    "BIT_3": (445.74, -90.17), "BIT_2": (446.54, -91.56),
    "BIT_1": (447.34, -92.97), "BIT_0": (448.13, -94.36),
    "EOC": (448.94, -41.86), "RST_N": (449.74, -2.29),
    "CMP_OUT": (450.54, -43.26), "CLK": (451.34, -0.2),
}
SAR_PORT = {n: (round(SAR_MX - x, 3), round(y + SAR_DY, 3))
            for n, (x, y) in SAR_PORTS_LOCAL.items()}

# glue port pads (M3, local label (x, 8.1)); pad order re-cut 2026-07-31
# so CLK/CMP_OUT/RST_N pad x matches their SAR port x order (see
# gen_adc_glue_layout.py GLUE_PORTS comment)
GLUE_PORTS_LOCAL = {
    "CLK": 35.91, "CMP_OUT": 36.71, "RST_N": 37.51, "CK": 38.31,
    "SAMPLE": 39.11, "VOUT1": 39.91, "VOUT2": 40.71, "VDD": 41.51,
    "VSS": 42.31,
}
GLUE_PAD_Y = 8.1 + GLUE_DY               # 227.1
GLUE_PAD = {n: (round(x + GLUE_DX, 3), GLUE_PAD_Y)
            for n, x in GLUE_PORTS_LOCAL.items()}

# comparator pins (M1 label position, local um; M1 pads verified around them)
CMP_PINS_LOCAL = {
    "CK": (-38.94, 20.9), "VDD": (27.04, 24.34), "VIN1": (-6.12, -6.03),
    "VIN2": (10.0, -5.75), "VOUT1": (-14.2, 12.43), "VOUT2": (17.98, 12.27),
    "VSS": (4.13, -19.64),
}
# stack points chosen INSIDE the verified M1 pad extents
CMP_STACK_LOCAL = {
    "CK": (-38.3, 20.9), "VDD": (27.04, 23.7), "VIN1": (-6.3, -6.2),
    "VIN2": (10.3, -6.2), "VOUT1": (-13.4, 12.0), "VOUT2": (17.3, 12.27),
    "VSS": (4.0, -19.0),
}
CMP_PIN = {n: (round(x + CMP_DX, 3), round(y + CMP_DY, 3))
           for n, (x, y) in CMP_STACK_LOCAL.items()}

# DAC pin geometry (local dac coords)
DAC_B_PINS = {  # label position on M2; M3 riser of each B net sits at pin x
    "BIT_0": (-182.0, 41.36), "BIT_1": (-194.0, -73.36),
    "BIT_2": (-206.0, -54.24), "BIT_3": (-218.0, -35.12),
    "BIT_4": (-230.0, -16.0), "BIT_5": (-242.0, 3.12),
    "BIT_6": (-254.0, 60.48), "BIT_7": (-266.0, -92.48),
}
DAC_W_EDGE = DAC_DX - 310.0        # 80.0 chip x of DAC west edge
DAC_E_EDGE = DAC_DX + 133.0        # 523.0

# south pad row
PAD_Y0, PAD_Y1 = 8.0, 16.0
PAD_HALF = 4.0
PIN_PADS = {   # net -> pad center x
    "CLK": 110.0, "RST_N": 122.0, "EOC": 134.0,
    "BIT_0": 146.0, "BIT_1": 158.0, "BIT_2": 170.0, "BIT_3": 182.0,
    "BIT_4": 194.0, "BIT_5": 206.0, "BIT_6": 218.0, "BIT_7": 230.0,
    "VSS": 242.0, "VDD": 254.0, "VIN": 453.88,
}
# south fan-out jog y (M4): must INCREASE with port x (a jog at y crosses
# the descending stubs of ports east of it, which stop at their own
# higher jog y)
JOG_Y = {"CLK": 23.0, "RST_N": 23.8, "EOC": 24.6,
         "BIT_0": 25.4, "BIT_1": 26.2, "BIT_2": 27.0, "BIT_3": 27.8,
         "BIT_4": 28.6, "BIT_5": 29.4, "BIT_6": 30.2, "BIT_7": 31.0,
         "VSS": 31.8, "VDD": 32.6}

# north band lanes (M4) for BIT port->bus: must INCREASE with port x
OUT_PINS = {"EOC", "BIT_0", "BIT_1", "BIT_2", "BIT_3", "BIT_4",
            "BIT_5", "BIT_6", "BIT_7"}

BAND_LANE = {"BIT_0": 181.0, "BIT_1": 182.0, "BIT_2": 183.0,
             "BIT_3": 184.0, "BIT_4": 185.0, "BIT_5": 186.0,
             "BIT_6": 187.0, "BIT_7": 188.0}
# west bus verticals (M4): x must INCREASE with band lane so a westward
# horizontal only crosses bus slots whose verticals START above it
BUS_X = {"BIT_0": 58.0, "BIT_1": 58.8, "BIT_2": 59.6, "BIT_3": 60.4,
         "BIT_4": 61.2, "BIT_5": 62.0, "BIT_6": 62.8, "BIT_7": 63.6}

# M5 band lanes (west group -> glue). Two exclusive-lane rules must hold
# simultaneously: (a) at the SAR port column a lane must not cross a
# foreign port vertical whose top (= its lane) is above it -> lane y
# DECREASES with port x; (b) at the glue a lane must not cross a foreign
# glue riser whose start (= its lane) is below it -> lane y DECREASES
# with pad x. Solvable because the glue pad order was re-cut to match
# the port order: CLK (91.59/375.21) > CMP_OUT (92.39/376.01) >
# RST_N (93.19/376.81).
M5_LANE = {"CLK": 195.0, "CMP_OUT": 193.5, "RST_N": 192.0}
# CLK/CMP_OUT/RST_N leave the port column below the lowest BIT band lane
# (181) so BIT M4 horizontals never meet their M4. MT.2a (0.46um) forbids
# M5 verticals at the 0.8um port pitch, so each net jogs WEST on M4 (at a
# staggered y -- a jog crosses only foreign stubs that stop below it) to
# its own M5 riser x at a 1.5um pitch: net -> (m5_x, m4_jog_y).
COL_XFER = {"CLK": (89.5, 178.5), "CMP_OUT": (91.0, 179.3),
            "RST_N": (92.5, 180.1)}
GLUE_TOP_Y = 228.8     # glue approach altitude (via pads row above glue)

# supply spines (M5) on the west side + branches under the band
VSS_SPINE_X0, VSS_SPINE_X1 = 42.0, 46.0
VDD_SPINE_X0, VDD_SPINE_X1 = 30.0, 34.0
VSS_SPINE_Y0, VSS_SPINE_Y1 = 26.0, 291.87
# VDD spine reaches down INTO its south band (y 0.5..3.5): its x range
# (30..34) is west of the VSS band (x >= 42), so no crossing — unlike
# VSS, whose spine stops at 26 and dives under the VDD band on M4
VDD_SPINE_Y0, VDD_SPINE_Y1 = 0.5, 543.87
DAC_GND_Y0, DAC_GND_Y1 = 285.87, 291.87   # DAC "0" spine west face band
DAC_VDD_Y0, DAC_VDD_Y1 = 537.87, 543.87
VSS_BRANCH_Y = 174.0   # M5 band branches (between SAR top 170 and the
VDD_BRANCH_Y = 177.0   # M4 band lanes at 181+; M5 verticals start at 179+)

# east channel verticals
SAMPLE_CH_X = 536.0
DACTOP_CH_X = 544.0
SAMPLE_WIN_Y = DAC_DY + 15.0    # 431.87  M4 east window lane (local y 15)
DACTOP_WIN_Y = DAC_DY + 19.0    # 435.87  M5 east window lane (local y 19)
DACTOP_RISE_X = DAC_DX + 107.0  # 497.0   M5 rise from the mesh handoff bar
SAMPLE_DESC_X = DAC_DX + 109.0  # 499.0   M4 descent onto the SAMPLE trunk
SAMPLE_TRUNK_Y = DAC_DY + 6.0   # 422.87  via3 point on SAMPLE's M3 trunk
# DAC VIN port tie-to-VSS: attach on VIN's M3 arm (local y -8.27, spans
# x 87.6..107.1) at local x 90, run M3 SOUTH below the array (an east
# run at arm y would short into the SAMPLE trunk's M3 bottom at local
# x 108.75..112.53!), then stack up onto the M5 GND ("0") spine at
# local y -128 (spine y -131..-125 spans the full DAC width).
VIN_TIE_X = DAC_DX + 90.0                     # 480.0
VIN_ARM_Y = DAC_DY - 8.27                     # 408.60
VIN_TIE_Y = DAC_DY - 128.0                    # 288.87

CMP_APPROACH_Y = 209.25   # DAC_TOP M5 west run to VIN2
# VOUT lanes: VOUT1's pin riser (x 446.6) lies inside VOUT2's horizontal
# span, so VOUT2 hops that crossing on M4; VOUT1 gets an identical-length
# dummy M4 hop so both nets keep the same layer stack and via count
# (pin_contracts section 4 symmetry). VOUT1's lane is the higher one so
# its riser only crosses where VOUT2 is hopped.
VOUT2_LANE_Y = 230.0
VOUT1_LANE_Y = 231.0
VOUT2_HOP_X0, VOUT2_HOP_X1 = 440.0, 452.0   # M4 hop over VOUT1's riser
VOUT1_HOP_X0, VOUT1_HOP_X1 = 420.0, 432.0   # matched dummy hop
VOUT1_DET_X0, VOUT1_DET_X1 = 410.0, 410.8   # length-matching detour
VOUT1_DET_TOP = 244.4
CK_XFER_Y = 262.0         # CK M5 transfer (above SAMPLE's 260 transfer)
SAMPLE_XFER_Y = 260.0


def um(v):
    return int(round(v / DBU))


def box(x0, y0, x1, y1):
    return db.Box(um(min(x0, x1)), um(min(y0, y1)), um(max(x0, x1)), um(max(y0, y1)))


class Router:
    def __init__(self, layout, top):
        self.layout = layout
        self.top = top
        self.net_shapes = {}   # net -> list[(metal_level, Box)]
        self.attach_ok = []    # (metal_level, Box) whitelist vs block shapes

    def li(self, ld):
        return self.layout.layer(*ld)

    def _add(self, net, level, b):
        self.net_shapes.setdefault(net, []).append((level, b))
        self.top.shapes(self.li(METALS[level])).insert(b)

    def wire(self, net, level, x0, y0, x1, y1, w=W):
        hw = w / 2.0
        self._add(net, level, box(x0 - hw, y0 - hw, x1 + hw, y1 + hw)
                  if (x0 <= x1 and y0 <= y1) else
                  box(min(x0, x1) - hw, min(y0, y1) - hw,
                      max(x0, x1) + hw, max(y0, y1) + hw))

    def via(self, net, low, x, y, pad=VIA_PAD):
        """cut + landing pads joining metal `low` and `low+1` at (x, y)."""
        ph = pad / 2.0
        vh = 0.13
        self._add(net, low, box(x - ph, y - ph, x + ph, y + ph))
        self._add(net, low + 1, box(x - ph, y - ph, x + ph, y + ph))
        self.top.shapes(self.li(VIAS[low])).insert(
            box(x - vh, y - vh, x + vh, y + vh))

    def stack(self, net, x, y, lo, hi, pad=VIA_PAD):
        for lvl in range(lo, hi):
            self.via(net, lvl, x, y, pad)

    def allow(self, level, x0, y0, x1, y1):
        self.attach_ok.append((level, box(x0, y0, x1, y1)))

    def label(self, text, x, y, ld=M5LBL):
        self.top.shapes(self.li(ld)).insert(db.Text(text, um(x), um(y)))


def load_block(target, path, topcell=None):
    """Read a block GDS into `target` (dbu-scaled), return its top Cell."""
    src = db.Layout()
    src.read(path)
    stop = src.cell(topcell) if topcell else src.top_cells()[0]
    if len(src.top_cells()) > 1 and topcell is None:
        raise RuntimeError("ambiguous topcell in " + path)
    new = target.create_cell(stop.name)
    new.copy_tree(stop)     # copy_tree scales for differing dbu
    return new


def main():
    layout = db.Layout()
    layout.dbu = DBU
    top = layout.create_cell("adc_top")

    dac = load_block(layout, "/foss/designs/dac/layout/dac_top_floorplan.gds")
    cmp_ = load_block(layout, "/foss/designs/comparator/layout/strongarm.gds")
    sar = load_block(layout, "/foss/designs/sar_logic/layout/sar_folded.gds",
                     "sar_logic")
    glue = load_block(layout, "/foss/designs/adc_top/layout/adc_glue.gds",
                      "adc_glue")

    # dbu-scaling sanity (strongarm.gds is dbu=0.005)
    cb = cmp_.bbox()
    assert abs(cb.width() * DBU - 83.25) < 0.1, "comparator scale bad: %s" % cb
    assert abs(dac.bbox().width() * DBU - 443.0) < 0.1

    places = [
        (dac, db.Trans(db.Vector(um(DAC_DX), um(DAC_DY)))),
        (cmp_, db.Trans(db.Vector(um(CMP_DX), um(CMP_DY)))),
        (sar, db.Trans(2, True, db.Vector(um(SAR_MX), um(SAR_DY)))),
        (glue, db.Trans(db.Vector(um(GLUE_DX), um(GLUE_DY)))),
    ]
    for cell, trans in places:
        top.insert(db.CellInstArray(cell.cell_index(), trans))

    # block shape regions per layer (chip coords) for the checkers
    block_regions = {}
    for name, (cell, trans) in zip(("dac", "cmp", "sar", "glue"), places):
        for lvl, ld in METALS.items():
            it = db.RecursiveShapeIterator(layout, cell, layout.layer(*ld))
            r = db.Region(it)
            r.transform(db.ICplxTrans(trans))
            r.merge()
            block_regions.setdefault(lvl, {})[name] = r

    rt = Router(layout, top)
    build_routes(rt)
    build_taps(rt)
    build_bv_pins(rt)
    build_signal_pins(rt)
    run_checks(rt, block_regions)

    # Project boundary on 0/0 = the full BV slot, not our drawn extent.
    # Inserted BEFORE build_fill so the density fill grid covers the whole
    # slot: density.drc sums drawn + dt-4 fill over the die area, and the
    # empty region above the blocks would otherwise sit at 0% metal.
    drawn = top.bbox()
    assert 0 <= drawn.left * DBU and 0 <= drawn.bottom * DBU \
        and drawn.right * DBU <= SLOT_W and drawn.top * DBU <= SLOT_H, \
        "drawn extent (%.2f,%.2f)..(%.2f,%.2f) exceeds slot BV %gx%g" % (
            drawn.left * DBU, drawn.bottom * DBU,
            drawn.right * DBU, drawn.top * DBU, SLOT_W, SLOT_H)
    top.shapes(layout.layer(0, 0)).insert(
        db.Box(0, 0, um(SLOT_W), um(SLOT_H)))

    build_fill(layout, top)

    b = top.bbox()
    opts = db.SaveLayoutOptions()
    opts.write_context_info = False
    out = "/foss/designs/adc_top/layout/adc_chip_top.gds"
    layout.write(out, opts)
    print("wrote %s topcell=adc_top" % out)
    print("  drawn extent (%.2f,%.2f)..(%.2f,%.2f)" % (
        drawn.left * DBU, drawn.bottom * DBU,
        drawn.right * DBU, drawn.top * DBU))
    print("  0/0 boundary 0,0..%.2f,%.2f   overall bbox %.2f x %.2f" % (
        SLOT_W, SLOT_H, b.width() * DBU, b.height() * DBU))


def build_routes(rt):
    # ---------------- south pads + fan-out ----------------
    for net, px in PIN_PADS.items():
        rt.wire(net, 5, px - PAD_HALF, PAD_Y0, px + PAD_HALF, PAD_Y1, w=0.0)
        # bidirectional pads have separate IN/OUT data paths; the padframe
        # audit wants the layout text to say which one we use (all are outputs)
        # no label here any more: every net now reaches its real BV pin,
        # and a second text on the same net at the wrong coordinates is
        # exactly what the padframe audit reads out of the GDS.
    for net in ("CLK", "RST_N", "EOC", "BIT_0", "BIT_1", "BIT_2", "BIT_3",
                "BIT_4", "BIT_5", "BIT_6", "BIT_7"):
        sx, _sy = SAR_PORT[net]
        jy = JOG_Y[net]
        # M4 stub: SAR bottom (39.77) has the port's fold slot free below
        # its lowest feeder; overlap up to the port label pad
        rt.wire(net, 4, sx, jy, sx, SAR_PORT[net][1], w=W_COL)
        rt.allow(4, sx - 0.3, 39.0, sx + 0.3, 170.5)
        rt.wire(net, 4, sx, jy, PIN_PADS[net], jy)
        rt.via(net, 4, PIN_PADS[net], jy)
        rt.wire(net, 5, PIN_PADS[net], jy, PIN_PADS[net], PAD_Y1 - 1.0)
    # VSS / VDD pad columns (M5) merging pad + jog + supply bands
    rt.wire("VSS", 4, SAR_PORT["VSS"][0], JOG_Y["VSS"],
            SAR_PORT["VSS"][0], SAR_PORT["VSS"][1], w=W_COL)
    rt.allow(4, SAR_PORT["VSS"][0] - 0.3, 39.0, SAR_PORT["VSS"][0] + 0.3, 170.5)
    rt.wire("VSS", 4, SAR_PORT["VSS"][0], JOG_Y["VSS"], PIN_PADS["VSS"], JOG_Y["VSS"])
    rt.via("VSS", 4, PIN_PADS["VSS"], JOG_Y["VSS"])
    rt.wire("VSS", 5, PIN_PADS["VSS"] - 2.5, 4.0, PIN_PADS["VSS"] + 2.5, 32.5, w=0.0)
    rt.wire("VDD", 4, SAR_PORT["VDD"][0], JOG_Y["VDD"],
            SAR_PORT["VDD"][0], SAR_PORT["VDD"][1], w=W_COL)
    rt.allow(4, SAR_PORT["VDD"][0] - 0.3, 39.0, SAR_PORT["VDD"][0] + 0.3, 170.5)
    rt.wire("VDD", 4, SAR_PORT["VDD"][0], JOG_Y["VDD"], PIN_PADS["VDD"], JOG_Y["VDD"])
    rt.via("VDD", 4, PIN_PADS["VDD"], JOG_Y["VDD"])
    rt.wire("VDD", 5, PIN_PADS["VDD"] - 2.5, 0.5, PIN_PADS["VDD"] + 2.5, 33.3, w=0.0)

    # ---------------- supply spines ----------------
    # VSS: south band (below VDD's) -> spine -> DAC GND spine west face
    rt.wire("VSS", 5, VSS_SPINE_X0, 4.0, PIN_PADS["VSS"] + 2.5, 7.0, w=0.0)
    rt.via("VSS", 4, 44.0, 5.5)          # M4 underpass below VDD south band
    rt.wire("VSS", 4, 44.0, 5.5, 44.0, 27.0)
    rt.via("VSS", 4, 44.0, 27.0)
    rt.wire("VSS", 5, VSS_SPINE_X0, VSS_SPINE_Y0, VSS_SPINE_X1, VSS_SPINE_Y1, w=0.0)
    rt.wire("VSS", 5, VSS_SPINE_X1 - 1.0, DAC_GND_Y0, DAC_W_EDGE + 1.0,
            DAC_GND_Y1, w=0.0)
    rt.allow(5, DAC_W_EDGE - 0.1, DAC_GND_Y0 - 0.1, DAC_W_EDGE + 1.1, DAC_GND_Y1 + 0.1)
    # VDD: south band -> spine -> DAC VDD spine west face
    rt.wire("VDD", 5, VDD_SPINE_X0, 0.5, PIN_PADS["VDD"] + 2.5, 3.5, w=0.0)
    rt.wire("VDD", 5, VDD_SPINE_X0, VDD_SPINE_Y0, VDD_SPINE_X1, VDD_SPINE_Y1, w=0.0)
    rt.wire("VDD", 5, VDD_SPINE_X1 - 1.0, DAC_VDD_Y0, DAC_W_EDGE + 1.0,
            DAC_VDD_Y1, w=0.0)
    rt.allow(5, DAC_W_EDGE - 0.1, DAC_VDD_Y0 - 0.1, DAC_W_EDGE + 1.1, DAC_VDD_Y1 + 0.1)
    # band branches (M5) feeding comparator + glue supplies
    # branch reaches x 501 so all 11 COMP-11 tap stacks (350..500) land
    # inside it (an isolated 0.4um M5 via pad violates MT.1/MT.4)
    rt.wire("VSS", 5, VSS_SPINE_X0 + 1.0, VSS_BRANCH_Y, 501.0,
            VSS_BRANCH_Y, w=1.0)
    # VDD branch: M4 underpass below the VSS spine
    rt.wire("VDD", 5, VDD_SPINE_X0 + 1.0, VDD_BRANCH_Y, 40.0, VDD_BRANCH_Y, w=1.0)
    rt.via("VDD", 4, 40.0, VDD_BRANCH_Y)
    rt.wire("VDD", 4, 40.0, VDD_BRANCH_Y, 49.0, VDD_BRANCH_Y)
    rt.via("VDD", 4, 49.0, VDD_BRANCH_Y)
    rt.wire("VDD", 5, 49.0, VDD_BRANCH_Y, CMP_PIN["VDD"][0] + 1.0, VDD_BRANCH_Y,
            w=1.0)

    # comparator supplies (stack down inside verified M1 pads)
    vx, vy = CMP_PIN["VSS"]
    rt.via("VSS", 4, vx, VSS_BRANCH_Y)
    rt.wire("VSS", 4, vx, vy, vx, VSS_BRANCH_Y)
    rt.stack("VSS", vx, vy, 1, 4)
    rt.allow(1, vx - 0.5, vy - 0.5, vx + 0.5, vy + 0.5)
    dx_, dy_ = CMP_PIN["VDD"]
    rt.via("VDD", 4, dx_, VDD_BRANCH_Y)
    rt.wire("VDD", 4, dx_, VDD_BRANCH_Y, dx_, dy_)
    rt.stack("VDD", dx_, dy_, 1, 4)
    rt.allow(1, dx_ - 0.5, dy_ - 0.5, dx_ + 0.5, dy_ + 0.5)

    # glue supplies: M4 risers from the branches to the approach row
    for net, by in (("VDD", VDD_BRANCH_Y), ("VSS", VSS_BRANCH_Y)):
        gx = GLUE_PAD[net][0]
        rt.via(net, 4, gx, by)
        rt.wire(net, 4, gx, by, gx, GLUE_TOP_Y)
        rt.via(net, 3, gx, GLUE_TOP_Y)
        rt.wire(net, 3, gx, GLUE_PAD_Y, gx, GLUE_TOP_Y, w=W3)
        rt.allow(3, gx - 0.3, GLUE_PAD_Y - 0.3, gx + 0.3, GLUE_TOP_Y + 0.3)

    # ---------------- BIT_0..7: SAR -> west bus -> DAC B pins ----------
    for i in range(8):
        net = "BIT_%d" % i
        sx, sy = SAR_PORT[net]
        lane = BAND_LANE[net]
        bx = BUS_X[net]
        px, py = DAC_B_PINS[net]
        dac_lane_y = DAC_DY + py - 1.0
        pin_x = DAC_DX + px
        # north stub through the fold slot (free above the label)
        rt.wire(net, 4, sx, sy, sx, lane, w=W_COL)
        # west to the bus, then north outside the DAC west edge
        rt.wire(net, 4, bx, lane, sx, lane)
        rt.wire(net, 4, bx, lane, bx, dac_lane_y)
        # into the DAC on the probed-free M3 corridor at pin_y - 1.0
        rt.via(net, 3, bx, dac_lane_y)
        rt.wire(net, 3, bx, dac_lane_y, pin_x, dac_lane_y, w=W3)
        rt.wire(net, 3, pin_x, dac_lane_y, pin_x, DAC_DY + py, w=W3)
        rt.allow(3, pin_x - 0.5, dac_lane_y - 0.5, pin_x + 0.5, DAC_DY + py + 0.6)

    # ---------------- CLK / RST_N / CMP_OUT (M5 band lanes) ------------
    for net in ("CLK", "RST_N", "CMP_OUT"):
        sx, sy = SAR_PORT[net]
        if net == "CMP_OUT":   # no south pad; whitelist its fold-slot overlap
            rt.allow(4, sx - 0.3, 39.0, sx + 0.3, 170.5)
        m5x, jogy = COL_XFER[net]
        lane = M5_LANE[net]
        gx = GLUE_PAD[net][0]
        # M4: port stub up to the staggered jog, jog west, via4 to M5
        rt.wire(net, 4, sx, sy, sx, jogy, w=W_COL)
        rt.wire(net, 4, m5x, jogy, sx, jogy, w=W_COL)
        rt.via(net, 4, m5x, jogy)
        # M5: riser (1.5um pitch column) + band lane east to the glue pad
        rt.wire(net, 5, m5x, jogy, m5x, lane)
        rt.wire(net, 5, m5x, lane, gx, lane)
        # glue end: back down to M4 (0.8um pad pitch is fine on M4)
        rt.via(net, 4, gx, lane)
        rt.wire(net, 4, gx, lane, gx, GLUE_TOP_Y, w=W_COL)
        rt.via(net, 3, gx, GLUE_TOP_Y)
        rt.wire(net, 3, gx, GLUE_PAD_Y, gx, GLUE_TOP_Y, w=W3)
        rt.allow(3, gx - 0.3, GLUE_PAD_Y - 0.3, gx + 0.3, GLUE_TOP_Y + 0.3)

    # ---------------- EOC: south pad only (drawn above) ----------------

    # ---------------- CK: glue -> comparator -------------------------
    gx = GLUE_PAD["CK"][0]
    cx, cy = CMP_PIN["CK"]
    rt.wire("CK", 3, gx, GLUE_PAD_Y, gx, GLUE_TOP_Y, w=W3)
    rt.allow(3, gx - 0.3, GLUE_PAD_Y - 0.3, gx + 0.3, GLUE_TOP_Y + 0.3)
    rt.via("CK", 3, gx, GLUE_TOP_Y)
    rt.wire("CK", 4, gx, GLUE_TOP_Y, gx, CK_XFER_Y, w=W_COL)
    rt.via("CK", 4, gx, CK_XFER_Y)
    rt.wire("CK", 5, gx, CK_XFER_Y, cx, CK_XFER_Y)
    rt.via("CK", 4, cx, CK_XFER_Y)
    rt.wire("CK", 4, cx, cy, cx, CK_XFER_Y)
    rt.stack("CK", cx, cy, 1, 4)
    rt.allow(1, cx - 0.6, cy - 0.6, cx + 0.6, cy + 0.6)

    # ---------------- SAMPLE: glue -> DAC east window ------------------
    gx = GLUE_PAD["SAMPLE"][0]
    rt.wire("SAMPLE", 3, gx, GLUE_PAD_Y, gx, GLUE_TOP_Y, w=W3)
    rt.allow(3, gx - 0.3, GLUE_PAD_Y - 0.3, gx + 0.3, GLUE_TOP_Y + 0.3)
    rt.via("SAMPLE", 3, gx, GLUE_TOP_Y)
    rt.via("SAMPLE", 4, gx, GLUE_TOP_Y)
    rt.wire("SAMPLE", 5, gx, GLUE_TOP_Y, gx, SAMPLE_XFER_Y)
    rt.wire("SAMPLE", 5, gx, SAMPLE_XFER_Y, SAMPLE_CH_X, SAMPLE_XFER_Y)
    rt.wire("SAMPLE", 5, SAMPLE_CH_X, SAMPLE_XFER_Y, SAMPLE_CH_X, SAMPLE_WIN_Y)
    rt.via("SAMPLE", 4, SAMPLE_CH_X, SAMPLE_WIN_Y)
    rt.wire("SAMPLE", 4, SAMPLE_DESC_X, SAMPLE_WIN_Y, SAMPLE_CH_X, SAMPLE_WIN_Y)
    rt.wire("SAMPLE", 4, SAMPLE_DESC_X, SAMPLE_TRUNK_Y, SAMPLE_DESC_X, SAMPLE_WIN_Y)
    rt.via("SAMPLE", 3, SAMPLE_DESC_X, SAMPLE_TRUNK_Y)
    rt.allow(3, SAMPLE_DESC_X - 0.3, SAMPLE_TRUNK_Y - 0.3,
             SAMPLE_DESC_X + 0.3, SAMPLE_TRUNK_Y + 0.3)

    # ---------------- DAC_TOP: mesh handoff -> comparator VIN2 --------
    bar_top = DAC_DY + 0.25        # handoff bar (chip y 407.69..417.12)
    rt.wire("DAC_TOP", 5, DACTOP_RISE_X, bar_top - 1.0, DACTOP_RISE_X,
            DACTOP_WIN_Y)
    rt.allow(5, DACTOP_RISE_X - 0.3, bar_top - 1.1, DACTOP_RISE_X + 0.3,
             bar_top + 0.1)
    rt.wire("DAC_TOP", 5, DACTOP_RISE_X, DACTOP_WIN_Y, DACTOP_CH_X, DACTOP_WIN_Y)
    rt.wire("DAC_TOP", 5, DACTOP_CH_X, CMP_APPROACH_Y, DACTOP_CH_X, DACTOP_WIN_Y)
    vx2, vy2 = CMP_PIN["VIN2"]
    rt.wire("DAC_TOP", 5, vx2, CMP_APPROACH_Y, DACTOP_CH_X, CMP_APPROACH_Y)
    rt.wire("DAC_TOP", 5, vx2, vy2, vx2, CMP_APPROACH_Y)
    rt.stack("DAC_TOP", vx2, vy2, 1, 5)
    rt.allow(1, vx2 - 0.6, vy2 - 0.6, vx2 + 0.6, vy2 + 0.6)

    # ---------------- VIN: south pad -> comparator VIN1 ---------------
    vx1, vy1 = CMP_PIN["VIN1"]
    rt.wire("VIN", 5, vx1, PAD_Y1 - 1.0, vx1, 168.0)
    rt.via("VIN", 4, vx1, 168.0)
    rt.wire("VIN", 4, vx1, 168.0, vx1, 181.0)   # M4 underpass below branches
    rt.via("VIN", 4, vx1, 181.0)
    rt.wire("VIN", 5, vx1, 181.0, vx1, vy1)
    rt.stack("VIN", vx1, vy1, 1, 5)
    rt.allow(1, vx1 - 0.6, vy1 - 0.6, vx1 + 0.6, vy1 + 0.6)

    # ---------------- DAC VIN port tie to VSS (south to the GND spine) -
    rt.wire("VSS", 3, VIN_TIE_X, VIN_TIE_Y, VIN_TIE_X, VIN_ARM_Y, w=W3)
    rt.allow(3, VIN_TIE_X - 0.5, VIN_ARM_Y - 0.5,
             VIN_TIE_X + 0.5, VIN_ARM_Y + 0.5)
    rt.stack("VSS", VIN_TIE_X, VIN_TIE_Y, 3, 5)
    rt.allow(5, VIN_TIE_X - 0.3, VIN_TIE_Y - 0.3,
             VIN_TIE_X + 0.3, VIN_TIE_Y + 0.3)

    # ---------------- VOUT1 / VOUT2: comparator -> glue (matched) -----
    for net, lane, det in (("VOUT1", VOUT1_LANE_Y, True),
                           ("VOUT2", VOUT2_LANE_Y, False)):
        cxp, cyp = CMP_PIN[net]
        gxp = GLUE_PAD[net][0]
        rt.stack(net, cxp, cyp, 1, 3)
        rt.allow(1, cxp - 0.7, cyp - 0.7, cxp + 0.7, cyp + 0.7)
        rt.wire(net, 3, cxp, cyp, cxp, lane, w=W3)
        if det:
            # west from pin: [hop_x1..pin] M3, matched dummy M4 hop,
            # [det_x1..hop_x0] M3, detour, [pad..det_x0] M3
            rt.wire(net, 3, VOUT1_HOP_X1, lane, cxp, lane, w=W3)
            rt.via(net, 3, VOUT1_HOP_X1, lane)
            rt.wire(net, 4, VOUT1_HOP_X0, lane, VOUT1_HOP_X1, lane)
            rt.via(net, 3, VOUT1_HOP_X0, lane)
            rt.wire(net, 3, VOUT1_DET_X1, lane, VOUT1_HOP_X0, lane, w=W3)
            rt.wire(net, 3, VOUT1_DET_X1, lane, VOUT1_DET_X1, VOUT1_DET_TOP, w=W3)
            rt.wire(net, 3, VOUT1_DET_X0, VOUT1_DET_TOP, VOUT1_DET_X1,
                    VOUT1_DET_TOP, w=W3)
            rt.wire(net, 3, VOUT1_DET_X0, lane, VOUT1_DET_X0, VOUT1_DET_TOP, w=W3)
            rt.wire(net, 3, gxp, lane, VOUT1_DET_X0, lane, w=W3)
        else:
            # M4 hop over VOUT1's pin riser (x 446.6 in this span)
            rt.wire(net, 3, VOUT2_HOP_X1, lane, cxp, lane, w=W3)
            rt.via(net, 3, VOUT2_HOP_X1, lane)
            rt.wire(net, 4, VOUT2_HOP_X0, lane, VOUT2_HOP_X1, lane)
            rt.via(net, 3, VOUT2_HOP_X0, lane)
            rt.wire(net, 3, gxp, lane, VOUT2_HOP_X0, lane, w=W3)
        rt.wire(net, 3, gxp, GLUE_PAD_Y, gxp, lane, w=W3)
        rt.allow(3, gxp - 0.3, GLUE_PAD_Y - 0.3, gxp + 0.3, lane + 0.3)

    # ---------------- V1.3d patch inside the comparator ----------------
    # strongarm.gds has one via1 (chip 487.83..488.09, 233.59..233.85)
    # whose M1 pad encloses it by only 0.01um on the left and 0.05um
    # below (< the 0.04/0.06 V1.3d thresholds). Its own DRC at dbu=0.005
    # quantized the rule's 2nm corner epsilon to zero and never fired;
    # the chip's dbu=0.001 surfaces it. Widen the pad's left enclosure
    # to 0.04um with a chip-level M1 patch (merges with the pad only --
    # nearest foreign M1 is 1.1um away).
    rt.wire("_patch_v13d", 1, 487.79, 233.54, 488.2, 233.92, w=0.0)
    rt.allow(1, 487.6, 233.4, 488.35, 234.05)


# ----------------------------------------------------------------------
# BV padframe pin interface
# Pin geometry is read from the organizers' authoritative interface file
# rather than transcribed: A13_BV_interface.yaml, 99 pins / 116 rectangles,
# every one Metal2, 1 um deep from the block edge. Coordinates come from
# each rectangle's "translated_user" field, already in our block frame.
BV_IFACE = "/foss/designs/adc_top/padframe_defs/BV/A13_BV_interface.yaml"
M2LBL = (36, 10)

# The west channel x 0..30 is empty on every layer for the full 1110 um
# height (measured against the real GDS), and the north half y>551 is
# empty across the full width. Two vertical M3 buses live in the channel.
# VSS sits WEST of VDD so that a VDD stub crosses only the VSS bus -- M2
# over M3, no short -- and each bus reaches its spine on its own layer.
CH_VSS_X, CH_VDD_X = 20.0, 26.0
CH_BUS_W = 1.0
CH_Y0, CH_Y1 = 4.0, 1106.0
# horizontal tie-off buses under the north pin row (pins at y 1109..1110)
NB_VDD_Y, NB_VSS_Y = 1100.0, 1103.0
NB_X0, NB_X1 = 33.0, 292.0
# where each channel bus ties into the existing M5 supply spines
VDD_TIE_Y, VSS_TIE_Y = 500.0, 200.0
VDD_TIE_X, VSS_TIE_X = 32.0, 44.0

# Tie-off polarity, from gf180mcu_fd_io__tt_025C_3v30.lib (not guessed):
#   bi_t PAD  function ((A)), three_state ((!OE)) -> OE HIGH to drive
#   bi_t Y    function ((IE*PAD))                 -> IE LOW, never read back
#   PU / PD   are the pad's pull resistors        -> LOW on a driven output
# CS/SL/PDRV0/PDRV1 select drive strength and slew. They do NOT gate the
# driver (only OE does), so any tie is functional, but the encoding is in
# neither the PDK liberty nor the spice models. Tied LOW pending the GF
# IO databook -- flagged as an open item, deliberately not invented.
TIEOFF = {"DVSS": "VSS", "DVDD": "VDD",
          "OE": "VDD",
          "IE": "VSS", "PU": "VSS", "PD": "VSS",
          "CS": "VSS", "SL": "VSS", "PDRV0": "VSS", "PDRV1": "VSS"}
# A (pad driver input), Y (pad readback) and ASIG5V (VIN) carry real
# signals; they are routed with their nets, not tied off here.
SIGNAL_TERMS = {"A", "Y", "ASIG5V"}


def build_bv_pins(rt):
    """Place the BV pin rectangles and drive every pad control terminal.

    Mitch, #chipathon-teams 2026-08-29: "You need to drive all the control
    pins to the pads ... be sure to connect them both in the layout and the
    schematic." The padring exposes each control as its own port
    (A13_BV_padring.v), so our block drives them; the padring ties nothing.
    """
    import yaml
    with open(BV_IFACE) as f:
        pins = yaml.safe_load(f)["pins"]

    # vertical channel buses
    for net, bx in (("VSS", CH_VSS_X), ("VDD", CH_VDD_X)):
        rt.wire(net, 3, bx, CH_Y0, bx, CH_Y1, w=CH_BUS_W)

    # channel -> existing M5 spines. VDD leaves east on M3: nothing sits
    # between its bus (x26) and the VDD spine (x30..34).
    rt.wire("VDD", 3, CH_VDD_X, VDD_TIE_Y, VDD_TIE_X, VDD_TIE_Y, w=CH_BUS_W)
    rt.stack("VDD", VDD_TIE_X, VDD_TIE_Y, 3, 5)
    # VSS has to cross the VDD bus AND the VDD M5 spine to reach its own
    # spine at x42..46, so it makes the run on M4, which is free there.
    rt.stack("VSS", CH_VSS_X, VSS_TIE_Y, 3, 4)
    rt.wire("VSS", 4, CH_VSS_X, VSS_TIE_Y, VSS_TIE_X, VSS_TIE_Y, w=CH_BUS_W)
    rt.stack("VSS", VSS_TIE_X, VSS_TIE_Y, 4, 5)

    # horizontal buses under the north pin row, fed from the channel.
    # VDD's feed is a straight M3 run (its bus is the eastern one); VSS
    # again hops to M4 to clear the VDD bus at x26.
    rt.wire("VDD", 3, CH_VDD_X, NB_VDD_Y, NB_X1, NB_VDD_Y, w=CH_BUS_W)
    rt.stack("VSS", CH_VSS_X, NB_VSS_Y, 3, 4)
    rt.wire("VSS", 4, CH_VSS_X, NB_VSS_Y, NB_X0, NB_VSS_Y, w=CH_BUS_W)
    rt.stack("VSS", NB_X0, NB_VSS_Y, 3, 4)
    rt.wire("VSS", 3, NB_X0, NB_VSS_Y, NB_X1, NB_VSS_Y, w=CH_BUS_W)

    placed = {"VDD": 0, "VSS": 0}
    skipped = []
    for p in pins:
        term = p["cell_terminal"]
        name = p["project_pin"]
        if term in SIGNAL_TERMS:
            skipped.append(name)
            continue
        net = TIEOFF[term]
        for r in p["rectangles"]:
            x0, y0, x1, y1 = [v / 200.0 for v in r["translated_user"]]
            cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            # exact rectangles: Router.wire() pads the box by w/2 on BOTH
            # axes, which would push the 10.25 um supply pins to x=-5.12
            # and the north pins past y=1110, outside the slot.
            if x0 < 1.0:                      # west edge pin
                h = y1 - y0
                bx = CH_VSS_X if net == "VSS" else CH_VDD_X
                rt._add(net, 2, box(x0, y0, x1, y1))          # the pin
                rt._add(net, 2, box(x1, cy - h / 2.0,         # stub east
                                    bx + VIA_PAD / 2.0, cy + h / 2.0))
                rt.via(net, 2, bx, cy)
            else:                             # north edge pin
                w = x1 - x0
                by = NB_VSS_Y if net == "VSS" else NB_VDD_Y
                rt._add(net, 2, box(x0, y0, x1, y1))          # the pin
                rt._add(net, 2, box(cx - w / 2.0, by - VIA_PAD / 2.0,
                                    cx + w / 2.0, y0))        # stub south
                rt.via(net, 2, cx, by)
            rt.label(name, cx, cy, ld=M2LBL)
            placed[net] += 1
    print("  BV pins: tied %d to VDD, %d to VSS; %d signal pins deferred"
          % (placed["VDD"], placed["VSS"], len(skipped)))


# ----------------------------------------------------------------------
# Signal pins on the BV interface.
#
# Each signal already exists as a net running from its SAR fold port east
# on M4 at JOG_Y[net] to a south pad. The pins live on the WEST edge, so
# every net simply extends its existing M4 jog westward into the empty
# channel, climbs a private M4 column, and drops to M2 for the last
# micron. The south pads and their fan-out are deliberately left in place:
# same net, so they become harmless stubs and no verified routing moves.
#
# Column x increases with JOG_Y. That is the ordering rule that keeps the
# bottom horizontals short-free: a net's westward jog spans [x_col, sx],
# so it may only cross columns west of it, and those columns belong to
# nets whose verticals start at a LOWER y and are therefore already gone.
# Two orderings have to hold at once, and they force each other:
#   (a) a net's westward lane at wy spans [x_col, sx], so it crosses the
#       columns west of it -> those columns must start ABOVE wy, i.e.
#       x_col increasing => wy increasing;
#   (b) a net descends at its port sx down to wy, crossing the lanes of
#       nets east of it -> those lanes must sit BELOW, i.e. wy decreasing
#       as sx increases.
# JOG_Y and sx both increase CLK -> BIT_7, so (b) pins CLK to the highest
# lane, and (a) then pins CLK to the easternmost column.
SIG_COL_X = {"CLK": 18.0, "RST_N": 16.5, "EOC": 15.0,
             "BIT_0": 13.5, "BIT_1": 12.0, "BIT_2": 10.5, "BIT_3": 9.0,
             "BIT_4": 7.5, "BIT_5": 6.0, "BIT_6": 4.5, "BIT_7": 3.0}
# westward lanes on M4, all below the lowest JOG_Y (23.0) so they pass
# under the existing eastward fan-out instead of through it
SIG_WEST_Y = {"CLK": 22.6, "RST_N": 21.8, "EOC": 21.0,
              "BIT_0": 20.2, "BIT_1": 19.4, "BIT_2": 18.6, "BIT_3": 17.8,
              "BIT_4": 17.0, "BIT_5": 16.2, "BIT_6": 15.4, "BIT_7": 14.6}
# BIT_6/BIT_7 land on the NORTH edge, so they leave their column on M5.
# M5 for the top run (not M4) is what makes this safe: the top horizontals
# would otherwise cross the other net's M4 column.
SIG_TOP_Y = {"BIT_6": 1088.0, "BIT_7": 1090.0}
# A pre-existing VSS M4 underpass sits at x=44, y 5.5..27 -- squarely
# across every westward lane. So a lane stays on M3 until x=30 (clearing
# both that underpass and the M5 supply spines) and only then drops to M4
# for the last stretch, where M4 is what clears the M3 channel buses.
# Keep that M3 detour as SHORT as possible: the BIT nets already carry
# the DAC's M3 entry lanes, and a full-length M3 lane pushes them over
# ANT.5 (they came back at ratio 427..627 on a 1.02 um^2 gate). So the
# lane rides M4 and dips to M3 only for the 2 um that crosses x=44.
UNDERPASS_X0, UNDERPASS_X1 = 43.0, 45.0
CLIMB_SEG = 150.0

# VIN is the analog sampling input and the one long haul: ~1100 um from
# the DAC to N03 on the north edge. It runs west along y=19 on M4 -- below
# every JOG_Y, so it crosses no signal jog -- then climbs a column at
# x=2.0, which is west of every signal column and therefore crosses none
# of them, then east on M5 across the empty north half.
VIN_SOUTH_Y = 12.0
VIN_COL_X = 2.0
VIN_TOP_Y = 1095.0
VIN_BAR_Y = 1105.5
VIN_DROP_X = 267.5


def climb(rt, net, x, ylo, yhi, seg):
    """Climb the channel alternating M5/M4 in `seg`-long chunks.

    A signal column is 200..1000 um. Carried whole on M4 it breaks ANT.5,
    and whole on Metaltop it breaks ANT.7 -- both cap perimeter-area over
    gate-area at 400, and the DAC switch gates on the BIT nets are only
    1.02 um^2. Alternating splits the run so neither layer accumulates
    enough on one net to trip its own rule.
    """
    # Metaltop is the binding rule (ANT.7), so it takes the smallest
    # share: this rotation gives M5 1/5 of the column against 2/5 each
    # for M4 and M3, which are the layers with headroom.
    order = (5, 4, 3, 4, 3)
    widths = {5: 0.5, 4: W_COL, 3: W3}
    y, i = ylo, 0
    while y < yhi - 1e-9:
        lvl = order[i % len(order)]
        y2 = min(y + seg, yhi)
        rt.wire(net, lvl, x, y, x, y2, w=widths[lvl])
        if y2 < yhi - 1e-9:
            nxt = order[(i + 1) % len(order)]
            rt.stack(net, x, y2, min(lvl, nxt), max(lvl, nxt))
            i += 1
        y = y2
    return order[i % len(order)]


def lane_m4(rt, net, x_west, wy, x_east):
    """M4 lane from x_east west to x_west, hopping to M3 across the
    pre-existing VSS M4 underpass at x=44."""
    rt.wire(net, 4, UNDERPASS_X1, wy, x_east, wy, w=W_COL)
    rt.stack(net, UNDERPASS_X1, wy, 3, 4)
    rt.wire(net, 3, UNDERPASS_X0, wy, UNDERPASS_X1, wy, w=W3)
    rt.stack(net, UNDERPASS_X0, wy, 3, 4)
    rt.wire(net, 4, x_west, wy, UNDERPASS_X0, wy, w=W_COL)


def build_signal_pins(rt):
    """Route the 12 signal nets to their BV pins; place the 9 unused
    pad readbacks (Y of each bi_t) as labelled rectangles.

    Y is the pad's output into our block. We drive nothing there and read
    nothing back (IE is tied low), so those pins are placed so the
    interface is geometrically complete but left unconnected on purpose.
    """
    import yaml
    with open(BV_IFACE) as f:
        pins = yaml.safe_load(f)["pins"]
    by_pin = {p["project_pin"]: p for p in pins}

    def rects(name):
        return [[v / 200.0 for v in r["translated_user"]]
                for r in by_pin[name]["rectangles"]]

    # ---- west-edge signals: CLK, RST_N, EOC + BIT_0..BIT_5 outputs ----
    west = [("CLK", "CLK"), ("RST_N", "RST_N"), ("EOC", "EOC_OUT")] + \
           [("BIT_%d" % i, "BIT_%d_OUT" % i) for i in range(6)]
    for net, pin in west:
        cx_col = SIG_COL_X[net]
        jy = JOG_Y[net]
        sx = SAR_PORT[net][0]
        x0, y0, x1, y1 = rects(pin)[0]
        cy, h = (y0 + y1) / 2.0, y1 - y0
        wy = SIG_WEST_Y[net]
        rt.stack(net, sx, jy, 3, 4)
        rt.wire(net, 3, sx, wy, sx, jy, w=W3)                 # descend
        rt.stack(net, sx, wy, 3, 4)
        lane_m4(rt, net, cx_col, wy, sx)                      # lane west
        rt.stack(net, cx_col, wy, 4, 5)
        top_lvl = climb(rt, net, cx_col, wy, cy, CLIMB_SEG)
        rt.stack(net, cx_col, cy, 2, top_lvl)                 # down to M2
        rt._add(net, 2, box(x0, y0, x1, y1))                  # the pin
        rt._add(net, 2, box(x1, cy - h / 2.0,
                            cx_col + VIA_PAD / 2.0, cy + h / 2.0))
        rt.label(pin, (x0 + x1) / 2.0, cy, ld=M2LBL)

    # ---- north-edge signals: BIT_6, BIT_7 ----
    for net in ("BIT_6", "BIT_7"):
        pin = net + "_OUT"
        cx_col, jy = SIG_COL_X[net], JOG_Y[net]
        sx = SAR_PORT[net][0]
        ty = SIG_TOP_Y[net]
        x0, y0, x1, y1 = rects(pin)[0]
        cx, w = (x0 + x1) / 2.0, x1 - x0
        wy = SIG_WEST_Y[net]
        rt.stack(net, sx, jy, 3, 4)
        rt.wire(net, 3, sx, wy, sx, jy, w=W3)
        rt.stack(net, sx, wy, 3, 4)
        lane_m4(rt, net, cx_col, wy, sx)
        rt.stack(net, cx_col, wy, 4, 5)
        top_lvl = climb(rt, net, cx_col, wy, ty, CLIMB_SEG)
        if top_lvl != 5:
            rt.stack(net, cx_col, ty, top_lvl, 5)
        rt.wire(net, 5, cx_col, ty, cx, ty, w=0.5)            # east on M5
        rt.stack(net, cx, ty, 2, 5)
        rt._add(net, 2, box(cx - VIA_PAD / 2.0, ty - VIA_PAD / 2.0,
                            cx + VIA_PAD / 2.0, y0))          # riser
        rt._add(net, 2, box(x0, y0, x1, y1))
        rt.label(pin, cx, (y0 + y1) / 2.0, ld=M2LBL)

    # ---- VIN ----
    px = PIN_PADS["VIN"]
    rt.wire("VIN", 5, px, PAD_Y1, px, VIN_SOUTH_Y, w=0.5)     # pad -> y19
    rt.stack("VIN", px, VIN_SOUTH_Y, 4, 5)
    lane_m4(rt, "VIN", VIN_COL_X, VIN_SOUTH_Y, px)
    rt.stack("VIN", VIN_COL_X, VIN_SOUTH_Y, 4, 5)
    rt.wire("VIN", 5, VIN_COL_X, VIN_SOUTH_Y, VIN_COL_X, VIN_TOP_Y, w=0.5)
    rt.wire("VIN", 5, VIN_COL_X, VIN_TOP_Y, VIN_DROP_X, VIN_TOP_Y, w=0.5)
    rt.stack("VIN", VIN_DROP_X, VIN_TOP_Y, 2, 5)
    rt.wire("VIN", 2, VIN_DROP_X, VIN_TOP_Y, VIN_DROP_X, VIN_BAR_Y, w=0.5)
    vr = sorted(rects("VIN"))
    rt._add("VIN", 2, box(vr[0][0], VIN_BAR_Y - 0.25,         # tie bar
                          vr[-1][2], VIN_BAR_Y + 0.25))
    for x0, y0, x1, y1 in vr:
        rt._add("VIN", 2, box(x0, VIN_BAR_Y, x1, y0))         # riser
        rt._add("VIN", 2, box(x0, y0, x1, y1))
    rt.label("VIN", (vr[0][0] + vr[0][2]) / 2.0,
             (vr[0][1] + vr[0][3]) / 2.0, ld=M2LBL)

    # ---- unused pad readbacks: placed, labelled, intentionally floating ----
    n_idle = 0
    for name in ["EOC_IN"] + ["BIT_%d_IN" % i for i in range(8)]:
        for x0, y0, x1, y1 in rects(name):
            rt.top.shapes(rt.li(METALS[2])).insert(box(x0, y0, x1, y1))
            rt.label(name, (x0 + x1) / 2.0, (y0 + y1) / 2.0, ld=M2LBL)
            n_idle += 1
    print("  BV signal pins: 12 nets routed, %d readback pins placed" % n_idle)


def build_taps(rt):
    """COMP-11: extra substrate taps for latch-up margin. The comparator
    block has only ONE tap; add a row of 11 p-substrate taps under the
    VSS band branch (y 174) spanning the glue + comparator region, each
    a copy of strongarm's own DRC/LVS-proven tap stack (COMP 0.48^2 +
    PPLUS 0.8^2 + CONT 0.22^2 under an M1 pad) with a via1..via4 stack
    up into the M5 VSS branch directly above."""
    layout = rt.layout
    li_comp = layout.layer(22, 0)
    li_pplus = layout.layer(31, 0)
    li_cont = layout.layer(33, 0)
    y = VSS_BRANCH_Y
    for i in range(11):
        x = 350.0 + 15.0 * i
        layout_shapes = [
            (li_comp, box(x - 0.24, y - 0.24, x + 0.24, y + 0.24)),
            (li_pplus, box(x - 0.4, y - 0.4, x + 0.4, y + 0.4)),
            (li_cont, box(x - 0.11, y - 0.11, x + 0.11, y + 0.11)),
        ]
        for li, b in layout_shapes:
            rt.top.shapes(li).insert(b)
        rt.wire("VSS", 1, x, y, x, y, w=0.6)   # M1 pad over the contact
        rt.stack("VSS", x, y, 1, 5)


FILL_SIZE = 3.0
FILL_PITCH = 3.8
FILL_MARGIN = 1.0


def build_fill(layout, top):
    """Chip-level dummy fill on the datatype-4 layers that density.drc
    sums with the drawn layers (COMP 25% / poly 14% / M1..M5+MT 30%
    whole-die minimums; pre-fill the die sits at 0.2-12%). Same-mask
    physical spacing to drawn shapes is kept by a FILL_MARGIN exclusion
    even though the datatype-0 rule deck does not check dt-4 shapes.
    The DAC block bbox is excluded from all METAL fill so the verified
    cap-array parasitics (DAC-9 FS, INT-6/7 transfer) are untouched;
    COMP/poly fill far below the MIM stack is allowed everywhere."""
    b = top.bbox()
    die = db.Region(db.Box(b.left + um(1.0), b.bottom + um(1.0),
                           b.right - um(1.0), b.top - um(1.0)))
    dac_bbox = db.Region(box(DAC_DX - 312.0, DAC_DY - 139.0,
                             DAC_DX + 135.0, DAC_DY + 135.5))

    def reg(l, d):
        r = db.Region(top.begin_shapes_rec(layout.layer(l, d)))
        r.merge()
        return r

    comp, nwell, poly = reg(22, 0), reg(21, 0), reg(30, 0)
    specs = [
        # (dummy layer, obstacles (already sized), extra excl., pitch):
        # M2/M3 lose the whole DAC bbox, so they need a tighter pitch
        # (3.0um squares @ 3.5um = 73% local) to clear the 30% die
        # minimum; the rest use the default 3.8um (62% local)
        ((22, 4), comp.sized(um(1.0)) + nwell.sized(um(2.0))
         + poly.sized(um(1.0)), None, FILL_PITCH),
        ((30, 4), poly.sized(um(1.0)) + comp.sized(um(1.0)), None, FILL_PITCH),
        ((34, 4), reg(34, 0).sized(um(FILL_MARGIN)), None, FILL_PITCH),
        ((36, 4), reg(36, 0).sized(um(FILL_MARGIN)), dac_bbox, 3.5),
        ((42, 4), reg(42, 0).sized(um(FILL_MARGIN)), dac_bbox, 3.5),
        ((46, 4), reg(46, 0).sized(um(FILL_MARGIN)), dac_bbox, FILL_PITCH),
        ((81, 4), reg(81, 0).sized(um(FILL_MARGIN)), dac_bbox, FILL_PITCH),
    ]
    x0 = die.bbox().left * DBU
    y0 = die.bbox().bottom * DBU
    grids = {}
    for pitch in set(s[3] for s in specs):
        base = db.Region()
        for i in range(int((die.bbox().width() * DBU) / pitch)):
            for j in range(int((die.bbox().height() * DBU) / pitch)):
                gx = x0 + i * pitch
                gy = y0 + j * pitch
                base.insert(box(gx, gy, gx + FILL_SIZE, gy + FILL_SIZE))
        grids[pitch] = base
    die_area = float(top.bbox().area())
    for (l, d), obst, extra, pitch in specs:
        avoid = obst
        if extra is not None:
            avoid = avoid + extra
        keep = grids[pitch].outside(avoid) & die
        top.shapes(layout.layer(l, d)).insert(keep)
        tot = reg(l, 0).area() + keep.area()
        print("fill %d/%d: %5d squares, density %.1f%%" % (
            l, d, keep.count(), 100.0 * tot / die_area))


def run_checks(rt, block_regions):
    layout = rt.layout
    fails = []

    # (2) chip routes vs block shapes, same layer, spacing-aware
    allow_by_level = {}
    for lvl, b in rt.attach_ok:
        allow_by_level.setdefault(lvl, db.Region()).insert(b)
    for net, shapes in rt.net_shapes.items():
        for lvl, b in shapes:
            grown = db.Region(b).sized(um(SPACING[lvl] - 0.005))
            for bname, reg in block_regions[lvl].items():
                hit = reg & grown
                if hit.is_empty():
                    continue
                allowed = allow_by_level.get(lvl)
                if allowed is not None:
                    hit = hit - allowed.sized(um(SPACING[lvl]))
                if not hit.is_empty():
                    bb = hit.bbox()
                    fails.append("net %s M%d vs block %s near (%.2f,%.2f)" % (
                        net, lvl, bname, bb.left * DBU, bb.bottom * DBU))

    # (3) cross-net clearance among chip routes
    net_regions = {}
    for net, shapes in rt.net_shapes.items():
        per = {}
        for lvl, b in shapes:
            per.setdefault(lvl, db.Region()).insert(b)
        for r in per.values():
            r.merge()
        net_regions[net] = per
    nets = sorted(net_regions)
    for i, ni in enumerate(nets):
        for nj in nets[i + 1:]:
            for lvl in net_regions[ni]:
                if lvl not in net_regions[nj]:
                    continue
                hit = net_regions[ni][lvl].sized(um(SPACING[lvl] - 0.005)) \
                    & net_regions[nj][lvl]
                if not hit.is_empty():
                    bb = hit.bbox()
                    fails.append("nets %s/%s M%d near (%.2f,%.2f)" % (
                        ni, nj, lvl, bb.left * DBU, bb.bottom * DBU))

    # (1) attach coverage: key attach points must land on block metal
    probes = [
        # the handoff "bar" is an L-shaped 0.5um M5 wire: horizontal strip
        # at local y -0.25..0.25 -- probe ON the strip, not below it
        ("DAC_TOP mesh bar", 5, "dac", DACTOP_RISE_X, DAC_DY),
        ("SAMPLE trunk", 3, "dac", SAMPLE_DESC_X, SAMPLE_TRUNK_Y),
        ("VIN tie GND spine", 5, "dac", VIN_TIE_X, VIN_TIE_Y),
        ("DAC VIN port arm", 3, "dac", VIN_TIE_X, VIN_ARM_Y),
        ("DAC VDD spine", 5, "dac", DAC_W_EDGE + 0.5, (DAC_VDD_Y0 + DAC_VDD_Y1) / 2),
        ("DAC GND spine", 5, "dac", DAC_W_EDGE + 0.5, (DAC_GND_Y0 + DAC_GND_Y1) / 2),
    ]
    for net in ("VIN1", "VIN2", "CK", "VDD", "VSS", "VOUT1", "VOUT2"):
        probes.append(("cmp pin " + net, 1, "cmp", CMP_PIN[net][0], CMP_PIN[net][1]))
    for i in range(8):
        px, py = DAC_B_PINS["BIT_%d" % i]
        probes.append(("B riser %d" % i, 3, "dac", DAC_DX + px, DAC_DY + py))
    for name, lvl, bname, x, y in probes:
        pt = db.Region(box(x - 0.05, y - 0.05, x + 0.05, y + 0.05))
        if (block_regions[lvl][bname] & pt).is_empty():
            fails.append("attach MISS: %s at (%.2f,%.2f) M%d" % (name, x, y, lvl))

    if fails:
        print("CHECK FAILURES (%d):" % len(fails))
        for f in fails[:60]:
            print("  ", f)
        sys.exit(1)
    print("all placement/route checks PASS (%d nets)" % len(rt.net_shapes))


if __name__ == "__main__":
    main()
