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

m1 = merged(34, 0)
m2 = merged(36, 0)
via1 = merged(35, 0)
contact = merged(33, 0)

m1_islands = [p for p in m1.each()]
m2_islands = [p for p in m2.each()]

def bbox_um(p):
    b = p.bbox()
    return (b.left*dbu, b.bottom*dbu, b.right*dbu, b.top*dbu)

def fmt(p):
    x1, y1, x2, y2 = bbox_um(p)
    return f"x:{x1:.3f}..{x2:.3f} y:{y1:.3f}..{y2:.3f}"

print(f"metal1 islands: {len(m1_islands)}, metal2 islands: {len(m2_islands)}, via1 shapes: {via1.count()}")

# map each via1 shape to the m1 island and m2 island it touches
via_edges = []
for v in via1.each():
    vr = db.Region(v)
    m1_hit = [i for i, p in enumerate(m1_islands) if not (db.Region(p) & vr).is_empty()]
    m2_hit = [i for i, p in enumerate(m2_islands) if not (db.Region(p) & vr).is_empty()]
    via_edges.append((v, m1_hit, m2_hit))

# find the blob island: bbox approx x:-29.360..-7.300 y:-5.000..18.390
blob_idx = None
for i, p in enumerate(m1_islands):
    x1, y1, x2, y2 = bbox_um(p)
    if abs(x1 - (-29.360)) < 0.5 and abs(y2 - 18.390) < 0.5 and x2 < 0:
        blob_idx = i
        break
print(f"\nblob m1 island index: {blob_idx}  bbox {fmt(m1_islands[blob_idx]) if blob_idx is not None else 'NOT FOUND'}")

if blob_idx is None:
    # fall back: print all islands with bbox area > 20 um2 for manual id
    for i, p in enumerate(m1_islands):
        x1, y1, x2, y2 = bbox_um(p)
        if (x2-x1)*(y2-y1) > 20:
            print(f"  island {i}: {fmt(p)}")
    raise SystemExit

# vias touching the blob
print("\nvia1 shapes touching blob island, and the m2 island each connects to:")
for v, m1_hit, m2_hit in via_edges:
    if blob_idx in m1_hit:
        print(f"  via {fmt(v)}")
        for j in m2_hit:
            print(f"    -> m2 island {j}: {fmt(m2_islands[j])}")
            # what other m1 islands does this m2 island reach via other vias?
            for v2, m1h2, m2h2 in via_edges:
                if j in m2h2 and v2 is not v:
                    others = [k for k in m1h2 if k != blob_idx]
                    for k in others:
                        print(f"       m2 also vias down at {fmt(v2)} to m1 island {k}: {fmt(m1_islands[k])}")

# contacts under the blob within the wide-strap band y:-3.6..-2.0
print("\ncontacts intersecting blob island in band y:-3.6..-2.0:")
band = db.Region(db.Box(int(-30/dbu), int(-3.6/dbu), int(-7/dbu), int(-2.0/dbu)))
blob_r = db.Region(m1_islands[blob_idx])
cts = contact & blob_r & band
for c in cts.each():
    print(f"  contact {fmt(c)}")

# also: all contacts on the blob anywhere (to see every down-connection)
print(f"\nall contacts intersecting blob island: {(contact & blob_r).count()} shapes")
for c in (contact & blob_r).merged().each():
    print(f"  {fmt(c)}")
