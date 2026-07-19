#!/usr/bin/env python3
"""Locate the cap_array dummy-ring M3 GND frame's real geometry (placed at
(0,0) in dac_top_floorplan, so cell-local == top-level coordinates), plus
anything on M3/M4/M5 in the planned strap corridor south of the array."""
import klayout.db as db

DBU = 0.001
layout = db.Layout()
layout.read("/foss/designs/dac/layout/cap_array.gds")
cap = layout.cell("cap_array")

bb = cap.bbox()
print(f"cap_array bbox ({bb.left*DBU:.3f},{bb.bottom*DBU:.3f})..({bb.right*DBU:.3f},{bb.top*DBU:.3f})")

m3 = layout.layer(42, 0)
r = db.Region(cap.begin_shapes_rec(m3))
r.merge()
# The frame is the merged M3 polygon with the largest bbox.
best = max(r.each_merged(), key=lambda p: p.bbox().area())
fb = best.bbox()
print(f"largest M3 polygon bbox ({fb.left*DBU:.3f},{fb.bottom*DBU:.3f})..({fb.right*DBU:.3f},{fb.top*DBU:.3f})")

# Probe candidate strap start points on the frame's south bar.
for x in (0.0, -5.0, 5.0):
    pt = db.Point(int(round(x / DBU)), fb.bottom + 140)  # 0.14um above bottom edge
    hit = any(p.inside(pt) for p in r.each_merged())
    print(f"probe M3 ({x:.2f}, {(fb.bottom+140)*DBU:.3f}): {'HIT' if hit else 'miss'}")

# Anything in the strap corridor x in [-2, 2], y in [-130, frame_bottom]?
corr = db.Box(int(-2 / DBU), int(-130 / DBU), int(2 / DBU), fb.bottom)
for lvl, ld in ((3, (42, 0)), (4, (46, 0)), (5, (81, 0)), (2, (36, 0))):
    li = layout.layer(*ld)
    reg = db.Region(cap.begin_shapes_rec(li))
    reg.merge()
    n = 0
    for p in reg.each_merged():
        if p.bbox().overlaps(corr):
            b2 = p.bbox()
            print(f"corridor M{lvl}: ({b2.left*DBU:.3f},{b2.bottom*DBU:.3f})..({b2.right*DBU:.3f},{b2.top*DBU:.3f})")
            n += 1
    if n == 0:
        print(f"corridor M{lvl}: empty")
