import klayout.db as db

l2n = db.LayoutVsSchematic()
l2n.read('/foss/designs/comparator/layout/klayout_lvs_run_TMP/strongarm_lvs.lvsdb')
xref = l2n.xref()

def net_desc(n):
    if n is None:
        return "-none-"
    terms = list(n.each_terminal())
    pins = list(n.each_pin())
    return f"{n.expanded_name()}(terms={len(terms)},pins={len(pins)})"

for cp in xref.each_circuit_pair():
    print(f"circuit pair: status={cp.status()}")
    for npair in xref.each_net_pair(cp):
        a, b = npair.first(), npair.second()
        print(f"  L:{net_desc(a):26s} R:{net_desc(b):26s} status={npair.status()}")
    for dpair in xref.each_device_pair(cp):
        a, b = dpair.first(), dpair.second()
        an = a.expanded_name() if a else "-none-"
        bn = b.expanded_name() if b else "-none-"
        print(f"  DEV L:{an:8s} R:{bn:8s} status={dpair.status()}")
