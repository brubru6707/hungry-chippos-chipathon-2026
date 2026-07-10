import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()
dbu = layout.dbu

print(f"top cell: {top.name}")
print("cells:", [layout.cell(i).name for i in layout.each_cell_top_down()][:20])

# ptap contact locations (top-cell coords, from earlier census)
ptap_boxes = [
    # M11
    (5.070, -15.760, 5.290, -15.540), (5.070, -15.250, 5.290, -15.030), (5.070, -14.740, 5.290, -14.520),
    # M8
    (9.000, -8.800, 9.220, -8.580), (9.000, -8.290, 9.220, -8.070), (9.000, -7.780, 9.220, -7.560),
    # M10
    (-5.090, -8.780, -4.870, -8.560), (-5.090, -8.270, -4.870, -8.050), (-5.090, -7.760, -4.870, -7.540),
    # M9
    (-8.620, 1.120, -8.400, 1.340), (-8.110, 1.120, -7.890, 1.340), (-7.600, 1.120, -7.380, 1.340),
    # M1
    (12.850, 1.810, 13.070, 2.030), (13.360, 1.810, 13.580, 2.030), (13.870, 1.810, 14.090, 2.030),
    # dummy
    (8.250, 6.880, 8.470, 7.100), (8.760, 6.880, 8.980, 7.100), (9.270, 6.880, 9.490, 7.100),
]

ct_li = layout.layer(33, 0)

# for each ptap contact box, walk the recursive shape iterator and report which cell owns the shape
for (x1, y1, x2, y2) in ptap_boxes[:3] + ptap_boxes[9:12] + ptap_boxes[12:15]:
    bx = db.Box(int(x1/dbu), int(y1/dbu), int(x2/dbu), int(y2/dbu))
    it = top.begin_shapes_rec_overlapping(ct_li, bx)
    owners = set()
    while not it.at_end():
        owners.add(it.cell().name)
        it.next()
    print(f"contact at ({x1},{y1})..({x2},{y2}): owned by cells {owners}")

# also: describe the nfet cell content layer by layer
for cell in layout.each_cell():
    if cell.name != top.name and 'fet' in cell.name.lower() or cell.name.startswith('nfet') or cell.name.startswith('pfet'):
        pass

# list all cells and their instance counts in top
from collections import Counter
cnt = Counter()
for inst in top.each_inst():
    cnt[inst.cell.name] += 1
print("\ninstances in top:", dict(cnt))
