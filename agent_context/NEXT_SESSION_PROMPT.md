# Prompt for next Claude session — INT-8 / Gate 5 chip-level assembly

Copy-paste everything below the line into a fresh Claude Code session started in the repo root.

---

Read PROGRESS.md first (2026-07-31 state). Branch `int-top-level` (pushed, PR it or branch from it)
closed INT-2…INT-7: pin contracts (`docs/pin_contracts.md` — the ADC conversion scheme, glue logic,
timing and input-range spec all live there), COMP-10, `sar_logic.sym`, `adc_top/` (schematic +
symbol + verified subckt netlist), **Gate 3 PASS** (TT, 0.50–3.29 V) and **Gate 4 PASS** (all four
MOS corners; guaranteed range 0.62–3.29 V; `adc_top/sim/corners_report.md`). The ADC is
schematically done and verified end-to-end at transistor level.

**Your job is INT-8 / Gate 5: chip-level physical assembly**, i.e.:

1. Floorplan the three proven blocks + glue into padring **slot B (16 pins; 13 used:**
   `VDD VSS VIN CLK RST_N BIT_7..0 EOC`): DAC (`dac/layout/` top-level, tapeout-ready),
   comparator (`comparator/layout/strongarm.gds`), SAR strip (`sar_logic/layout/sar_cells.gds`,
   1219.6×45.7 µm — **fold via `designs/scripts/gen_sar_layout.py` if the slot needs a squarer
   block**; the generator supports it).
2. Draw + verify layouts for the 6 glue cells (2 inv, 2 nor2 for the buffered NOR decision latch,
   CK/SAMPLE inverters) — sar_logic leaf-cell layouts in `gen_sar_layout.py` are the template;
   **keep the two latch-input inverters identical/symmetric** (pin_contracts §4 explains why).
3. Top-level routing, then chip DRC (variant=D always) + LVS vs a native-element reference built
   from `adc_top/sim/adc_top_subckt.spice` (LVS refs must use native M/C elements — X-calls to
   undefined subckts silently extract 0 devices = false pass).
4. Close COMP-11 (extra substrate taps) and chip-level dummy fill / density (COMP-7 note) here.

**Env/workflow (hard-won, don't rediscover):** everything runs in docker
`hpretl/iic-osic-tools:chipathon26` (`docker run -d --user 501:20 -v "$(pwd)":/foss/designs --name
sar_sim …`; a `sar_sim` container may already exist — `docker start sar_sim`). DRC/LVS:
`designs/scripts/run_dac_drc.sh` / `run_dac_lvs.sh` (any block), variant=D, lvs_sub=VSS.
Headless netlisting: cwd matters — run xschem from `sar_logic/sar_designs` so bare-name symbol
refs resolve; xschem emits subckts by **basename** (the dac gate cells are `dac_nand2` etc. for
this reason — never create same-name cells in two libs). Sim: this comparator **requires**
`.tran` max step ≤0.05n + `reltol=1e-4` (coarser silently fabricates wrong decisions — cost us
half a session); per-code constant-VIN decks, not PWL staircases; `.save` only measured signals;
MIM caps need `.lib … mimcap_typical` AND `… cap_mim`.

**Conventions:** update PROGRESS.md rows as you close items; commit style `int:`/`comp:` etc. with
detailed bodies; verify every claim by running the tool; never eyeball.

**Still open for the team (not blocking INT-8):** target ENOB + sample rate (proposed 833 kS/s @
10 MHz, 12 CLK/conversion); ADC-level supply/temp sweeps (low-risk follow-up); REP-2..5;
datasheet lines from Gate 3/4: offset ≈ −0.5 LSB calibratable, input range 0.65–3.25 V.
