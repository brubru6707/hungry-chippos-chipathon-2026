import klayout.db as db

l2n = db.LayoutVsSchematic()
l2n.read('/foss/designs/comparator/layout/klayout_lvs_run_TMP/strongarm_lvs.lvsdb')
netlist = l2n.netlist()
top = None
for c in netlist.each_circuit():
    top = c
dbu = 0.005  # will read from internal layout below if available
try:
    dbu = l2n.internal_layout().dbu
except Exception:
    pass

net = top.net_by_name('VOUT2')
print(f"net: {net.expanded_name()}  dbu={dbu}")

for li in l2n.layer_indexes():
    name = l2n.layer_name(li)
    info = None
    try:
        info = l2n.internal_layout().get_info(li)
    except Exception:
        pass
    lyr = l2n.layer_by_index(li)
    if not isinstance(lyr, db.Region):
        continue
    region = l2n.shapes_of_net(net, lyr, True)
    if region is None or region.is_empty():
        continue
    region.merge()
    print(f"\n-- layer idx {li} name={name} info={info}: {region.count()} merged shapes")
    for p in region.each():
        b = p.bbox()
        print(f"   x:{b.left*dbu:.3f}..{b.right*dbu:.3f} y:{b.bottom*dbu:.3f}..{b.top*dbu:.3f}")
