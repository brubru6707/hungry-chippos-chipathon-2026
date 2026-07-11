**Describe the bug**
Running LVS via the KLayout GUI menu action (Tools → gf180mcu PDK → Run KLayout LVS, from gf180mcu_lvs.lylvs) reports a netlist mismatch (a false short between two nets) on a layout that is verified LVS-clean when checked via the documented CLI flow (run_lvs.py, from the same PDK). Both runs use the exact same .gds and .spice files and the same effective settings (confirmed via the GUI's own cached lvs_options.yml), yet only the GUI path fails. Re-running after File → Reload doesn't change the result, ruling out a stale in-memory layout.

Root cause as far as I could trace it: in libs.tech/klayout/tech/lvs/gf180mcu.lvs, the CLI wrapper (run_lvs.py) always sets $input, forcing source($input) to freshly re-read the GDS from disk. The GUI macro (gf180mcu_lvs.lylvs) never sets $input and instead relies on KLayout's implicit "current active view" as the layout source. I confirmed the on-disk file and the GUI's already-open view are byte-identical (matching polygon counts on the COMP layer, 45 merged polygons both ways). Something about extracting from the active view vs. an explicitly re-sourced layout produces a different (incorrect) result even for identical geometry.

Note: this is not a universal failure. A simple test circuit (single inverter) passes cleanly both ways, GUI and CLI. It reproduces specifically on this hierarchical, 11-device layout (two subcell PCell types instantiated separately, plus explicit substrate/tap geometry) — not on a trivial flat circuit with no substrate taps to reconcile.

**To Reproduce**
Here are the files:
- Spice: https://github.com/brubru6707/hungry-chippos-chipathon-2026/blob/main/comparator/schematic/strongarm.spice
- GDS: https://github.com/brubru6707/hungry-chippos-chipathon-2026/blob/main/comparator/layout/strongarm.gds

Terminal command (passes clean):
```bash
docker exec f53d67a84b8b bash -lc '
LVS_RUN_DIR=/foss/designs/comparator/layout/klayout_lvs_run
mkdir -p "$LVS_RUN_DIR"
cp /foss/designs/comparator/schematic/strongarm.spice "$LVS_RUN_DIR/strongarm_lvs.spice"
cp /foss/designs/comparator/layout/strongarm.gds "$LVS_RUN_DIR/strongarm.gds"
cd "$LVS_RUN_DIR"
python3 /foss/designs/designs/scripts/lvs_strip_gds_labels.py strongarm.gds
python /foss/pdks/gf180mcuD/libs.tech/klayout/tech/lvs/run_lvs.py \
  --layout=strongarm_lvs.gds \
  --netlist=strongarm_lvs.spice \
  --variant=D \
  --run_dir=. \
  --topcell=strongarm \
  --lvs_sub=VSS \
  --run_mode=flat \
  --schematic_simplify \
  --top_lvl_pins
'
```

GUI steps (fails):
1. Open the .gds in the KLayout GUI.
2. Go to Tools → gf180mcu PDK → Run KLayout LVS with sub_name=vss, run_mode=flat, variant=D, simplify=false, top_lvl_pins=true, purge_nets=true, schematic_translate=false.
3. Observe `ERROR: Netlists don't match`, with every net/device flagged and two nets that should be distinct merged into one.

**Expected behavior**
The GUI LVS run should match the CLI run_lvs.py result (Congratulations! Netlists match.) for the same layout/netlist/settings, since it's meant to be the same underlying rule deck (gf180mcu.lvs).

**Screenshots**
xxxxx

**Environment:**
- OS: macOS (host), Ubuntu 24.04 (container)
- Operating mode: VNC (Xvnc/noVNC, DISPLAY=:1)
- Version tag: 2026.04 (hpretl/iic-osic-tools:chipathon26, KLayout 0.30.8)

**Additional context**
Two file paths inside the PDK that I think show the bug. In the first file, $input forces a fresh source(), and if $input is not set, it falls through to whatever RBA::CellView.active already has loaded. In the second file (the entire GUI macro), it sets several options ($schematic, $lvs_sub, $run_mode, $topcell, etc., lines 64–114) but never sets $input anywhere before including gf180mcu.lvs on line 117.

`/foss/pdks/gf180mcuD/libs.tech/klayout/tech/lvs/gf180mcu.lvs`
```ruby
    80	logger.info("Starting running GF180MCU Klayout LVS runset on #{$input}")
    81	logger.info("Ruby Version for klayout: #{RUBY_VERSION}")
    82	
    83	if $input
    84	  if $topcell
    85	    source($input, $topcell)
    86	  else
    87	    source($input)
    88	  end
    89	end
    90	
    91	logger.info('Loading database to memory is complete.')
    92	
    93	if $report
    94	  logger.info("GF180MCU Klayout LVS runset output at: #{$report}")
    95	  report_lvs($report)
    96	else
    97	  layout_dir = Pathname.new(RBA::CellView.active.filename).parent.realpath
    98	  report_path = layout_dir.join("#{source.cell_name}.lvsdb").to_s
```

`/foss/pdks/ciel/gf180mcu/versions/7b70722e33c03fcb5dabcf4d479fb0822d9251c9/gf180mcuD/libs.tech/klayout/tech/macros/gf180mcu_lvs.lylvs`
```ruby
     1	<?xml version="1.0" encoding="utf-8"?>
     2	<klayout-macro>
     3	 <description>Run Klayout LVS</description>
     4	 <version>0.1</version>
     5	 <category>lvs</category>
     6	 <prolog/>
     7	 <epilog/>
     8	 <doc/>
     9	 <autorun>false</autorun>
    10	 <autorun-early>false</autorun-early>
    11	 <priority>0</priority>
    12	 <shortcut/>
    13	 <show-in-menu>true</show-in-menu>
    14	 <group-name/>
    15	 <menu-path>submenu&gt;end("gf180mcu PDK").end</menu-path>
    16	 <interpreter>dsl</interpreter>
    17	 <dsl-interpreter-name>lvs-dsl-xml</dsl-interpreter-name>
    18	 <text>
    19	# Copyright 2022 GlobalFoundries PDK Authors
    20	#
    21	# Licensed under the Apache License, Version 2.0 (the "License");
    22	# you may not use this file except in compliance with the License.
    23	# You may obtain a copy of the License at
    24	#
    25	#     https://www.apache.org/licenses/LICENSE-2.0
    26	#
    27	# Unless required by applicable law or agreed to in writing, software
    28	# distributed under the License is distributed on an "AS IS" BASIS,
    29	# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    30	# See the License for the specific language governing permissions and
    31	# limitations under the License.
    32	
    33	
    34	require 'yaml'
    35	# For some reason klayout messes with the __dir__ path, so it is necessary
    36	# to use this workaround instead of
    37	# require_relative "options_helper"
    38	require File.expand_path("options_helper", File.dirname(__FILE__))
    39	
    40	## reading the loaded gds file path
    41	layout_path = Pathname.new(RBA::CellView.active.filename)
    42	
    43	options = get_option_lvs()
    44	
    45	## reading netlist option to get netlist_path
    46	if options["netlist"] == ""
    47	    net_name = layout_path.split()[1].to_s().split(".")[0]
    48	
    49	    net_dir = "#{layout_path.split()[0]}/#{net_name}.cdl"
    50	    unless File.exist?net_dir
    51	      net_dir = "#{layout_path.split()[0]}/#{net_name}.spice"
    52	    end
    53	else
    54	    # Interpret schematic relative to layout file
    55	    net_dir = File.expand_path(options["netlist"], File.dirname(layout_path))
    56	end
    57	
    58	unless File.exist?net_dir
    59	  STDERR.puts "netlist file #{net_dir} doesn't exist"
    60	  exit
    61	end
    62	
    63	## passing options to lvs run file
    64	$schematic = net_dir
    65	
    66	$lvs_sub = options["sub_name"]
    67	
    68	$run_mode = options["run_mode"]
    69	
    70	if options["variant"] == "A"
    71	  $metal_top = "30K"
    72	  $metal_level = "3LM"
    73	  $mim_option = "A"
    74	elsif options["variant"] == "B"
    75	  $metal_top = "11K"
    76	  $metal_level = "4LM"
    77	  $mim_option = "B"
    78	elsif options["variant"] == "C"
    79	  $metal_top = "9K"
    80	  $metal_level = "5LM"
    81	  $mim_option = "B"
    82	elsif options["variant"] == "D"
    83	  $metal_top = "11K"
    84	  $metal_level = "5LM"
    85	  $mim_option = "B"
    86	end
    87	
    88	unless options["top_cell_name"] == ""
    89	  $topcell = options["top_cell_name"]
    90	end
    91	
    92	$spice_net_names = options["spice_net"]
    93	
    94	$spice_comments = options["spice_comment"]
    95	
    96	$scale = options["scale"]
    97	
    98	$verbose = options["verbose"]
    99	
    100	$simplify = options["simplify"]
    101	
    102	$net_only = options["net_only"]
    103	
    104	$top_lvl_pins = options["top_lvl_pins"]
    105	
    106	$combine = options["combine"]
    107	
    108	$purge = options["purge"]
    109	
    110	$purge_nets = options["purge_nets"]
    111	
    112	$implicit_connect = options["implicit_connect"]
    113	
    114	$schematic_translate = options["schematic_translate"]
    115	
    116	## include lvs run file
    117	#%include ../lvs/gf180mcu.lvs
    118	
    119	</text>
    120	</klayout-macro>
```
