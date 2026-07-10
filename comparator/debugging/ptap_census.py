import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()
dbu = layout.dbu

def merged(l, d):
    li = layout.layer(l, d)
    r = db.Region(top.begin_shapes_rec(li))
    r.merge()
    return r

comp = merged(22, 0)
pplus = merged(31, 0)
nplus = merged(32, 0)
nwell = merged(21, 0)
contact = merged(33, 0)
m1 = merged(34, 0)
dnwell = merged(12, 0)
lvpwell = merged(204, 0)

def fmt(b):
    return f"x:{b.left*dbu:.3f}..{b.right*dbu:.3f} y:{b.bottom*dbu:.3f}..{b.top*dbu:.3f}"

print("DNWELL shapes:")
for p in dnwell.each():
    print("  ", fmt(p.bbox()))
print("LVPWELL shapes:")
for p in lvpwell.each():
    print("  ", fmt(p.bbox()))
print("NWELL shapes:")
for p in nwell.each():
    print("  ", fmt(p.bbox()))

ptap = (comp & pplus) - nwell   # p+ tap regions in p-substrate / pwell
ntap = (comp & nplus) & nwell   # n+ tap in nwell

print(f"\nptap regions ({ptap.merged().count()}):")
for p in ptap.merged().each():
    print("  ", fmt(p.bbox()))

m1_islands = [p for p in m1.each()]

# contacts landing on ptap
ptap_contacts = contact & ptap
print(f"\nptap contacts: {ptap_contacts.count()}")
# group by m1 island
for i, isl in enumerate(m1_islands):
    hits = ptap_contacts & db.Region(isl)
    if not hits.is_empty():
        b = isl.bbox()
        print(f"\n m1 island {i} ({fmt(b)}) has {hits.count()} ptap contacts:")
        for c in hits.merged().each():
            print("    ", fmt(c.bbox()))
