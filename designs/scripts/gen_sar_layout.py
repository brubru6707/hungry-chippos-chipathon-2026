#!/usr/bin/env python3
"""
Generate the SAR_LOGIC leaf cells (inv, tg, nand2, nor2) for gf180mcuD
variant=D -- Step 1 of the SAR-4 layout (see sar_logic/sar_designs/*.sch).

Sizes (from the verified schematics, all L=0.28u):
  inv   : PMOS 1u   / NMOS 0.5u
  tg    : PMOS 1u   / NMOS 0.5u   (post tg.sch W/L-swap fix)
  nand2 : PMOS 1u x2 parallel / NMOS 1u x2 series
  nor2  : PMOS 2u x2 series   / NMOS 0.5u x2 parallel

Style: planar cells in the spirit of gen_dac_switch_layout.build_nand2_cell
-- PDK PCell devices (validated geometry), POLY stripes for gate joins, and
M1-only interconnect. Keeping the leaves free of M2/M3 lets the DFF and
top-level assembly route channels on M2 (tracks) + M3 (drops) anywhere,
including directly over leaf cells, without layer conflicts.

Interconnect scheme per cell (all coordinates derived from PCell pad labels
at runtime, NOT hardcoded, so the same builder works across W values):
  - VDD rail above the PMOS row; VSS rail below the NMOS row.
  - One or two M1 "gap tracks" in the PMOS/NMOS inter-row gap carry the
    output and (for the 2-input gates) the series-mid or A/B terminal nets.
    Track spans and drop verticals are chosen so no vertical crosses a
    foreign track (same reasoning as the DAC nand2's y_top/y_bot/mid_y).
  - Gate joins ride POLY (crossing M1 tracks on a different layer); when
    the PMOS and NMOS gate-contact x differ (different W), the stripe jogs
    horizontally on POLY inside the gap.

Reuses gen_dac_switch_layout's environment fixes (HOME/USER + generic-PDK
activation), PCell params, label harvesting, and grid snapping verbatim.
"""

import sys

sys.path.insert(0, "/foss/designs/designs/scripts")

from gen_dac_switch_layout import (  # noqa: E402
    _add_label,
    _add_pcell,
    _fet_params,
    _labels,
    _m1_wire,
    snap_to_grid,
)
import klayout.db as db  # noqa: E402

L_GATE = 0.28
ROW_GAP = 2.2   # PMOS-row-bbox to NMOS-row-bbox spacing: fits two 0.24um M1
                # tracks at 0.7um pitch with >=0.31um (M1.2a) clearance to the
                # row-edge pads (0.75um first-track offset), and exceeds the
                # 1.5um nwell-to-nmos-active margin proven by build_driver_cell
COL_GAP = 0.8   # inter-column bbox gap for the 2-input gates: two same-net
                # VDD-tied nwells 0.8um apart clear NW.2a_LV's 0.6um rule
TRACK0 = 0.75   # first gap track offset below the PMOS row bbox
TRACK_P = 0.7   # gap track pitch
RAIL_OFF = 0.5  # supply rail offset outside the row bbox
POLY_HW = 0.15  # poly stripe half-width (0.30um >= PL.1's 0.28um)


def _poly_wire(top, dbu, x0, y0, x1, y1, li_poly, hw=POLY_HW):
    def um(v):
        return int(round(v / dbu))
    top.shapes(li_poly).insert(
        db.Box(um(min(x0, x1) - hw), um(min(y0, y1) - hw), um(max(x0, x1) + hw), um(max(y0, y1) + hw))
    )


def _probe(kind, params):
    """Standalone-instantiate a PCell to measure its bbox in um."""
    probe_layout = db.Layout()
    probe_layout.dbu = 0.001
    probe_top = probe_layout.create_cell("probe")
    _add_pcell(probe_layout, probe_top, kind, params, db.Trans())
    probe_top.flatten(1)
    b = probe_top.bbox()
    d = probe_layout.dbu
    return (b.left * d, b.bottom * d, b.right * d, b.top * d)


def _gate_join(top, dbu, li_poly, pg, ng, jog_y):
    """POLY stripe joining a PMOS gate pad to the NMOS gate pad below it,
    jogging horizontally at jog_y (inside the row gap) if the two gate
    contacts sit at different x (different device widths shift the pad).

    The stripe spans exactly pad-center to pad-center: the PCell's own
    contact-pad poly (with its enclosure margin) already reaches the gate,
    and extending past the pad toward the device clips the active edge,
    producing 0.01um min-channel-width slivers (DF.2a_LV).

    Stripe half-width is 0.13 (0.26um), deliberately NARROWER than the
    0.28um gate poly: the NMOS gate pad sits on the far side of its row, so
    the descending stripe runs along the full channel at the gate x -- a
    stripe wider than the gate would widen the poly-over-active union and
    extract as a longer L (seen as L=0.3u with the 0.30um stripe). 0.26um
    stays inside the gate footprint (>=0.01um margin at 0.005 grid snap)
    and above the poly interconnect minimum width."""
    hw = 0.13
    if abs(pg[0] - ng[0]) < 0.01:
        _poly_wire(top, dbu, pg[0], ng[1], pg[0], pg[1], li_poly, hw=hw)
    else:
        _poly_wire(top, dbu, pg[0], jog_y, pg[0], pg[1], li_poly, hw=hw)
        _poly_wire(top, dbu, pg[0], jog_y, ng[0], jog_y, li_poly, hw=hw)
        _poly_wire(top, dbu, ng[0], ng[1], ng[0], jog_y, li_poly, hw=hw)


def _rails(top, dbu, li_m1, li_m1lbl, p_pads, n_pads, pmax, nmin, vdd="VDD", vss="VSS"):
    """VDD rail above the PMOS row / VSS rail below the NMOS row, with a
    vertical from every listed pad."""
    vdd_y = pmax + RAIL_OFF
    vss_y = nmin - RAIL_OFF
    xs = [p[0] for p in p_pads]
    _m1_wire(top, dbu, min(xs), vdd_y, max(xs), vdd_y, li_m1)
    for (x, y) in p_pads:
        _m1_wire(top, dbu, x, y, x, vdd_y, li_m1)
    _add_label(top, dbu, min(xs), vdd_y, vdd, li_m1lbl)
    xs = [p[0] for p in n_pads]
    _m1_wire(top, dbu, min(xs), vss_y, max(xs), vss_y, li_m1)
    for (x, y) in n_pads:
        _m1_wire(top, dbu, x, y, x, vss_y, li_m1)
    _add_label(top, dbu, min(xs), vss_y, vss, li_m1lbl)


def _track(top, dbu, li_m1, li_m1lbl, track_y, drops, label=None):
    """One horizontal M1 gap track plus a vertical drop from each pad."""
    xs = [p[0] for p in drops]
    _m1_wire(top, dbu, min(xs), track_y, max(xs), track_y, li_m1)
    for (x, y) in drops:
        _m1_wire(top, dbu, x, y, x, track_y, li_m1)
    if label:
        _add_label(top, dbu, min(xs), track_y, label, li_m1lbl)


def _place_rows(layout, top, p_specs, n_specs):
    """Place PMOS columns (y=0) and NMOS columns (below, ROW_GAP clear).
    p_specs/n_specs: list of _fet_params dicts, one per column, left to
    right with COL_GAP bbox spacing. Returns (pmax, pmin, nmax, nmin) row
    bbox y-extents in um."""
    dbu = layout.dbu
    x = 0.0
    p_extent = [0.0, 0.0]
    for i, params in enumerate(p_specs):
        bb = _probe("pfet", params)
        _add_pcell(layout, top, "pfet", params, db.Trans(db.Vector(int(round(x / dbu)), 0)))
        if i == 0:
            p_extent[0] = bb[1]
        p_extent[1] = max(p_extent[1], bb[3])
        x += (bb[2] - bb[0]) + COL_GAP
    top.flatten(1)
    pmin, pmax = p_extent[0], p_extent[1]

    x = 0.0
    nmin = None
    nmax = None
    for params in n_specs:
        bb = _probe("nfet", params)
        y = pmin - ROW_GAP - bb[3]
        _add_pcell(layout, top, "nfet", params, db.Trans(db.Vector(int(round(x / dbu)), int(round(y / dbu)))))
        nmin = (y + bb[1]) if nmin is None else min(nmin, y + bb[1])
        nmax = (y + bb[3]) if nmax is None else max(nmax, y + bb[3])
        x += (bb[2] - bb[0]) + COL_GAP
    top.flatten(1)
    return pmax, pmin, nmax, nmin


def build_inv(layout, cell_name="inv", pfet_w=1.0, nfet_w=0.5):
    """inv.sch: XM1 vout vin VDD VDD pfet 1u; XM2 vout vin VSS VSS nfet 0.5u."""
    top = layout.create_cell(cell_name)
    dbu = layout.dbu
    li_poly, li_m1, li_m1lbl = layout.layer(30, 0), layout.layer(34, 0), layout.layer(34, 10)
    pp = _fet_params(pfet_w, L_GATE, ["ps", "pd"], ["pg"], "pvdd")
    np_ = _fet_params(nfet_w, L_GATE, ["ns", "nd"], ["ng"], "ngnd")
    pmax, pmin, nmax, nmin = _place_rows(layout, top, [pp], [np_])
    p, n = _labels(top, li_m1lbl, "p"), _labels(top, li_m1lbl, "n")

    _rails(top, dbu, li_m1, li_m1lbl, [p["ps"], p["pvdd"]], [n["ns"], n["ngnd"]], pmax, nmin)
    out_y = pmin - TRACK0
    _track(top, dbu, li_m1, li_m1lbl, out_y, [p["pd"], n["nd"]], "vout")
    _gate_join(top, dbu, li_poly, p["pg"], n["ng"], jog_y=pmin - TRACK0 - TRACK_P)
    _add_label(top, dbu, p["pg"][0], p["pg"][1], "vin", li_m1lbl)
    snap_to_grid(top)
    return top


def build_tg(layout, cell_name="tg", pfet_w=1.0, nfet_w=0.5):
    """tg.sch: XM1 A CTRL_B B VDD pfet 1u; XM2 A CTRL B VSS nfet 0.5u.
    Gates deliberately NOT joined (complementary clocks)."""
    top = layout.create_cell(cell_name)
    dbu = layout.dbu
    li_m1, li_m1lbl = layout.layer(34, 0), layout.layer(34, 10)
    pp = _fet_params(pfet_w, L_GATE, ["ps", "pd"], ["pg"], "pvdd")
    np_ = _fet_params(nfet_w, L_GATE, ["ns", "nd"], ["ng"], "ngnd")
    pmax, pmin, nmax, nmin = _place_rows(layout, top, [pp], [np_])
    p, n = _labels(top, li_m1lbl, "p"), _labels(top, li_m1lbl, "n")

    # Only the well/substrate taps go to the rails (A/B are signal terminals).
    _rails(top, dbu, li_m1, li_m1lbl, [p["pvdd"]], [n["ngnd"]], pmax, nmin)
    a_y = pmin - TRACK0            # upper gap track: A = both drains
    b_y = a_y - TRACK_P            # lower gap track: B = both sources
    # a-track spans the drain-side (right) pads; b's source-side (left) pads
    # sit outside that span, so b's verticals never cross the a track.
    _track(top, dbu, li_m1, li_m1lbl, a_y, [p["pd"], n["nd"]], "A")
    _track(top, dbu, li_m1, li_m1lbl, b_y, [p["ps"], n["ns"]], "B")
    _add_label(top, dbu, p["pg"][0], p["pg"][1], "CTRL_B", li_m1lbl)
    _add_label(top, dbu, n["ng"][0], n["ng"][1], "CTRL", li_m1lbl)
    snap_to_grid(top)
    return top


def build_nand2(layout, cell_name="nand2", pfet_w=1.0, nfet_w=1.0):
    """nand2.sch: parallel PMOS (XM1/XM2, sources=VDD, drains=Z, gates A/B),
    series NMOS Z -[A]- net1 -[B]- VSS."""
    top = layout.create_cell(cell_name)
    dbu = layout.dbu
    li_poly, li_m1, li_m1lbl = layout.layer(30, 0), layout.layer(34, 0), layout.layer(34, 10)
    pa = _fet_params(pfet_w, L_GATE, ["ps_a", "pd_a"], ["pg_a"], "pvdd_a")
    pb = _fet_params(pfet_w, L_GATE, ["ps_b", "pd_b"], ["pg_b"], "pvdd_b")
    na = _fet_params(nfet_w, L_GATE, ["ns_a", "nd_a"], ["ng_a"], "ngnd_a")
    nb = _fet_params(nfet_w, L_GATE, ["ns_b", "nd_b"], ["ng_b"], "ngnd_b")
    pmax, pmin, nmax, nmin = _place_rows(layout, top, [pa, pb], [na, nb])
    p, n = _labels(top, li_m1lbl, "p"), _labels(top, li_m1lbl, "n")

    _rails(
        top, dbu, li_m1, li_m1lbl,
        [p["ps_a"], p["pvdd_a"], p["ps_b"], p["pvdd_b"]],
        [n["nd_b"], n["ngnd_a"], n["ngnd_b"]],
        pmax, nmin,
    )
    # Series NMOS assignment: Z on col A's left diffusion (ns_a), mid on the
    # two adjacent inner diffusions (nd_a <-> ns_b), VSS on col B's right
    # diffusion (nd_b, wired in _rails above). MOS D/S symmetry makes the
    # left/right choice free; adjacency keeps the mid track narrow.
    z_y = pmin - TRACK0            # upper track: Z = pd_a + pd_b + ns_a
    mid_y = z_y - TRACK_P          # lower track: net1 = nd_a + ns_b
    # ns_a's vertical to z_y passes mid_y's height, but the mid track spans
    # only [nd_a.x, ns_b.x] and ns_a.x < nd_a.x -- no crossing. pd_b's drop
    # to z_y stops above mid_y. (Same-reasoning as the DAC nand2 channel.)
    _track(top, dbu, li_m1, li_m1lbl, z_y, [p["pd_a"], p["pd_b"], n["ns_a"]], "Z")
    _track(top, dbu, li_m1, li_m1lbl, mid_y, [n["nd_a"], n["ns_b"]])
    jog = z_y - 2 * TRACK_P
    _gate_join(top, dbu, li_poly, p["pg_a"], n["ng_a"], jog_y=jog)
    _gate_join(top, dbu, li_poly, p["pg_b"], n["ng_b"], jog_y=jog)
    _add_label(top, dbu, p["pg_a"][0], p["pg_a"][1], "A", li_m1lbl)
    _add_label(top, dbu, p["pg_b"][0], p["pg_b"][1], "B", li_m1lbl)
    snap_to_grid(top)
    return top


def build_nor2(layout, cell_name="nor2", pfet_w=2.0, nfet_w=0.5):
    """nor2.sch: series PMOS VDD -[A]- net1 -[B]- Z (XM2 then XM1),
    parallel NMOS (XM3/XM4, drains=Z, sources=VSS, gates A/B)."""
    top = layout.create_cell(cell_name)
    dbu = layout.dbu
    li_poly, li_m1, li_m1lbl = layout.layer(30, 0), layout.layer(34, 0), layout.layer(34, 10)
    pa = _fet_params(pfet_w, L_GATE, ["ps_a", "pd_a"], ["pg_a"], "pvdd_a")
    pb = _fet_params(pfet_w, L_GATE, ["ps_b", "pd_b"], ["pg_b"], "pvdd_b")
    na = _fet_params(nfet_w, L_GATE, ["ns_a", "nd_a"], ["ng_a"], "ngnd_a")
    nb = _fet_params(nfet_w, L_GATE, ["ns_b", "nd_b"], ["ng_b"], "ngnd_b")
    pmax, pmin, nmax, nmin = _place_rows(layout, top, [pa, pb], [na, nb])
    p, n = _labels(top, li_m1lbl, "p"), _labels(top, li_m1lbl, "n")

    _rails(
        top, dbu, li_m1, li_m1lbl,
        [p["ps_a"], p["pvdd_a"], p["pvdd_b"]],
        [n["ns_a"], n["ngnd_a"], n["ns_b"], n["ngnd_b"]],
        pmax, nmin,
    )
    # net1 (series mid): the adjacent inner PMOS diffusions, narrow upper
    # track. Z: col B's outer PMOS drain + both NMOS drains, lower track --
    # pd_b's drop passes net1_y's height but net1's span [pd_a.x, ps_b.x]
    # ends left of pd_b.x; the NMOS drain drops stop below net1_y.
    net1_y = pmin - TRACK0
    z_y = net1_y - TRACK_P
    _track(top, dbu, li_m1, li_m1lbl, net1_y, [p["pd_a"], p["ps_b"]])
    _track(top, dbu, li_m1, li_m1lbl, z_y, [p["pd_b"], n["nd_a"], n["nd_b"]], "Z")
    jog = z_y - TRACK_P
    _gate_join(top, dbu, li_poly, p["pg_a"], n["ng_a"], jog_y=jog)
    _gate_join(top, dbu, li_poly, p["pg_b"], n["ng_b"], jog_y=jog)
    _add_label(top, dbu, p["pg_a"][0], p["pg_a"][1], "A", li_m1lbl)
    _add_label(top, dbu, p["pg_b"][0], p["pg_b"][1], "B", li_m1lbl)
    snap_to_grid(top)
    return top


def main():
    layout = db.Layout()
    layout.dbu = 0.001
    cells = {
        "inv": build_inv(layout),
        "tg": build_tg(layout),
        "nand2": build_nand2(layout),
        "nor2": build_nor2(layout),
    }
    build_dff(layout, cells, "set")
    build_dff(layout, cells, "rst")
    options = db.SaveLayoutOptions()
    options.write_context_info = False
    layout.write("/foss/designs/sar_logic/layout/sar_cells.gds", options)
    print("wrote sar_logic/layout/sar_cells.gds with topcells:", [c.name for c in layout.each_cell()])




# ======================================================================
# Step 2: DFF assembly -- leaf cells in a row + M2-track/M3-drop channel
# ======================================================================

from gen_dac_switch_layout import (  # noqa: E402
    _m2_wire,
    _m3_wire,
    _via2_hop,
    _via_transition,
)

PIN_NAMES = {
    "inv": ("VDD", "VSS", "vin", "vout"),
    "tg": ("VDD", "VSS", "A", "B", "CTRL", "CTRL_B"),
    "nand2": ("VDD", "VSS", "A", "B", "Z"),
    "nor2": ("VDD", "VSS", "A", "B", "Z"),
}
CELL_GAP = 1.2    # leaf-bbox gap in the row (also > NW.2a's 0.6um same-potential nwell rule)
TRACK_PITCH = 0.65  # M2 track pitch: 0.195 (landing-pad hw) + 0.16 (wire hw)
                    # + 0.28 (M2.2a) = 0.635 -- a drop's track-landing pad
                    # must clear the NEIGHBORING track's wire, not just
                    # wire-to-wire (which 0.6 would satisfy)
DROP_PITCH = 0.8   # min x pitch between M3 drop verticals

# Pins that sit on a leaf device's native gate-contact pad. The native pad is
# only ~0.26um wide with S/D contact-column M1 ~0.44um away on BOTH sides, so
# the standard 0.46um _via_transition landing violates M1.2a (0.31um) there.
# V1.3a needs zero M1 overlap of via1, and V1.3c's end-of-line overlap only
# applies along the narrow direction's ends -- so a 0.26um-wide by 0.60um-tall
# landing (matching the native pad width, extending along the gate) is legal
# on both counts while keeping exactly 0.31um to the neighbors.
GATE_PINS = {
    ("inv", "vin"), ("tg", "CTRL"), ("tg", "CTRL_B"),
    ("nand2", "A"), ("nand2", "B"), ("nor2", "A"), ("nor2", "B"),
}


def _cell_pins(cell, names):
    """Pin-label positions (um) of `cell`, filtered to `names`."""
    layout = cell.layout()
    li = layout.layer(34, 10)
    dbu = layout.dbu
    out = {}
    for shp in cell.shapes(li).each():
        if shp.is_text() and shp.text.string in names:
            out[shp.text.string] = (shp.text.x * dbu, shp.text.y * dbu)
    return out


def _place_row(layout, top, cells, insts):
    """Place leaf instances left-to-right, bbox tops aligned at y=0.
    insts: list of (inst_name, cell_name, {leaf_pin: net}).
    Returns (pin_list, row_right): pin_list = [(net, x, y), ...]."""
    dbu = layout.dbu
    x_cursor = 0.0
    pin_list = []
    supply_pins = {}
    for _iname, cname, pinmap in insts:
        cell = cells[cname]
        bb = cell.bbox()
        x_off = x_cursor - bb.left * dbu
        y_off = -bb.top * dbu
        top.insert(db.CellInstArray(
            cell.cell_index(),
            db.Trans(db.Vector(int(round(x_off / dbu)), int(round(y_off / dbu)))),
        ))
        pins = _cell_pins(cell, PIN_NAMES[cname])
        for leaf_pin, net in pinmap.items():
            px, py = pins[leaf_pin]
            if net in ("VDD", "VSS"):
                # supplies ride M1 straps, not channel tracks (congestion +
                # power integrity) -- see build_dff
                supply_pins.setdefault(net, []).append((px + x_off, py + y_off))
                continue
            kind = "gate" if (cname, leaf_pin) in GATE_PINS else "pad"
            pin_list.append((net, px + x_off, py + y_off, kind))
        x_cursor += bb.width() * dbu + CELL_GAP
    return pin_list, supply_pins, x_cursor - CELL_GAP


def channel_route(layout, top, pin_list, exports, y_ch0):
    """Connect every pin of each net through one M2 track per net in the
    channel above the row (y >= y_ch0), reaching pins with M3 verticals.

    Constraint model (why this is correct by construction): leaf cells are
    poly+M1 only, so M2/M3 may run anywhere over them. The only conflicts
    possible are M2-track vs M2-track (avoided: one exclusive track y per
    net) and M3-drop vs M3-drop (avoided: >= DROP_PITCH x spacing via the
    greedy assignment below). M3 verticals crossing foreign M2 tracks are
    different layers. Each drop is: pin M1 pad -> via1/M2 -> short same-y
    M2 jog to its assigned drop x -> via2/M3 -> vertical to its net's
    track y -> via2/M2 landing merged with the track.

    exports: [(net, port_name), ...] -> M3 stubs from the net track up to
    a pad row at the channel top, labeled for the next hierarchy level.
    Returns y_top of the export pad row."""
    dbu = layout.dbu
    li_m1 = layout.layer(34, 0)
    li_m1lbl = layout.layer(34, 10)
    li_v1 = layout.layer(35, 0)
    li_m2 = layout.layer(36, 0)
    li_v2 = layout.layer(38, 0)
    li_m3 = layout.layer(42, 0)

    def um(v):
        return int(round(v / dbu))

    def m2_pad(x, y, hw=0.195):
        top.shapes(li_m2).insert(db.Box(um(x - hw), um(y - hw), um(x + hw), um(y + hw)))

    nets = []
    for net, _x, _y, _k in pin_list:
        if net not in nets:
            nets.append(net)
    track_y = {net: y_ch0 + i * TRACK_PITCH for i, net in enumerate(nets)}
    y_top = y_ch0 + len(nets) * TRACK_PITCH + 0.6

    # greedy left-to-right drop-x assignment at >= DROP_PITCH
    order = sorted(range(len(pin_list)), key=lambda i: (pin_list[i][1], pin_list[i][2]))
    drop_x = {}
    cursor = None
    for i in order:
        x = pin_list[i][1]
        cursor = x if cursor is None else max(x, cursor + DROP_PITCH)
        drop_x[i] = cursor

    span = {net: [None, None] for net in nets}
    for i, (net, px, py, kind) in enumerate(pin_list):
        dx = drop_x[i]
        if kind == "gate":
            # skinny-tall M1 landing on the native gate pad (see GATE_PINS)
            top.shapes(li_m1).insert(db.Box(um(px - 0.13), um(py - 0.30), um(px + 0.13), um(py + 0.30)))
            top.shapes(li_v1).insert(db.Box(um(px - 0.13), um(py - 0.13), um(px + 0.13), um(py + 0.13)))
            m2_pad(px, py)
        else:
            _via_transition(top, dbu, px, py, li_m1, li_v1, li_m2)
        if abs(dx - px) > 0.005:
            _m2_wire(top, dbu, px, py, dx, py, li_m2)
            m2_pad(dx, py)  # V2.3c/d: via2 needs a full pad, not the 0.32um wire end
        _via2_hop(top, dbu, dx, py, li_v2, li_m3)
        ty = track_y[net]
        _m3_wire(top, dbu, dx, py, dx, ty, li_m3)
        m2_pad(dx, ty)      # V2.3c/d: landing pad where the vertical meets the track
        _via2_hop(top, dbu, dx, ty, li_v2, li_m3)
        s = span[net]
        s[0] = dx if s[0] is None else min(s[0], dx)
        s[1] = dx if s[1] is None else max(s[1], dx)

    # export stubs get their own x slots right of all drops
    ex_x0 = (max(d for d in drop_x.values()) if drop_x else 0.0) + 1.0
    for k, (net, port) in enumerate(exports):
        ex = ex_x0 + k * DROP_PITCH
        ty = track_y[net]
        m2_pad(ex, ty)
        _via2_hop(top, dbu, ex, ty, li_v2, li_m3)
        _m3_wire(top, dbu, ex, ty, ex, y_top, li_m3)
        top.shapes(li_m3).insert(db.Box(
            int(round((ex - 0.195) / dbu)), int(round((y_top - 0.195) / dbu)),
            int(round((ex + 0.195) / dbu)), int(round((y_top + 0.195) / dbu)),
        ))
        _add_label(top, dbu, ex, y_top, port, li_m1lbl)
        s = span[net]
        s[0] = ex if s[0] is None else min(s[0], ex)
        s[1] = ex if s[1] is None else max(s[1], ex)

    for net in nets:
        s = span[net]
        ty = track_y[net]
        _m2_wire(top, dbu, s[0], ty, s[1], ty, li_m2)
        # via2/M2 landings along the track already exist at each drop x
    return y_top, ex_x0 + len(exports) * DROP_PITCH


DFF_SET_INSTS = [
    ("x10", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "CLK", "vout": "net7"}),
    ("x11", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "RST_N", "vout": "net8"}),
    ("x2", "tg", {"VDD": "VDD", "VSS": "VSS", "CTRL": "net7", "CTRL_B": "CLK", "A": "D", "B": "net3"}),
    ("x5", "nor2", {"VDD": "VDD", "VSS": "VSS", "A": "net3", "B": "net8", "Z": "net1"}),
    ("x7", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "net1", "vout": "net2"}),
    ("x1", "tg", {"VDD": "VDD", "VSS": "VSS", "CTRL": "CLK", "CTRL_B": "net7", "A": "net2", "B": "net3"}),
    ("x3", "tg", {"VDD": "VDD", "VSS": "VSS", "CTRL": "CLK", "CTRL_B": "net7", "A": "net2", "B": "net6"}),
    ("x6", "nor2", {"VDD": "VDD", "VSS": "VSS", "A": "net6", "B": "net8", "Z": "net4"}),
    ("x9", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "net4", "vout": "net5"}),
    ("x4", "tg", {"VDD": "VDD", "VSS": "VSS", "CTRL": "net7", "CTRL_B": "CLK", "A": "net5", "B": "net6"}),
    ("x8", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "net4", "vout": "Q"}),
]

DFF_RST_INSTS = [
    ("x10", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "CLK", "vout": "net7"}),
    ("x2", "tg", {"VDD": "VDD", "VSS": "VSS", "CTRL": "net7", "CTRL_B": "CLK", "A": "D", "B": "net1"}),
    ("x5", "nand2", {"VDD": "VDD", "VSS": "VSS", "A": "net1", "B": "RST_N", "Z": "net3"}),
    ("x7", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "net3", "vout": "net4"}),
    ("x1", "tg", {"VDD": "VDD", "VSS": "VSS", "CTRL": "CLK", "CTRL_B": "net7", "A": "net4", "B": "net1"}),
    ("x3", "tg", {"VDD": "VDD", "VSS": "VSS", "CTRL": "CLK", "CTRL_B": "net7", "A": "net4", "B": "net2"}),
    ("x6", "nand2", {"VDD": "VDD", "VSS": "VSS", "A": "net2", "B": "RST_N", "Z": "net5"}),
    ("x9", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "net5", "vout": "net6"}),
    ("x4", "tg", {"VDD": "VDD", "VSS": "VSS", "CTRL": "net7", "CTRL_B": "CLK", "A": "net6", "B": "net2"}),
    ("x8", "inv", {"VDD": "VDD", "VSS": "VSS", "vin": "net5", "vout": "Q"}),
]

DFF_PORTS = [("CLK", "CLK"), ("D", "D"), ("Q", "Q"), ("RST_N", "RST_N")]


def _supply_straps(layout, top, supply_pins, y_top, ex_x0):
    """M1 supply straps + M3 export stubs. All leaf cells are top-aligned,
    so every VDD rail label sits at the same y -- one strap through them
    merges the rails. VSS rails differ in depth per cell type (different
    device widths), so each gets a stub down to a common bottom strap.
    Returns nothing; exports land at the strap's right end."""
    dbu = layout.dbu
    li_m1 = layout.layer(34, 0)
    li_m1lbl = layout.layer(34, 10)
    li_v1 = layout.layer(35, 0)
    li_m2 = layout.layer(36, 0)
    li_v2 = layout.layer(38, 0)
    li_m3 = layout.layer(42, 0)

    def um(v):
        return int(round(v / dbu))

    vdd = supply_pins["VDD"]
    vss = supply_pins["VSS"]
    vdd_y = vdd[0][1]
    vss_y = min(y for _x, y in vss) - 0.6
    ex_vdd = max(ex_x0, max(x for x, _y in vdd + vss) + 2.0)
    ex_vss = ex_vdd + DROP_PITCH
    _m1_wire(top, dbu, min(x for x, _y in vdd), vdd_y, ex_vdd, vdd_y, li_m1)
    for x, y in vss:
        _m1_wire(top, dbu, x, y, x, vss_y, li_m1)
    _m1_wire(top, dbu, min(x for x, _y in vss), vss_y, ex_vss, vss_y, li_m1)
    for port, sx, sy in (("VDD", ex_vdd, vdd_y), ("VSS", ex_vss, vss_y)):
        _via_transition(top, dbu, sx, sy, li_m1, li_v1, li_m2)
        _via2_hop(top, dbu, sx, sy, li_v2, li_m3)
        _m3_wire(top, dbu, sx, sy, sx, y_top, li_m3)
        top.shapes(li_m3).insert(db.Box(
            um(sx - 0.195), um(y_top - 0.195), um(sx + 0.195), um(y_top + 0.195)))
        _add_label(top, dbu, sx, y_top, port, li_m1lbl)


def build_dff(layout, cells, variant):
    name = "dff_set_n" if variant == "set" else "dff_rst_n"
    insts = DFF_SET_INSTS if variant == "set" else DFF_RST_INSTS
    top = layout.create_cell(name)
    pin_list, supply_pins, _right = _place_row(layout, top, cells, insts)
    y_top, ex_next = channel_route(layout, top, pin_list, DFF_PORTS, y_ch0=1.0)
    _supply_straps(layout, top, supply_pins, y_top, ex_next)
    snap_to_grid(top)
    return top


if __name__ == "__main__":
    main()
