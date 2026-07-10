import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
dbu = layout.dbu

nfet = None
for c in layout.each_cell():
    if c.name == 'nfet':
        nfet = c
assert nfet is not None

ct_li = layout.layer(33, 0)
to_delete = []
for s in nfet.each_shape(ct_li):
    b = s.bbox()
    # tap contacts: x:1.470..1.690 in cell-local coords
    if b.left * dbu > 1.4:
        to_delete.append(s)

print(f"deleting {len(to_delete)} tap contacts from nfet cell def:")
for s in to_delete:
    b = s.bbox()
    print(f"  x:{b.left*dbu:.3f}..{b.right*dbu:.3f} y:{b.bottom*dbu:.3f}..{b.top*dbu:.3f}")

assert len(to_delete) == 3, f"expected exactly 3, got {len(to_delete)}"
for s in to_delete:
    nfet.shapes(ct_li).erase(s)

layout.write(GDS)
print("written", GDS)
