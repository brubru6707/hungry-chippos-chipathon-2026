#!/usr/bin/env python3
"""DRC fix batches for strongarm.gds. Usage: drc_fix.py <group1|group2|group3>

All coordinates derived from drc_recon{,2,3}.py dumps of the LVS-clean file
(md5 609af8d558b5e5d75882b06f1d6af86d). Rules targeted:
M1.1 (m1 width 0.23), M1.2a (m1 space 0.23), M2.1 (m2 width 0.28),
V1.1 (via1 exactly 0.26x0.26), V1.3a/c (m1 cover / EOL 0.06 over via1),
V1.4a/b (m2 overlap 0.01 / EOL 0.06 over via1).
"""
import sys
import klayout.db as db

GDS = '/foss/designs/comparator/layout/strongarm.gds'
layout = db.Layout()
layout.read(GDS)
top = layout.top_cell()
dbu = layout.dbu

M1 = layout.layer(34, 0)
VIA1 = layout.layer(35, 0)
M2 = layout.layer(36, 0)

def box(x1, y1, x2, y2):
    return db.Box(int(round(x1/dbu)), int(round(y1/dbu)), int(round(x2/dbu)), int(round(y2/dbu)))

def erase_top(li, x1, y1, x2, y2):
    """Boolean-subtract box from TOP-LEVEL shapes on layer li (cells untouched)."""
    moat = db.Region(box(x1, y1, x2, y2))
    existing = db.Region()
    for s in top.each_shape(li):
        if s.is_box() or s.is_polygon() or s.is_path():
            existing.insert(s.polygon)
    new = existing - moat
    top.shapes(li).clear()
    for p in new.each():
        top.shapes(li).insert(p)

def add(li, x1, y1, x2, y2):
    top.shapes(li).insert(box(x1, y1, x2, y2))

group = sys.argv[1]

if group == 'group1':
    # -- dangling vias (no m1, no m2 anywhere over them; confirmed floating) --
    erase_top(VIA1, -3.26, 19.44, -3.00, 19.70)   # V1.3a/V1.4a
    erase_top(VIA1, -4.05, 19.67, -3.79, 19.93)   # V1.3a/V1.4a
    erase_top(VIA1, 11.56, -1.59, 11.82, -1.33)   # V1.3a/V1.4a
    # -- floating m1 stub island at x15.24 + its dead-end via --
    erase_top(VIA1, 15.25, 0.55, 15.51, 0.81)     # V1.3c/V1.4a
    erase_top(M1, 15.24, -1.63, 15.54, 0.84)      # M1.2a (0.10 gap to gate stub)
    # -- M9 gate via 0.26x0.28 -> 0.26x0.26 (trim top 0.02) --
    erase_top(VIA1, -9.72, 4.78, -9.46, 4.80)     # V1.1
    # -- M6 drain via exceeded m1 top by 0.03: shift down --
    erase_top(VIA1, -28.84, 18.05, -28.58, 18.31)
    add(VIA1, -28.84, 18.01, -28.58, 18.27)       # V1.3a; m1 17.99..18.28, m2 pad 17.99..18.37
    # -- m1 EOL 0.06 over VOUT2 via at x-5.15 (m1 pad topped out at 4.87) --
    add(M1, -5.305, 4.80, -5.005, 4.89)           # V1.3c
    # -- M3 source route rework: vias were 0.10x0.18, m2 wire 0.18 wide --
    erase_top(VIA1, -18.56, 19.43, -18.46, 19.61)
    erase_top(VIA1, -16.35, 19.43, -16.25, 19.61)
    erase_top(M2, -18.61, 19.43, -16.43, 19.61)
    add(VIA1, -18.64, 19.34, -18.38, 19.60)       # V1.1; on VDD trunk m1 -18.66..-18.36
    add(VIA1, -16.37, 19.34, -16.11, 19.60)       # V1.1; on source pad m1 -16.43..-16.05 y19.33..19.71
    add(M2, -18.70, 19.33, -16.05, 19.61)         # M2.1/V1.4a/V1.4b; 0.28 gap to CK m2 above
    # -- V1.4b m2 EOL extensions (m2 fell 0.03-0.04 short of via+0.06) --
    add(M2, 19.81, 18.13, 19.87, 18.43)
    add(M2, 21.83, 18.24, 22.13, 18.30)
    add(M2, 28.09, 18.44, 28.15, 18.74)
    add(M2, 30.11, 18.56, 30.41, 18.62)

elif group == 'group2':
    # -- M1 gate: 0.66um corridor cannot hold a legal m1 wire; reroute on m2 --
    erase_top(M1, 11.32, 0.55, 14.76, 0.84)       # remove bridge (M1.2a x2), keep trunk+stub
    add(VIA1, 10.98, 0.55, 11.24, 0.81)           # on VOUT1 trunk m1 10.90..11.32 x 0.53..1.15
    add(VIA1, 14.82, 0.54, 15.08, 0.80)           # on gate stub m1 14.76..15.14 x 0.48..0.86
    add(M2, 10.92, 0.53, 15.14, 0.82)             # 0.29 wide, EOL 0.06 both ends
    # -- M3 pocket: seg A 0.21 from VDD trunk -> trim west edge above y18.30 --
    erase_top(M1, -18.155, 18.30, -18.13, 20.835) # M1.2a
    # -- fill staircase throat at A/VOUT1-trunk junction --
    add(M1, -18.60, 17.24, -17.70, 17.52)         # M1.1 x2
    # -- seg B 0.18 above CK gate pad -> raise bottom to 20.50 --
    erase_top(M1, -17.70, 20.45, -16.43, 20.50)   # M1.2a

elif group == 'group3':
    # -- widen 0.20 m1 traces to 0.23 (side chosen where >=0.23 clear, verified) --
    add(M1, 3.29, -20.13, 3.52, -19.96)           # t1a east
    add(M1, 3.29, -18.46, 3.52, -15.84)           # t1b east
    add(M1, -10.30, -9.91, -10.07, -6.00)         # t2a west (aligns with neck fill)
    add(M1, -10.30, -5.00, -10.07, -3.44)         # t2b west
    add(M1, -10.30, -1.57, -10.07, -0.92)         # t2c west
    add(M1, -10.30, -1.15, -8.51, -0.92)          # t3 south (gap below stays 0.42)
    add(M1, -8.74, -1.15, -8.51, -0.33)           # t4 west
    add(M1, -26.24, 12.795, -24.14, 13.025)       # t5 north
    add(M1, -24.20, 12.795, -23.97, 17.90)        # t6 west
    add(M1, -24.20, 17.70, -19.49, 17.93)         # t7 north
    add(M1, 11.47, -8.31, 13.71, -8.08)           # t8 south
    add(M1, 13.48, -8.31, 13.51, -0.57)           # t9 west
    add(M1, 3.13, 18.81, 10.65, 19.04)            # t10 north
    add(M1, 20.53, 19.03, 20.56, 19.38)           # t11 (M4 strap) east
    add(M1, -38.17, 18.70, -29.94, 18.93)         # t12 north
    # -- same-polygon notch/slot fills (merged-region-verified same net) --
    add(M1, -7.37, 1.70, -7.30, 1.75)             # M1.2a R2 notch
    add(M1, 3.03, -12.37, 4.33, -12.22)           # M1.2a R3 slot
    # -- M5 bridge/pad staircase throat (0.20 diagonal) --
    add(M1, 28.52, 17.73, 28.90, 17.86)           # M1.1 x2

elif group == 'group4':
    # residual M1.1: opposite staircase steps at y-0.33 (t4 widen top met the
    # polygon's own east widening) leave a 0.20 diagonal throat; carry the
    # west widening up past the transition (west side verified empty)
    add(M1, -8.74, -0.33, -8.71, 0.00)

else:
    raise SystemExit(f"unknown group {group}")

layout.write(GDS)
print(f"{group} applied")
