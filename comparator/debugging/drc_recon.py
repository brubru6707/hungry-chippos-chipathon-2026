#!/usr/bin/env python3
"""Dump all shapes (with cell ownership) intersecting named regions, per layer."""
import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()
dbu = layout.dbu

LAYERS = {'comp': (22, 0), 'poly': (30, 0), 'contact': (33, 0),
          'metal1': (34, 0), 'via1': (35, 0), 'metal2': (36, 0)}

REGIONS = {
    'R1_m1gate':   (10.5, -0.4, 16.2, 1.8),
    'R2_m9gap':    (-8.2, 1.2, -6.6, 2.3),
    'R3_tailgap':  (2.5, -13.0, 5.2, -11.6),
    'R4_m3pocket': (-19.8, 16.0, -15.6, 21.3),
    'R5a_dangling':(-4.5, 19.0, -2.5, 20.4),
    'R5b_dangling':(11.1, -2.0, 12.3, -0.9),
    'R6_m6via':    (-29.6, 17.5, -28.2, 18.8),
    'R7_m5corner': (28.2, 17.1, 29.7, 18.4),
    'R8_v14b':     (19.4, 17.8, 30.8, 19.0),
}

def fmt(b):
    return f"({b.left*dbu:.3f},{b.bottom*dbu:.3f};{b.right*dbu:.3f},{b.top*dbu:.3f})"

for rname, (x1, y1, x2, y2) in REGIONS.items():
    bx = db.Box(int(x1/dbu), int(y1/dbu), int(x2/dbu), int(y2/dbu))
    print(f"\n########## {rname} {x1},{y1} .. {x2},{y2} ##########")
    for lname, (l, d) in LAYERS.items():
        li = layout.layer(l, d)
        seen = []
        it = top.begin_shapes_rec_touching(li, bx)
        while not it.at_end():
            s = it.shape()
            if s.is_box() or s.is_polygon() or s.is_path():
                poly = s.polygon.transformed(it.trans())
                owner = layout.cell(it.cell_index()).name
                seen.append((fmt(poly.bbox()), owner, str(poly.num_points())))
            it.next()
        if seen:
            print(f"  -- {lname} --")
            for bb, owner, npts in sorted(seen):
                print(f"    {bb}  cell={owner} pts={npts}")
