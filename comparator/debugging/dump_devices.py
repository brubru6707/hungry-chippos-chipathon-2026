import klayout.db as db

l2n = db.LayoutVsSchematic()
l2n.read('/foss/designs/comparator/layout/klayout_lvs_run_TMP/strongarm_lvs.lvsdb')
netlist = l2n.netlist()

for circuit in netlist.each_circuit():
    print(f"=== circuit {circuit.name} ===")
    for dev in circuit.each_device():
        terms = {}
        for td in dev.device_class().terminal_definitions():
            net = dev.net_for_terminal(td.id())
            terms[td.name] = net.expanded_name() if net is not None else "<none>"
        pos = dev.trans.disp
        print(f"{dev.expanded_name():6s} {dev.device_class().name:10s} "
              f"pos=({pos.x:.3f},{pos.y:.3f}) "
              f"D={terms.get('D','?'):8s} G={terms.get('G','?'):8s} "
              f"S={terms.get('S','?'):8s} B={terms.get('B','?'):8s}")
