#!/usr/bin/env python3
"""Extract the tgate cell's DVDD/DVSS tap pin geometry, in both cell-local
and placed top-level coordinates (tgate is placed at (88.0, 0.0) in
dac_top_floorplan).  Reports every label in the cell plus the metal
polygons containing/near each supply label so the routing pass can land a
via INSIDE the real pin rectangle instead of assuming coordinates."""
import klayout.db as db

DBU = 0.001
PLACE = (88.0, 0.0)

layout = db.Layout()
layout.read("/foss/designs/dac/layout/dac_logic_checkpoint.gds")
tg = layout.cell("tgate")
assert tg is not None

METAL = {1: (34, 0), 2: (36, 0), 3: (42, 0), 4: (46, 0), 5: (81, 0)}
LABEL = {1: (34, 10), 2: (36, 10), 3: (42, 10), 4: (46, 10), 5: (81, 10)}

print("=== all labels in tgate (cell-local um) ===")
labels = []
for lvl, (ln, dt) in LABEL.items():
    li = layout.layer(ln, dt)
    for s in tg.begin_shapes_rec(li):
        sh = s.shape()
        if sh.is_text():
            t = sh.text.transformed(s.trans())
            x, y = t.x * DBU, t.y * DBU
            labels.append((sh.text.string, lvl, x, y))
            print(f"  '{sh.text.string}' M{lvl} label at ({x:.3f}, {y:.3f})"
                  f"  top-level ({x+PLACE[0]:.3f}, {y+PLACE[1]:.3f})")

print("\n=== metal polygons containing each supply label ===")
for name, lvl, lx, ly in labels:
    if name.upper() not in ("DVDD", "DVSS", "VDD", "VSS", "0"):
        continue
    li = layout.layer(*METAL[lvl])
    r = db.Region(tg.begin_shapes_rec(li))
    r.merge()
    pt = db.Point(int(round(lx / DBU)), int(round(ly / DBU)))
    for p in r.each_merged():
        if p.inside(pt):
            bb = p.bbox()
            print(f"  '{name}' M{lvl}: containing polygon bbox cell-local "
                  f"({bb.left*DBU:.3f},{bb.bottom*DBU:.3f})..({bb.right*DBU:.3f},{bb.top*DBU:.3f})"
                  f"  top-level ({bb.left*DBU+PLACE[0]:.3f},{bb.bottom*DBU+PLACE[1]:.3f})"
                  f"..({bb.right*DBU+PLACE[0]:.3f},{bb.top*DBU+PLACE[1]:.3f})"
                  f"  area_um2={p.area()*DBU*DBU:.3f}")

print("\n=== tgate cell bbox ===")
bb = tg.bbox()
print(f"  cell-local ({bb.left*DBU:.3f},{bb.bottom*DBU:.3f})..({bb.right*DBU:.3f},{bb.top*DBU:.3f})")
print(f"  top-level  ({bb.left*DBU+PLACE[0]:.3f},{bb.bottom*DBU+PLACE[1]:.3f})"
      f"..({bb.right*DBU+PLACE[0]:.3f},{bb.top*DBU+PLACE[1]:.3f})")
