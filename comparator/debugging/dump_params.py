import klayout.db as db

l2n = db.LayoutVsSchematic()
l2n.read('/foss/designs/comparator/layout/klayout_lvs_run_TMP/strongarm_lvs.lvsdb')

for label, nl in (('LAYOUT', l2n.netlist()), ('REFERENCE', l2n.reference)):
    print(f"== {label} ==")
    for circuit in nl.each_circuit():
        for dev in circuit.each_device():
            dc = dev.device_class()
            params = {pd.name: dev.parameter(pd.id()) for pd in dc.parameter_definitions()}
            core = {k: v for k, v in params.items() if k in ('W', 'L', 'AS', 'AD', 'PS', 'PD', 'NF', 'M')}
            print(f"  {dev.expanded_name():4s} class={dc.name:16s} {core}")
