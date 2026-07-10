import klayout.db as db
l2n = db.LayoutVsSchematic()
l2n.read("/foss/designs/comparator/layout/klayout_lvs_run_TMP/strongarm_lvs.lvsdb")
netlist = l2n.netlist()
top_c = None
for c in netlist.each_circuit():
    top_c = c
dbu = l2n.internal_layout().dbu
net = top_c.net_by_name("VDD")
r = l2n.shapes_of_net(net, l2n.layer_by_index(14), True)
r.merge()
w = r & db.Region(db.Box(int(-30.9/dbu), int(17.5/dbu), int(-28.4/dbu), int(20.5/dbu)))
print("VDD m1 in window (-30.9..-28.4, 17.5..20.5):")
for p in w.each():
    pts = [f"({pt.x*dbu:.2f},{pt.y*dbu:.2f})" for pt in p.each_point_hull()]
    print("  ", " ".join(pts))
