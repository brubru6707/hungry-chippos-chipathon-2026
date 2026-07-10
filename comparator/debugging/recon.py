import klayout.db as db

l2n = db.LayoutVsSchematic()
l2n.read('/foss/designs/comparator/layout/klayout_lvs_run_TMP/strongarm_lvs.lvsdb')
netlist = l2n.netlist()
top_c = None
for c in netlist.each_circuit():
    top_c = c
dbu = l2n.internal_layout().dbu

# find the metal1 layer index by matching a known VOUT2 m1 bbox
# from earlier: layer idx 14 was metal1, idx 16 metal2, idx 15 via1, idx 9 contact
M1_LI, VIA1_LI, M2_LI, CT_LI = 14, 15, 16, 9

def show_net(name, li, label):
    net = top_c.net_by_name(name)
    if net is None:
        print(f"{name}: no such net")
        return
    r = l2n.shapes_of_net(net, l2n.layer_by_index(li), True)
    r.merge()
    print(f"\n{name} on {label}: {r.count()} islands")
    for p in r.each():
        b = p.bbox()
        print(f"   x:{b.left*dbu:.3f}..{b.right*dbu:.3f} y:{b.bottom*dbu:.3f}..{b.top*dbu:.3f}")

for n in ('VSS', 'VDD', '$7', '$22', '$19', '$8', '$3', 'VOUT2', 'CK'):
    show_net(n, M1_LI, 'metal1')

show_net('VOUT2', M2_LI, 'metal2')
show_net('VDD', M2_LI, 'metal2')
show_net('VSS', M2_LI, 'metal2')

# island 15 ($8 net) full polygon detail
net = top_c.net_by_name('$8')
r = l2n.shapes_of_net(net, l2n.layer_by_index(M1_LI), True)
r.merge()
print("\n$8 (island15) polygon vertices:")
for p in r.each():
    pts = [f"({pt.x*dbu:.2f},{pt.y*dbu:.2f})" for pt in p.each_point_hull()]
    print("  ", " ".join(pts))
