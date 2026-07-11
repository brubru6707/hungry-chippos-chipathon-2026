import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
dbu = layout.dbu

for cellname in ('nfet', 'pfet'):
    cell = None
    for c in layout.each_cell():
        if c.name == cellname:
            cell = c
    print(f"\n===== cell {cellname} (bbox {cell.bbox().to_s()}) =====")
    for li in layout.layer_indexes():
        info = layout.get_info(li)
        shapes = list(cell.each_shape(li))
        if not shapes:
            continue
        print(f" layer {info}: {len(shapes)} shapes")
        for s in shapes:
            b = s.bbox()
            print(f"   x:{b.left*dbu:.3f}..{b.right*dbu:.3f} y:{b.bottom*dbu:.3f}..{b.top*dbu:.3f}"
                  + ("  TEXT:" + s.text_string if s.is_text() else ""))
