import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()

targets = []
for inst in top.each_inst():
    t = inst.dcplx_trans
    if inst.cell.name == 'nfet' and abs(t.disp.x - 7.870) < 0.01 and abs(t.disp.y - 5.410) < 0.01:
        targets.append(inst)

assert len(targets) == 1, f"expected 1 dummy instance, found {len(targets)}"
top.erase(targets[0])
layout.write(GDS)
print("dummy nfet instance deleted")
