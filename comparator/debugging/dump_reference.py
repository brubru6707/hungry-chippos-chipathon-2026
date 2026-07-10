import klayout.db as db

l2n = db.LayoutVsSchematic()
l2n.read('/foss/designs/comparator/layout/klayout_lvs_run_TMP/strongarm_lvs.lvsdb')
ref = l2n.reference

for circuit in ref.each_circuit():
    print(f"=== reference circuit {circuit.name} ===")
    for dev in circuit.each_device():
        terms = {}
        for td in dev.device_class().terminal_definitions():
            net = dev.net_for_terminal(td.id())
            terms[td.name] = net.expanded_name() if net is not None else "<none>"
        print(f"{dev.expanded_name():6s} {dev.device_class().name:12s} "
              f"D={terms.get('D','?'):8s} G={terms.get('G','?'):8s} "
              f"S={terms.get('S','?'):8s} B={terms.get('B','?'):8s}")
