# merge_comparator_2stage.py — build comparator_2stage.gds from the two
# verified bricks WITHOUT any PCell regeneration (batch mode keeps the
# frozen, DRC/LVS-verified geometry exactly as-is).
#
# Run (inside the container):
#   klayout -b -r /foss/designs/comparator_alt/layout/merge_comparator_2stage.py
#
# Result: /foss/designs/comparator_alt/layout/comparator_2stage.gds
#   top cell comparator_2stage containing one instance of each brick.
#   preamp_dyn at the origin, strongarm_2 60 um to its right as a starting
#   point — do the real placement (rail abutment, DIP/VIN facing) in the GUI
#   by moving the INSTANCES, not the cells' contents.

import pya

LAYDIR = "/foss/designs/comparator_alt/layout/"

lay = pya.Layout()
lay.dbu = 0.005  # match the PDK/brick database unit

# read both bricks into one database (cells merge into the tree; dbu-checked)
lay.read(LAYDIR + "preamp_dyn.gds")
lay.read(LAYDIR + "strongarm_2.gds")

pre = lay.cell("preamp_dyn")
sa  = lay.cell("strongarm_2")
assert pre is not None, "preamp_dyn cell not found after read!"
assert sa  is not None, "strongarm_2 cell not found after read!"

top = lay.create_cell("comparator_2stage")
top.insert(pya.DCellInstArray(pre.cell_index(), pya.DTrans(pya.DVector(0.0, 0.0))))
top.insert(pya.DCellInstArray(sa.cell_index(),  pya.DTrans(pya.DVector(60.0, 0.0))))

lay.write(LAYDIR + "comparator_2stage.gds")
print("wrote " + LAYDIR + "comparator_2stage.gds")
print("cells: " + ", ".join([c.name for c in lay.each_cell()][:10]) + " ...")
