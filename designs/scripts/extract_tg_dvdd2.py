#!/usr/bin/env python3
"""Probe every metal level for polygons containing or near the tgate
DVDD/DVSS label points (cell-local)."""
import klayout.db as db

DBU = 0.001
PLACE = (88.0, 0.0)
POINTS = {"DVDD": (1.620, 9.490), "DVSS": (19.580, -7.280)}
METAL = {1: (34, 0), 2: (36, 0), 3: (42, 0), 4: (46, 0), 5: (81, 0)}

layout = db.Layout()
layout.read("/foss/designs/dac/layout/dac_logic_checkpoint.gds")
tg = layout.cell("tgate")

for name, (lx, ly) in POINTS.items():
    pt = db.Point(int(round(lx / DBU)), int(round(ly / DBU)))
    probe = db.Box(pt.x - 1000, pt.y - 1000, pt.x + 1000, pt.y + 1000)
    print(f"=== {name} label cell-local ({lx:.3f},{ly:.3f}) top ({lx+PLACE[0]:.3f},{ly+PLACE[1]:.3f}) ===")
    for lvl, ld in METAL.items():
        li = layout.layer(*ld)
        r = db.Region(tg.begin_shapes_rec(li))
        r.merge()
        for p in r.each_merged():
            bb = p.bbox()
            if p.inside(pt):
                rel = "CONTAINS"
            elif bb.overlaps(probe):
                rel = "near(<=1um)"
            else:
                continue
            print(f"  M{lvl} {rel}: bbox local ({bb.left*DBU:.3f},{bb.bottom*DBU:.3f})"
                  f"..({bb.right*DBU:.3f},{bb.top*DBU:.3f})"
                  f" top ({bb.left*DBU+PLACE[0]:.3f},{bb.bottom*DBU+PLACE[1]:.3f})"
                  f"..({bb.right*DBU+PLACE[0]:.3f},{bb.top*DBU+PLACE[1]:.3f})")
