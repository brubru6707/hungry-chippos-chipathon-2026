import klayout.db as db
layout = db.Layout()
layout.read('/foss/designs/comparator/layout/strongarm.gds')
top = layout.top_cell()
dbu = layout.dbu

def clipdump(l, d, x1, y1, x2, y2, label):
    r = db.Region(top.begin_shapes_rec(layout.layer(l, d)))
    r.merge()
    c = r & db.Region(db.Box(int(x1/dbu), int(y1/dbu), int(x2/dbu), int(y2/dbu)))
    print(f"{label} in ({x1}..{x2}, {y1}..{y2}): {c.count()} shapes")
    for p in c.each():
        b = p.bbox()
        print(f"   x:{b.left*dbu:.3f}..{b.right*dbu:.3f} y:{b.bottom*dbu:.3f}..{b.top*dbu:.3f}")

# m1 along planned finger + west of it
clipdump(34, 0, 16.5, 16.9, 20.7, 18.6, 'm1')
# m2 along planned leg1 (y 17.4..18.0) from x 3.0 to 18.5
clipdump(36, 0, 3.0, 17.2, 18.6, 18.1, 'm2')
# m2 along leg2 corridor x 3.2..3.8 full height
clipdump(36, 0, 3.1, -3.0, 3.9, 18.0, 'm2')
# m2 along leg3 corridor y -2.4..-1.9
clipdump(36, 0, -11.5, -2.5, 3.9, -1.8, 'm2')
# m1 spacing check around leg endpoints: junction block area
clipdump(34, 0, -11.6, -3.6, -10.0, -1.4, 'm1')
