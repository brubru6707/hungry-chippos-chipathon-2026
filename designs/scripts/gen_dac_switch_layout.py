#!/usr/bin/env python3
"""
Generate the DAC bottom-plate CMOS rail driver cell (unit_switch, VREF=VDD
rework -- see dac/schematic/unit_switch.sch) for gf180mcuD variant=D
(5LM, mim_option=B, metal_top=11K).

Topology (matches unit_switch.sch exactly): a single CMOS inverter --
PMOS pull-up (source=VDD, drain=VOUT, gate=bN_bar, bulk/nwell-tap=VDD),
NMOS pull-down (source=GND, drain=VOUT, gate=bN_bar, bulk/psub-tap=GND).
L=0.28u for both devices in every bit. Per-bit W (from cap_array.sch's
unit_switch instantiations x_sw0..x_sw7):
  bit0: nfet_wid=0.42u  pfet_wid=0.84u
  bit7 (MSB): nfet_wid=53.76u  pfet_wid=53.76u pfet_m=2 (two parallel
    53.76u PMOS devices -- gf180mcuD's binned nfet_03v3/pfet_03v3 models
    cap out at W<=100.001u regardless of nf, so the 107.52u MSB PMOS is
    split m=2 rather than drawn as one W=107.52u or one nf=2 device; see
    dac/schematic/unit_switch.sch's header comment).

This checkpoint script builds bit0 (smallest driver, proves the base
topology) and bit7 (proves the m=2 parallel-device construction) as two
separate topcells in one GDS. The other 6 bit sizes reuse the identical
generator function (build_driver_cell) and are deferred to a follow-up
pass per the Step-1 checkpoint scope.

Device generation uses the PDK's own gf180mcu KLayout PCell library
(pymacros/cells/fet.py -> draw_fet.py), NOT hand-drawn polygons -- this
reuses the PDK's validated device geometry/DRC-rule constants directly
rather than re-deriving them. Two environment fixes were required to make
this PCell path usable headlessly in the iic-osic-tools container (both
undocumented failures, not code bugs to route around at the geometry
level):
  1. `docker exec` does not set $HOME/$USER, so gdsfactory's internal
     getpass.getuser() call crashes on uid 1000 (no /etc/passwd entry).
     Fix: pass HOME=/headless USER=headless to the exec environment.
  2. Even with (1) fixed, every gdsfactory PCell call (even a bare
     rectangle) fails with "No active PDK" -- gdsfactory v9.40 requires
     an active PDK context that the vendored gf180mcu pymacros code
     (written for gdsfactory v7, patched via cells/_patches.py mixins for
     v9 compatibility) never activates, and no gf180mcu-specific
     gdsfactory PDK package is installed to activate instead. Fix:
     `gf.gpdk.PDK.activate()` (the *generic* gdsfactory PDK) before any
     PCell call. This is safe here because draw_fet.py addresses layers
     by explicit (layer, datatype) tuples from layers_def.py, not by
     symbolic PDK layer names, so the generic PDK's own layer map is
     never consulted.
This is exactly why dac/../gen_dac_cap_layout.py drew the MIM cap with
raw klayout.db polygons instead of PCells -- at the time, fix (2) above
had not been found. Any future PCell use in this repo needs both fixes.

"m" multiplicity convention (established by dac/layout/cap_array_caps_only_ref.spice
for cap_mim_2f0fF binary weighting): realize "m" as N separate parallel
physical unit devices, NOT a single instance with an M= SPICE parameter.
Used here for the MSB's pfet_m=2.
"""

import sys

sys.path.insert(0, "/foss/pdks/gf180mcuD/libs.tech/klayout/tech/pymacros")

import gdsfactory as gf  # noqa: E402

gf.gpdk.PDK.activate()

import klayout.db as db  # noqa: E402
from cells import gf180mcu  # noqa: E402

gf180mcu()
GF180_LIB = db.Library.library_by_name("gf180mcu")

NWELL_GAP = 1.5  # um, generous PMOS-nwell-to-NMOS-active spacing (checkpoint cell,
# not yet density/area-optimized -- see NW.2a_LV 0.6um connected-nwell /
# unrelated-diffusion spacing precedent in nwell.drc; 1.5um is a safe margin)
M1_SPACING = 0.31  # um, metal1 min spacing (m1_sp constant in draw_fet.py)
PFET_GAP = -0.15  # um "gap" (negative = overlap) between parallel PMOS instances'
# bounding boxes for the m=2 MSB case. The two PMOS devices are on the same
# node (both VDD-tied nwells) so overlapping nwells is correct/required --
# NW.2a_LV flags same-potential nwells closer than 0.6um that aren't merged
# into one polygon; a small negative gap guarantees the merge (measured:
# PFET_GAP=0.1 left a real 0.102um nwell-to-nwell gap, i.e. ~1:1 mapping).


def _fet_params(w_gate, l_gate, sd_lbl, g_lbl, sub_lbl):
    return dict(
        volt="3.3V",
        bulk="Bulk Tie",
        w_gate=w_gate,
        l_gate=l_gate,
        ld=0.52,
        nf=1,
        grw=0.38,
        gate_con_pos="alternating",
        con_bet_fin=1,
        sd_con_col=1,
        interdig=0,
        patt="",
        deepnwell=0,
        pcmpgr=0,
        patt_lbl=0,
        lbl=1,
        sd_lbl=sd_lbl,
        g_lbl=g_lbl,
        sub_lbl=sub_lbl,
    )


def _add_pcell(layout, top, pcell_name, params, trans):
    pcell_id = GF180_LIB.layout().pcell_id(pcell_name)
    pc = layout.add_pcell_variant(GF180_LIB, pcell_id, params)
    inst = top.insert(db.CellInstArray(pc, trans))
    return inst


def _labels(top, li_label, prefix):
    """Return {suffix: (x, y)} in um for every TEXT shape whose string startswith prefix."""
    out = {}
    for shp in top.shapes(li_label).each():
        if shp.is_text() and shp.text.string.startswith(prefix):
            out[shp.text.string] = (shp.text.x * top.layout().dbu, shp.text.y * top.layout().dbu)
    return out


GRID_DBU = 5  # gf180mcuD manufacturing grid is 0.005um; at dbu=0.001 that's 5 database units


def snap_to_grid(top, grid_dbu=GRID_DBU):
    """Snap every polygon/box vertex in `top` to the manufacturing grid.

    gdsfactory (via the generic-PDK-activation workaround) introduces
    sub-nm floating point drift that lands some vertices 1nm off the
    PDK's real 0.005um grid, tripping every *_OFFGRID DRC rule even
    though the shapes are geometrically correct. Text labels are left
    untouched (position doesn't need grid alignment).
    """
    layout = top.layout()
    for li in layout.layer_indexes():
        shapes = top.shapes(li)
        to_erase = []
        replacements = []
        for shp in shapes.each():
            if shp.is_text():
                continue
            if shp.is_box():
                b = shp.box
                nb = db.Box(
                    round(b.left / grid_dbu) * grid_dbu,
                    round(b.bottom / grid_dbu) * grid_dbu,
                    round(b.right / grid_dbu) * grid_dbu,
                    round(b.top / grid_dbu) * grid_dbu,
                )
                to_erase.append(shp)
                replacements.append(nb)
            elif shp.is_polygon() or shp.is_path():
                poly = shp.polygon if shp.is_polygon() else shp.path.polygon()
                pts = [
                    db.Point(round(p.x / grid_dbu) * grid_dbu, round(p.y / grid_dbu) * grid_dbu)
                    for p in poly.each_point_hull()
                ]
                to_erase.append(shp)
                replacements.append(db.SimplePolygon(pts))
        for shp in to_erase:
            shapes.erase(shp)
        for rep in replacements:
            shapes.insert(rep)


def _via_transition(top, dbu, x, y, li_m1, li_via1, li_m2):
    """Small M1+via1+M2 stack at (x,y): moves a net onto metal2 so long-
    distance routing never has to share metal1 with (and risk shorting
    to) an unrelated pad or rail it must physically cross -- V1.1 fixes
    via1 at 0.26um; a 0.23um half-width M1 landing pad gives 0.10um
    enclosure margin. The M2 pad is deliberately smaller (0.195 half-width,
    still >= M2.3's 0.1444um^2 min-area with margin): native pad pitch in a
    row (e.g. drain-to-bulk-tap, ~0.7um) is tight enough that a 0.23
    half-width M2 pad at every pad in the row violates M2.2a's 0.28um
    spacing against its own row-neighbor's M2 pad."""
    vh, ph, ph2 = 0.13, 0.23, 0.195

    def um(v):
        return int(round(v / dbu))

    top.shapes(li_m1).insert(db.Box(um(x - ph), um(y - ph), um(x + ph), um(y + ph)))
    top.shapes(li_via1).insert(db.Box(um(x - vh), um(y - vh), um(x + vh), um(y + vh)))
    top.shapes(li_m2).insert(db.Box(um(x - ph2), um(y - ph2), um(x + ph2), um(y + ph2)))


def _m2_wire(top, dbu, x0, y0, x1, y1, li_m2, hw=0.16):
    """Straight metal2 segment (M2.1 min width 0.28um; hw=0.16 -> 0.32um)."""

    def um(v):
        return int(round(v / dbu))

    top.shapes(li_m2).insert(
        db.Box(um(min(x0, x1) - hw), um(min(y0, y1) - hw), um(max(x0, x1) + hw), um(max(y0, y1) + hw))
    )


def _add_label(top, dbu, x, y, text, li_m1lbl):
    top.shapes(li_m1lbl).insert(db.Text(text, int(round(x / dbu)), int(round(y / dbu))))


def _via2_hop(top, dbu, x, y, li_via2, li_m3):
    """Add a via2+M3 landing at a point that already has an M2 pad (from
    _via_transition) -- moves the net from M2 up to M3 (V2.1 fixes via2 at
    0.26um). Same 0.195 half-width as the M2 pad, for the same reason
    (tight native-pad pitch would otherwise violate M3's own min spacing
    between neighboring pads' M3 landings)."""
    vh, ph = 0.13, 0.195

    def um(v):
        return int(round(v / dbu))

    top.shapes(li_via2).insert(db.Box(um(x - vh), um(y - vh), um(x + vh), um(y + vh)))
    top.shapes(li_m3).insert(db.Box(um(x - ph), um(y - ph), um(x + ph), um(y + ph)))


def _m3_wire(top, dbu, x0, y0, x1, y1, li_m3, hw=0.16):
    """Straight metal3 segment (M3.1 min width 0.28um; hw=0.16 -> 0.32um)."""

    def um(v):
        return int(round(v / dbu))

    top.shapes(li_m3).insert(
        db.Box(um(min(x0, x1) - hw), um(min(y0, y1) - hw), um(max(x0, x1) + hw), um(max(y0, y1) + hw))
    )


def _connect_shelf_m3(top, dbu, points, shelf_y, trunk_x, li_m1, li_via1, li_m2, li_via2, li_m3):
    """Like _connect_shelf_m2, but hops one layer further to metal3. Used
    for a net whose connection points structurally INTERLEAVE (in X) with
    another net's points on the same row -- e.g. the MSB's 2 parallel PMOS
    give gate points at [pg0, pg1] and drain points at [pd0, pd1] with
    pg0 < pd0 < pg1 < pd1, so gate's and VOUT's reach spans cross no
    matter how their Y-shelves are ordered (a classic non-planar routing
    conflict; the fix real layouts use is a dedicated layer per net, not
    more shelf-juggling on one layer)."""
    for (x, y) in points:
        _via_transition(top, dbu, x, y, li_m1, li_via1, li_m2)
        _via2_hop(top, dbu, x, y, li_via2, li_m3)
        _m3_wire(top, dbu, x, y, x, shelf_y, li_m3)
        _m3_wire(top, dbu, x, shelf_y, trunk_x, shelf_y, li_m3)


def _connect_shelf_m3_offset(top, dbu, x, y, shelf_y, trunk_x, x_jog, li_m1, li_via1, li_m2, li_via2, li_m3):
    """M3 counterpart of _connect_shelf_m2_offset (see its docstring)."""
    _via_transition(top, dbu, x, y, li_m1, li_via1, li_m2)
    _via2_hop(top, dbu, x, y, li_via2, li_m3)
    xo = x + x_jog
    _m3_wire(top, dbu, x, y, xo, y, li_m3)
    _m3_wire(top, dbu, xo, y, xo, shelf_y, li_m3)
    _m3_wire(top, dbu, xo, shelf_y, trunk_x, shelf_y, li_m3)


def _connect_net_m3_two_sides(
    top, dbu, top_points, bot_points, shelf_top, shelf_bot, trunk_x, label_text,
    li_m1, li_via1, li_m2, li_via2, li_m3, li_m1lbl,
):
    _connect_shelf_m3(top, dbu, top_points, shelf_top, trunk_x, li_m1, li_via1, li_m2, li_via2, li_m3)
    _connect_shelf_m3(top, dbu, bot_points, shelf_bot, trunk_x, li_m1, li_via1, li_m2, li_via2, li_m3)
    _m3_wire(top, dbu, trunk_x, shelf_bot, trunk_x, shelf_top, li_m3)
    _add_label(top, dbu, trunk_x, shelf_bot, label_text, li_m1lbl)


def _connect_shelf_m2_offset(top, dbu, x, y, shelf_y, trunk_x, x_jog, li_m1, li_via1, li_m2):
    """Like _connect_shelf_m2 for a single point, but jogs sideways by
    `x_jog` immediately after the via, before descending to the shelf.

    Needed when a point's straight-down column would pass too close to a
    DIFFERENT net's native via pad elsewhere in the same row -- e.g. the
    NMOS source's column heading to GND's (outermost, so it must travel
    past) shelf passes directly by the NMOS gate's via pad only ~0.54um
    away natively, clearing by just 0.185um where M2.2a needs 0.28um. No
    amount of shelf-Y reordering fixes this (it's an X-proximity issue
    between a column and a *static* pad, not two reaches); a real routing
    would call this a jog around an obstacle.
    """
    _via_transition(top, dbu, x, y, li_m1, li_via1, li_m2)
    xo = x + x_jog
    _m2_wire(top, dbu, x, y, xo, y, li_m2)
    _m2_wire(top, dbu, xo, y, xo, shelf_y, li_m2)
    _m2_wire(top, dbu, xo, shelf_y, trunk_x, shelf_y, li_m2)


def _connect_shelf_m2(top, dbu, points, shelf_y, trunk_x, li_m1, li_via1, li_m2):
    """Via-transition each (x,y) onto metal2, jump vertically (at the
    point's own X) from its native Y up/down to `shelf_y`, then reach
    horizontally (at shelf_y) over to `trunk_x`.

    Bounding each jump to exactly [native_y, shelf_y] keeps it clear of
    any OTHER net's shelf further out (it never overshoots into that
    territory); giving each net its own exclusive shelf_y keeps its
    horizontal reach clear of every other net's reach regardless of X
    overlap. This is the fix for the actual failure mode found via LVS:
    routing a horizontal reach at a pad's *native* row Y -- even on M2 --
    still crosses other nets' via-transition points that share that same
    Y band (e.g. a bulk-tap reach passing directly over a drain's via),
    shorting them. Two nets only conflict here if they share a shelf_y;
    giving every net(-side) its own shelf and stopping each jump exactly
    at its own shelf avoids that by construction.
    """
    for (x, y) in points:
        _via_transition(top, dbu, x, y, li_m1, li_via1, li_m2)
        _m2_wire(top, dbu, x, y, x, shelf_y, li_m2)
        _m2_wire(top, dbu, x, shelf_y, trunk_x, shelf_y, li_m2)


def _connect_net_m2_one_side(top, dbu, points, shelf_y, trunk_x, label_text, li_m1, li_via1, li_m2, li_m1lbl):
    """A net whose points all sit on one side of the gap (e.g. VDD: PMOS
    source + bulk-tap only)."""
    _connect_shelf_m2(top, dbu, points, shelf_y, trunk_x, li_m1, li_via1, li_m2)
    _add_label(top, dbu, trunk_x, shelf_y, label_text, li_m1lbl)


def _connect_net_m2_two_sides(
    top, dbu, top_points, bot_points, shelf_top, shelf_bot, trunk_x, label_text, li_m1, li_via1, li_m2, li_m1lbl
):
    """A net spanning both rows (VOUT, bN_bar): each side gets its own
    shelf, then a single M2 trunk bar at `trunk_x` connects the two
    shelves (safe: nothing else occupies the gap between the two rows
    at trunk_x -- each side's points never jump past their own shelf)."""
    _connect_shelf_m2(top, dbu, top_points, shelf_top, trunk_x, li_m1, li_via1, li_m2)
    _connect_shelf_m2(top, dbu, bot_points, shelf_bot, trunk_x, li_m1, li_via1, li_m2)
    _m2_wire(top, dbu, trunk_x, shelf_bot, trunk_x, shelf_top, li_m2)
    _add_label(top, dbu, trunk_x, shelf_bot, label_text, li_m1lbl)


def build_driver_cell(
    layout,
    cell_name,
    nfet_w,
    pfet_w,
    pfet_count,
    l_gate=0.28,
    vdd_net="VDD",
    gnd_net="GND",
    gate_net="bN_bar",
    out_net="VOUT",
):
    top = layout.create_cell(cell_name)
    dbu = layout.dbu

    li_comp = layout.layer(22, 0)
    li_m1 = layout.layer(34, 0)
    li_m1lbl = layout.layer(34, 10)
    li_via1 = layout.layer(35, 0)
    li_m2 = layout.layer(36, 0)
    li_via2 = layout.layer(38, 0)
    li_m3 = layout.layer(42, 0)

    # --- PMOS row: pfet_count parallel devices, tied together ---
    pfet_insts = []
    x = 0.0
    for i in range(pfet_count):
        sub = f"pvdd{i}"
        params = _fet_params(pfet_w, l_gate, [f"ps{i}", f"pd{i}"], [f"pg{i}"], sub)
        tr = db.Trans(db.Vector(int(round(x / dbu)), 0))
        pfet_insts.append(_add_pcell(layout, top, "pfet", params, tr))
        # measure this instance's width by instantiating standalone to get pitch
        probe_layout = db.Layout()
        probe_top = probe_layout.create_cell("probe")
        _add_pcell(probe_layout, probe_top, "pfet", params, db.Trans())
        probe_top.flatten(1)
        w = probe_top.bbox().width() * probe_layout.dbu
        x += w + PFET_GAP

    top.flatten(1)
    pfet_bbox = top.bbox()
    pfet_ymin = pfet_bbox.bottom * dbu
    pfet_ymax = pfet_bbox.top * dbu

    # --- NMOS row, placed below with NWELL_GAP clearance ---
    probe_layout = db.Layout()
    probe_top = probe_layout.create_cell("probe")
    nfet_params = _fet_params(nfet_w, l_gate, ["ns0", "nd0"], ["ng0"], "ngnd0")
    _add_pcell(probe_layout, probe_top, "nfet", nfet_params, db.Trans())
    probe_top.flatten(1)
    nfet_bbox_probe = probe_top.bbox()
    nfet_top_at_origin = nfet_bbox_probe.top * probe_layout.dbu
    nfet_bot_at_origin = nfet_bbox_probe.bottom * probe_layout.dbu

    nfet_y = pfet_ymin - NWELL_GAP - nfet_top_at_origin
    nfet_tr = db.Trans(db.Vector(int(0), int(round(nfet_y / dbu))))
    _add_pcell(layout, top, "nfet", nfet_params, nfet_tr)
    top.flatten(1)
    nfet_ymin = nfet_y + nfet_bot_at_origin

    # --- gather label positions ---
    p_labels = _labels(top, li_m1lbl, "p")
    n_labels = _labels(top, li_m1lbl, "n")

    p_src = [p_labels[f"ps{i}"] for i in range(pfet_count)]
    p_drn = [p_labels[f"pd{i}"] for i in range(pfet_count)]
    p_gate = [p_labels[f"pg{i}"] for i in range(pfet_count)]
    p_sub = [p_labels[f"pvdd{i}"] for i in range(pfet_count)]
    n_src = n_labels["ns0"]
    n_drn = n_labels["nd0"]
    n_gate = n_labels["ng0"]
    n_sub = n_labels["ngnd0"]

    # Every net gets its own exclusive metal2 Y-shelf, well clear of the two
    # rows and of every other net's shelf (see _connect_shelf_m2) -- routing
    # a reach at a pad's *native* row Y (even on M2) still crosses other
    # nets' via-transition points sharing that Y band and shorts them, which
    # is what an earlier version of this routing did.
    # SHELF ordering matters, not just separation: VDD/GND connect two
    # far-apart points (source + bulk-tap) so their *reach* at their own
    # shelf is wide; VOUT/gate connect a single point per side to a nearby
    # trunk_x so their reach is a near-zero-length square. A wide-reach net
    # must be the OUTERMOST (furthest-from-row) shelf on its side -- any
    # narrower net further out would have its column pass *through* the
    # wide net's shelf on the way out, and a wide reach spans enough X to
    # hit that column. (Columns themselves are always narrow, so a
    # wide-reach net being outermost is safe: only narrow reaches occur at
    # the shelves its own column passes through on the way there.)
    SHELF = 0.7  # >= M2.2a's 0.28um spacing + 2*hw(0.16) margin, times some safety
    vdd_y = pfet_ymax + 2 * SHELF  # outermost above pfet (wide reach)
    gnd_y = nfet_ymin - 3 * SHELF  # outermost below nfet (wide reach)
    vout_top, vout_bot = pfet_ymax + 1 * SHELF, nfet_ymin - 1 * SHELF
    gate_top, gate_bot = pfet_ymin - 1 * SHELF, nfet_ymin - 2 * SHELF

    # VOUT alone routes on metal3, not metal2: its trunk necessarily spans
    # the FULL row-to-row height (PMOS drain to NMOS drain), so it passes
    # through every other net's shelf height along the way. For pfet_count=1
    # that's harmless (VDD/gate's reaches at those heights are narrow), but
    # for pfet_count>1 (the MSB's m=2 case) VDD's points (source+bulk-tap
    # per instance) structurally INTERLEAVE in X with VOUT's own points
    # (drain per instance) -- e.g. two instances give native X order
    # ps0 < pg0 < pd0 < pvdd0 ~ ps1 < pg1 < pd1 < pvdd1, so pvdd0/ps1 sits
    # inside VOUT's [pd0,pd1] span. No Y-shelf ordering resolves that on one
    # layer -- whichever net is "outer" has its column pass directly through
    # the other's reach. Real layouts solve exactly this with a dedicated
    # layer per net that must cross everything else; VDD/GND/gate all stay
    # on M2 (none of them has a full-height trunk, so none of them crosses
    # each other: VDD/GND's reaches are local to their own end of the cell,
    # and gate's two shelves sit entirely below pfet_ymin, never overlapping
    # VDD's near-pfet_ymax shelf or GND's near-nfet_ymin one).
    _connect_net_m2_one_side(top, dbu, p_src + p_sub, vdd_y, p_src[0][0], vdd_net, li_m1, li_via1, li_m2, li_m1lbl)
    # n_src's column must travel out to GND's (outermost) shelf, passing directly
    # by the NMOS gate's native via pad only ~0.5um away -- jog left first (see
    # _connect_shelf_m2_offset) to clear it; n_sub (bulk-tap, far from the gate) needs no jog.
    _connect_shelf_m2_offset(top, dbu, n_src[0], n_src[1], gnd_y, n_src[0], -0.3, li_m1, li_via1, li_m2)
    _connect_shelf_m2(top, dbu, [n_sub], gnd_y, n_src[0], li_m1, li_via1, li_m2)
    _add_label(top, dbu, n_src[0], gnd_y, gnd_net, li_m1lbl)
    # Same reasoning as gate_trunk_x below: VOUT's trunk spans the full
    # row-to-row height, so trunk_x=n_drn[0] (only ~0.5um from gate's own
    # native via pad) is too close regardless of gate's own routing -- a
    # via_transition pad sits at a point's real coordinates no matter where
    # that net's reach/trunk go afterward. Go far right (opposite of
    # gate's far-left) to clear every native pad in the row at once.
    vout_trunk_x = max(n_src[0], n_sub[0], p_src[0][0], p_sub[0][0], n_drn[0], *[p[0] for p in p_drn]) + 1.3
    # p_drn's column heads UP to vout_top (away from p_gate, which sits at the
    # BOTTOM of the pfet row) so it never passes p_gate's height -- no jog
    # needed there. n_drn's column heads DOWN to vout_bot, past n_gate's
    # height (n_gate sits at the bottom of the nfet row too) -- same jog
    # n_src needed against GND above.
    _connect_shelf_m3(top, dbu, p_drn, vout_top, vout_trunk_x, li_m1, li_via1, li_m2, li_via2, li_m3)
    _connect_shelf_m3_offset(
        top, dbu, n_drn[0], n_drn[1], vout_bot, vout_trunk_x, 0.3, li_m1, li_via1, li_m2, li_via2, li_m3
    )
    _m3_wire(top, dbu, vout_trunk_x, vout_bot, vout_trunk_x, vout_top, li_m3)
    _add_label(top, dbu, vout_trunk_x, vout_bot, out_net, li_m1lbl)
    # gate's trunk_x must clear BOTH source's and drain's native via pads by
    # a full row (its column is continuous from gate_top to gate_bot, so it
    # passes every other native pad's Y along the way, not just gate's own)
    # -- n_gate[0] sits BETWEEN source and drain natively, too close to
    # both (~0.5um) for any trunk_x to clear both simultaneously. Going far
    # enough left of source is the only way to clear everything at once --
    # but that makes gate's reach-to-trunk wide enough to instead cross
    # GND's column (which, being outermost, passes through gate_bot's
    # height). Route gate on M3 (like VOUT) to sidestep GND entirely; it
    # no longer conflicts with VOUT there since the far-left trunk_x keeps
    # gate's M3 shapes well clear of VOUT's (n_drn[0]-anchored) M3 shapes.
    gate_trunk_x = min(n_src[0], n_sub[0], p_src[0][0], p_sub[0][0]) - 1.3
    _connect_net_m3_two_sides(
        top, dbu, p_gate, [n_gate], gate_top, gate_bot, gate_trunk_x, gate_net,
        li_m1, li_via1, li_m2, li_via2, li_m3, li_m1lbl,
    )

    snap_to_grid(top)
    return top


def build_nand2_cell(layout, cell_name, pfet_w=1.7, nfet_w=1.7, l_gate=0.3):
    """2-input NAND matching dac/schematic/nand2.sch: 2 parallel PMOS
    (source=DVDD, drain=y, gates=a/b), 2 series NMOS (top: drain=y,
    gate=a, source=mid; bottom: drain=mid, gate=b, source=DVSS). Series
    stacking is realized as two separate PCell instances M1-wired
    together (top's source pad to bottom's drain pad) rather than a
    shared-diffusion 2-finger device, for the same reason unit_switch's
    m=2 uses parallel physical devices: simpler, verifiable connectivity
    over layout density at this checkpoint stage.
    """
    top = layout.create_cell(cell_name)
    dbu = layout.dbu
    li_m1 = layout.layer(34, 0)
    li_m1lbl = layout.layer(34, 10)
    li_via1 = layout.layer(35, 0)
    li_m2 = layout.layer(36, 0)
    li_via2 = layout.layer(38, 0)
    li_m3 = layout.layer(42, 0)

    # --- PMOS row: 2 parallel devices (A gate=a, B gate=b), tied source/drain ---
    p_params = []
    x = 0.0
    for tag in ("a", "b"):
        params = _fet_params(pfet_w, l_gate, [f"ps_{tag}", f"pd_{tag}"], [f"pg_{tag}"], f"pvdd_{tag}")
        p_params.append(params)
        tr = db.Trans(db.Vector(int(round(x / dbu)), 0))
        _add_pcell(layout, top, "pfet", params, tr)
        probe_layout = db.Layout()
        probe_top = probe_layout.create_cell("probe")
        _add_pcell(probe_layout, probe_top, "pfet", params, db.Trans())
        probe_top.flatten(1)
        w = probe_top.bbox().width() * probe_layout.dbu
        x += w + 0.6  # generous same-net-but-separate-instance spacing (not merged like m=2 nwells)

    top.flatten(1)
    pfet_ymin = top.bbox().bottom * dbu
    pfet_ymax = top.bbox().top * dbu

    # 3 stacked rows (pfet, ntop, nbot) need up to 3 distinct shelves in a single
    # gap (y, a, and b's pfet-side escape all live in the pfet/ntop gap) -- widen
    # the row-to-row spacing here (vs. NWELL_GAP's 1.5um for the 2-row driver
    # cell) so SHELF-separated shelves (0.7um apart, 3 of them) fit with margin.
    NAND2_GAP = 3.0

    # --- NMOS_top (drain=y, gate=a, source=mid) ---
    probe_layout = db.Layout()
    probe_top = probe_layout.create_cell("probe")
    ntop_params = _fet_params(nfet_w, l_gate, ["ntop_d", "ntop_s"], ["ntop_g"], "ntop_sub")
    _add_pcell(probe_layout, probe_top, "nfet", ntop_params, db.Trans())
    probe_top.flatten(1)
    ntop_top_at_origin = probe_top.bbox().top * probe_layout.dbu
    ntop_height = probe_top.bbox().height() * probe_layout.dbu

    ntop_y = pfet_ymin - NAND2_GAP - ntop_top_at_origin
    _add_pcell(layout, top, "nfet", ntop_params, db.Trans(db.Vector(0, int(round(ntop_y / dbu)))))
    top.flatten(1)
    ntop_ymin = ntop_y + (probe_top.bbox().bottom * probe_layout.dbu)

    # --- NMOS_bottom (drain=mid, gate=b, source=DVSS) ---
    nbot_params = _fet_params(nfet_w, l_gate, ["nbot_d", "nbot_s"], ["nbot_g"], "nbot_sub")
    probe_layout = db.Layout()
    probe_top = probe_layout.create_cell("probe")
    _add_pcell(probe_layout, probe_top, "nfet", nbot_params, db.Trans())
    probe_top.flatten(1)
    nbot_top_at_origin = probe_top.bbox().top * probe_layout.dbu
    nbot_bot_at_origin = probe_top.bbox().bottom * probe_layout.dbu

    nbot_y = ntop_y - NAND2_GAP - (ntop_height - ntop_top_at_origin) - nbot_top_at_origin
    _add_pcell(layout, top, "nfet", nbot_params, db.Trans(db.Vector(0, int(round(nbot_y / dbu)))))
    top.flatten(1)
    nbot_ymin = nbot_y + nbot_bot_at_origin

    pa = _labels(top, li_m1lbl, "p")
    na = _labels(top, li_m1lbl, "n")

    p_src = [pa["ps_a"], pa["ps_b"]]
    p_drn = [pa["pd_a"], pa["pd_b"]]
    p_gate = {"a": pa["pg_a"], "b": pa["pg_b"]}
    p_sub = [pa["pvdd_a"], pa["pvdd_b"]]
    ntop_d, ntop_s, ntop_g = na["ntop_d"], na["ntop_s"], na["ntop_g"]
    nbot_d, nbot_s, nbot_g, nbot_sub = na["nbot_d"], na["nbot_s"], na["nbot_g"], na["nbot_sub"]

    # Every net gets its own exclusive metal2 shelf (see build_driver_cell's
    # _connect_shelf_m2 docstring for why: a reach at a pad's *native* row Y --
    # even on M2 -- crosses other nets' via points sharing that Y band).
    # Shelf ORDER matters, not just separation (see build_driver_cell's SHELF
    # comment): a net whose reach spans a wide X (y: 2 separate PMOS drains;
    # DVDD/DVSS: source+bulk-tap; b: gate-to-far-trunk_x) must be the
    # OUTERMOST shelf on its side, so nothing else's column need travel far
    # enough to cross it -- a narrower net's column only travels out to ITS
    # OWN (closer) shelf and never enters the wide net's territory.
    STEP = 0.7
    dvdd_y = pfet_ymax + 1 * STEP
    a_shelf = pfet_ymin - 1 * STEP  # pfet/ntop gap, innermost (narrow: 1 point each side)
    y_shelf = pfet_ymin - 2 * STEP  # middle (wide: 2 PMOS drains + ntop)
    b_top_shelf = pfet_ymin - 3 * STEP  # outermost (b's reach runs far in X to clear y_shelf)
    mid_shelf = ntop_ymin - 1 * STEP  # ntop/nbot gap (only net there)
    dvss_y = nbot_ymin - 1 * STEP  # below nbot row, innermost (wide: source+bulk-tap)
    b_bot_shelf = nbot_ymin - 2 * STEP  # outermost
    b_trunk_x = max(pa["pd_a"][0], pa["pd_b"][0], ntop_d[0], p_gate["b"][0], nbot_g[0]) + 2.0

    # y and b route on M3 (like unit_switch's VOUT/gate): both have reaches
    # or trunks that span far enough in X/Y to otherwise cross another
    # net's native via pad or reach at close range -- see build_driver_cell's
    # notes on why (native pad pitch is tight, and via_transition always
    # leaves a static pad at a point's real coordinates regardless of that
    # net's own trunk direction). DVDD/a/mid/DVSS stay on M2.
    _connect_net_m2_one_side(top, dbu, p_src + p_sub, dvdd_y, p_src[0][0], "DVDD", li_m1, li_via1, li_m2, li_m1lbl)
    _connect_net_m3_two_sides(
        top, dbu, p_drn, [ntop_d], y_shelf, y_shelf, ntop_d[0], "y",
        li_m1, li_via1, li_m2, li_via2, li_m3, li_m1lbl,
    )
    _connect_net_m3_two_sides(
        top, dbu, [p_gate["a"]], [ntop_g], a_shelf, a_shelf, ntop_g[0], "a",
        li_m1, li_via1, li_m2, li_via2, li_m3, li_m1lbl,
    )
    _connect_net_m3_two_sides(
        top, dbu, [ntop_s], [nbot_d], mid_shelf, mid_shelf, ntop_s[0], "mid",
        li_m1, li_via1, li_m2, li_via2, li_m3, li_m1lbl,
    )
    # p_gate["b"]'s column descends past y_shelf's height (b_top_shelf is
    # further out) right where y's own pd_b column sits (gate and drain are
    # adjacent within the same PMOS instance, only ~0.5um apart) -- jog
    # away first, same pattern as unit_switch's n_drn vs n_gate.
    _connect_shelf_m3_offset(
        top, dbu, p_gate["b"][0], p_gate["b"][1], b_top_shelf, b_trunk_x, -0.6,
        li_m1, li_via1, li_m2, li_via2, li_m3,
    )
    _connect_shelf_m3(top, dbu, [nbot_g], b_bot_shelf, b_trunk_x, li_m1, li_via1, li_m2, li_via2, li_m3)
    _m3_wire(top, dbu, b_trunk_x, b_bot_shelf, b_trunk_x, b_top_shelf, li_m3)
    _add_label(top, dbu, b_trunk_x, b_bot_shelf, "b", li_m1lbl)
    _connect_net_m2_one_side(
        top, dbu, [nbot_s, nbot_sub], dvss_y, nbot_s[0], "DVSS", li_m1, li_via1, li_m2, li_m1lbl
    )

    snap_to_grid(top)
    return top


def main():
    layout = db.Layout()
    layout.dbu = 0.001

    build_driver_cell(layout, "unit_switch_bit0", nfet_w=0.42, pfet_w=0.84, pfet_count=1)
    build_driver_cell(layout, "unit_switch_bit7", nfet_w=53.76, pfet_w=53.76, pfet_count=2)

    options = db.SaveLayoutOptions()
    options.write_context_info = False
    layout.write("/foss/designs/dac/layout/unit_switch_checkpoint.gds", options)
    print("wrote dac/layout/unit_switch_checkpoint.gds with topcells:", [c.name for c in layout.each_cell()])

    logic_layout = db.Layout()
    logic_layout.dbu = 0.001
    build_driver_cell(
        logic_layout, "inv1", nfet_w=0.85, pfet_w=1.7, pfet_count=1, l_gate=0.3,
        vdd_net="DVDD", gnd_net="DVSS", gate_net="vin", out_net="vout",
    )
    build_nand2_cell(logic_layout, "nand2")
    logic_layout.write("/foss/designs/dac/layout/dac_logic_checkpoint.gds", options)
    print("wrote dac/layout/dac_logic_checkpoint.gds with topcells:", [c.name for c in logic_layout.each_cell()])


if __name__ == "__main__":
    main()
