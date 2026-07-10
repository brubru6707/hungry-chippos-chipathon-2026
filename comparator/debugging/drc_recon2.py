#!/usr/bin/env python3
"""Vertex-level dump: merged regions clipped to windows, per layer."""
import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()
dbu = layout.dbu

def merged(lnum, dnum, bx):
    li = layout.layer(lnum, dnum)
    r = db.Region(top.begin_shapes_rec_touching(li, bx))
    r.merge()
    return r & db.Region(bx)

# window: (x1,y1,x2,y2, layers)
WINDOWS = {
    # narrow m1 traces (window = trace + 0.7 margin)
    't1':  (2.6, -20.9, 4.2, -15.1, ['m1']),
    't2':  (-11.0, -10.6, -9.3, -0.3, ['m1']),
    't3t4':(-10.9, -1.9, -7.8, 0.5, ['m1']),
    't5t6':(-27.0, 12.1, -23.2, 18.5, ['m1']),
    't7':  (-24.8, 17.0, -18.8, 18.6, ['m1']),
    't8t9':(10.8, -9.0, 14.4, 0.2, ['m1']),
    't10': (2.4, 18.1, 11.4, 19.7, ['m1']),
    't11': (19.6, 18.3, 21.2, 20.2, ['m1']),
    't12': (-38.9, 18.0, -29.2, 19.6, ['m1']),
    # spacing / other clusters
    'R1_corridor': (10.9, -0.3, 16.3, 1.7, ['m1','via1','m2']),
    'stub_bottom': (14.6, -2.4, 16.2, 0.2, ['m1','via1','m2']),
    'R2_gap': (-8.4, 1.0, -6.4, 2.4, ['m1']),
    'R3_gap': (2.3, -13.3, 5.3, -11.3, ['m1']),
    'R4_vddtrunk': (-19.3, 17.9, -17.4, 21.4, ['m1']),
    'R5b_via_m1': (11.2, -2.0, 12.2, -0.9, ['m1']),
    'R5a_m2': (-4.6, 19.0, -2.4, 20.4, ['m2','m1']),
    'R8_m2_west': (19.3, 17.9, 22.4, 19.2, ['m2','via1']),
    'R8_m2_east': (27.6, 18.2, 30.7, 19.5, ['m2','via1']),
}
LM = {'m1': (34,0), 'via1': (35,0), 'm2': (36,0), 'comp': (22,0), 'poly': (30,0), 'cont': (33,0)}

for wname, (x1, y1, x2, y2, layers) in WINDOWS.items():
    bx = db.Box(int(round(x1/dbu)), int(round(y1/dbu)), int(round(x2/dbu)), int(round(y2/dbu)))
    print(f"\n##### {wname} ({x1},{y1})..({x2},{y2}) #####")
    for ln in layers:
        r = merged(*LM[ln], bx)
        for i, poly in enumerate(r.each()):
            pts = ' '.join(f"({p.x*dbu:.3f},{p.y*dbu:.3f})" for p in poly.each_point_hull())
            print(f"  {ln}[{i}]: {pts}")
