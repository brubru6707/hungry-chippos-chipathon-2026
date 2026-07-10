import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()
dbu = layout.dbu

def box(x1, y1, x2, y2):
    return db.Box(int(round(x1/dbu)), int(round(y1/dbu)), int(round(x2/dbu)), int(round(y2/dbu)))

# new substrate tap under VSS metal1 lobe (x:3.49..4.85, y:-19.96..-18.46), empty silicon
top.shapes(layout.layer(22, 0)).insert(box(3.93, -19.45, 4.41, -18.97))   # COMP 0.48x0.48
top.shapes(layout.layer(31, 0)).insert(box(3.77, -19.61, 4.57, -18.81))   # Pplus 0.16 enclosure
top.shapes(layout.layer(33, 0)).insert(box(4.06, -19.32, 4.28, -19.10))   # contact 0.22

layout.write(GDS)
print("VSS tap added")
