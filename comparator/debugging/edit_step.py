"""Generic single-step editor: pass step name as argv[1]."""
import sys
import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()
dbu = layout.dbu

def box(x1, y1, x2, y2):
    return db.Box(int(round(x1/dbu)), int(round(y1/dbu)), int(round(x2/dbu)), int(round(y2/dbu)))

def erase_top_m1(x1, y1, x2, y2):
    """Erase given box from TOP-LEVEL metal1 shapes only (cells untouched)."""
    li = layout.layer(34, 0)
    moat = db.Region(box(x1, y1, x2, y2))
    existing = db.Region()
    for s in top.each_shape(li):
        if s.is_box() or s.is_polygon() or s.is_path():
            existing.insert(s.polygon)
    new = existing - moat
    top.shapes(li).clear()
    for p in new.each():
        top.shapes(li).insert(p)

def add(l, d, x1, y1, x2, y2):
    top.shapes(layout.layer(l, d)).insert(box(x1, y1, x2, y2))

step = sys.argv[1]

if step == 'junction_notch':
    erase_top_m1(-11.72, -2.85, -11.36, -2.49)

elif step == 'neck_restore':
    add(34, 0, -10.300, -6.000, -10.040, -5.000)

elif step == 'm5_bridge':
    add(34, 0, 28.70, 17.35, 29.30, 17.95)

elif step == 'm6_head_cut':
    erase_top_m1(-29.36, 17.68, -28.52, 17.99)

elif step == 'm6_drain_m2':
    # via1 on M6 drain piece + m2 route east to M2's gate pad (VOUT2) + via1 down
    add(35, 0, -28.84, 18.05, -28.58, 18.31)          # via on drain piece
    add(36, 0, -28.90, 17.99, -28.52, 18.37)          # m2 via pad
    add(36, 0, -28.58, 18.05, -27.60, 18.35)          # m2 east jog
    add(36, 0, -27.90, 16.65, -27.60, 18.35)          # m2 south leg
    add(36, 0, -27.90, 16.65, -6.94, 16.95)           # m2 long east wire
    add(36, 0, -7.24, 16.65, -6.94, 17.87)            # m2 up jog at east end
    add(36, 0, -7.16, 17.49, -6.78, 17.87)            # m2 via pad over M2 gate pad
    add(35, 0, -7.10, 17.55, -6.84, 17.81)            # via down to M2 gate pad m1 (VOUT2)

elif step == 'm6_ntap_m2':
    # via on ntap-side piece, m2 jog west, vertical north, top jog east,
    # via onto M6's own VDD pad piece (-29.24..-28.83, 19.13..19.51)
    add(35, 0, -29.30, 17.31, -29.04, 17.57)          # via on ntap piece
    add(36, 0, -29.94, 17.25, -28.98, 17.63)          # m2 bottom jog west
    add(36, 0, -29.94, 17.25, -29.64, 19.51)          # m2 vertical north
    add(36, 0, -29.94, 19.13, -28.84, 19.51)          # m2 top jog east
    add(35, 0, -29.16, 19.19, -28.90, 19.45)          # via onto VDD pad piece

elif step == 'm4_col2_vdd':
    add(34, 0, 20.33, 18.95, 20.53, 19.46)            # strap $2 col2 pad to its ntap/VDD pad

elif step == 'm4_col1_divorce':
    erase_top_m1(20.01, 17.30, 21.10, 18.14)

elif step == 'm4_col1_net3':
    # m1 finger west from col1 pad (thin under gate pad, thick further west),
    # via1 up to m2, long m2 route (west, south, west) to NET3 junction block
    add(34, 0, 19.31, 17.53, 20.24, 17.86)            # m1 neck under gate pad (0.23 gap to it)
    add(34, 0, 17.89, 17.53, 19.31, 17.91)            # m1 thick finger west
    add(35, 0, 17.99, 17.59, 18.25, 17.85)            # via1 m1->m2
    add(36, 0, 17.93, 17.53, 18.31, 17.91)            # m2 via pad
    add(36, 0, 3.35, 17.53, 18.31, 17.83)             # m2 leg1 west
    add(36, 0, 3.35, -2.32, 3.65, 17.83)              # m2 leg2 south
    add(36, 0, -11.06, -2.32, 3.65, -1.94)            # m2 leg3 west
    add(35, 0, -11.00, -2.26, -10.74, -2.00)          # via1 down into NET3 junction block

elif step == 'm3_gate_ck':
    # via on CK stub, m2 north along x~-19.3, m2 east above VDD m2 wire, via onto M3 gate pad
    add(35, 0, -19.43, 17.72, -19.17, 17.98)          # via on CK m1 stub
    add(36, 0, -19.45, 17.66, -19.15, 20.27)          # m2 north leg
    add(36, 0, -19.45, 19.89, -16.75, 20.27)          # m2 east leg (0.28 above VDD m2)
    add(35, 0, -17.07, 19.95, -16.81, 20.21)          # via onto M3 gate pad m1

elif step == 'm3_ntap_vdd':
    # via on M3 ntap pad, short m2 north merging into existing VDD m2 wire
    add(35, 0, -16.37, 18.66, -16.11, 18.92)          # via on ntap pad
    add(36, 0, -16.43, 18.60, -16.05, 19.61)          # m2 vertical, merges with VDD m2 wire

else:
    raise SystemExit(f"unknown step {step}")

layout.write(GDS)
print(f"step {step} applied")
