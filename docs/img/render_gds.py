# Headless GDS -> PNG renderer (run inside the IIC-OSIC-TOOLS container):
#   klayout -z -nc -r docs/img/render_gds.py -rd gds=<path> -rd out=<path> [-rd cell=<top>]
# Uses the gf180mcu layer properties for true PDK colors.
import pya

lv = pya.LayoutView()
cv = lv.load_layout(gds, 0)
lv.load_layer_props("/foss/pdks/gf180mcuD/libs.tech/klayout/tech/gf180mcu.lyp")
try:
    if "cell" in globals() and cell:
        lv.active_cellview().cell = lv.active_cellview().layout().cell(cell)
except Exception:
    pass
lv.max_hier_levels = 30
lv.zoom_fit()
lv.set_config("background-color", "#ffffff")
lv.set_config("grid-visible", "false")
lv.save_image(out, 1600, 1600)
print("saved", out)
