import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()
dbu = layout.dbu

def merged(l, d):
    r = db.Region(top.begin_shapes_rec(layout.layer(l, d)))
    r.merge()
    return r

def fmt(b):
    return f"x:{b.left*dbu:.3f}..{b.right*dbu:.3f} y:{b.bottom*dbu:.3f}..{b.top*dbu:.3f}"

def clip(region, x1, y1, x2, y2):
    return region & db.Region(db.Box(int(x1/dbu), int(y1/dbu), int(x2/dbu), int(y2/dbu)))

m1 = merged(34, 0)
m2 = merged(36, 0)
via1 = merged(35, 0)
comp = merged(22, 0)
poly = merged(30, 0)
nwell = merged(21, 0)
pplus = merged(31, 0)
nplus = merged(32, 0)

# 1. emptiness check for new ptap: region south of nfets, under VSS m1
print("== candidate new-tap area (2.9..5.1, -20.3..-16.5): occupancy ==")
for name, r in (('comp', comp), ('poly', poly), ('nwell', nwell), ('pplus', pplus), ('nplus', nplus), ('m1', m1)):
    c = clip(r, 2.9, -20.3, 5.1, -16.5)
    print(f"  {name}: {c.count()} shapes", [fmt(p.bbox()) for p in c.each()][:6])

# VSS m1 polygon detail
print("\n== VSS m1 polygon (island containing (4.0,-18)) ==")
for p in m1.each():
    if p.bbox().contains(db.Point(int(4.0/dbu), int(-18.0/dbu))):
        pts = [f"({pt.x*dbu:.2f},{pt.y*dbu:.2f})" for pt in p.each_point_hull()]
        print("  ", " ".join(pts))

# 2. $7 (net1) island near $19 pad
print("\n== m1 near (28.3..29.5, 16.8..18.5) ==")
for p in clip(m1, 28.0, 16.5, 29.6, 19.2).each():
    print("  ", fmt(p.bbox()))

# 3. island 17 (VOUT2) geometry near $2's strapped contact (20.32..20.54, 17.61..17.83)
print("\n== m1 near (19.5..21.5, 16.8..19.2) ==")
for p in clip(m1, 19.5, 16.8, 21.5, 19.2).each():
    pts = [f"({pt.x*dbu:.2f},{pt.y*dbu:.2f})" for pt in p.each_point_hull()]
    print("  ", " ".join(pts))

# 4. VDD rail polygon near M6 head (x -30..-28, y 17.9..19)
print("\n== m1 near M6 head (-30.2..-27.9, 17.0..19.5) ==")
for p in clip(m1, -30.2, 17.0, -27.9, 19.5).each():
    pts = [f"({pt.x*dbu:.2f},{pt.y*dbu:.2f})" for pt in p.each_point_hull()]
    print("  ", " ".join(pts))

# 5. full m2 + via1 census
print("\n== ALL m2 islands ==")
for p in m2.each():
    print("  ", fmt(p.bbox()))
print("== ALL via1 ==")
for p in via1.each():
    print("  ", fmt(p.bbox()))

# 6. nfet instance transforms (to find dummy)
print("\n== nfet/pfet instances ==")
for inst in top.each_inst():
    t = inst.dcplx_trans
    print(f"  {inst.cell.name}: disp=({t.disp.x:.3f},{t.disp.y:.3f}) rot={t.angle} mirror={t.is_mirror()}")
