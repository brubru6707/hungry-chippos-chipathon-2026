#!/usr/bin/env python3
"""Third recon pass: remaining unknown geometry."""
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

WINDOWS = {
    'A_via_m9area': (-5.9, 4.0, -4.5, 5.4, ['m1', 'via1', 'm2']),
    'B_vout1_trunk': (-19.2, 16.0, -17.2, 17.8, ['m1']),
    'C_corridor_m2': (9.0, -0.4, 16.2, 1.8, ['m2', 'via1']),
}
LM = {'m1': (34, 0), 'via1': (35, 0), 'm2': (36, 0)}

for wname, (x1, y1, x2, y2, layers) in WINDOWS.items():
    bx = db.Box(int(round(x1/dbu)), int(round(y1/dbu)), int(round(x2/dbu)), int(round(y2/dbu)))
    print(f"\n##### {wname} ({x1},{y1})..({x2},{y2}) #####")
    for ln in layers:
        r = merged(*LM[ln], bx)
        for i, poly in enumerate(r.each()):
            pts = ' '.join(f"({p.x*dbu:.3f},{p.y*dbu:.3f})" for p in poly.each_point_hull())
            print(f"  {ln}[{i}]: {pts}")
