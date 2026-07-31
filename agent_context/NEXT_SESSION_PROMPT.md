# Prompt for next Claude session — top-level integration (INT-2…INT-8)

Copy-paste everything below the line into a fresh Claude Code session started in the repo root.

---

Read PROGRESS.md first (especially the 2026-07-30 snapshot and the "What's Left — Critical Path" section). All three sub-blocks of our 8-bit SAR ADC (gf180mcuD) are individually complete and signed off:

- **DAC** (`dac/`): Gates 2/3/5 closed, block is tapeout-ready (DRC 0/660, LVS 377/377). 12 pins: VIN, VDD, SAMPLE, B0–B7, DAC_TOP.
- **Comparator** (`comparator/`): StrongARM, Gate 1 PASS (delay 370 ps worst-corner vs 2 ns budget; offset treated as calibratable DC shift). 7 pins: CK, VIN1, VIN2, VOUT1, VOUT2, VDD, VSS.
- **SAR_LOGIC** (`sar_logic/`): SAR-1…6 all closed 2026-07-30 — logic verified end-to-end (transistor-level binary search, codes exact) and laid out (1219.6×45.7 µm strip, DRC 0/660, LVS 458/458). 14 pins: VDD, VSS, BIT_7..0, EOC, RST_N, CMP_OUT, CLK.
- `comparator_alt/` is Luc's backup double-tail comparator (for the paper) — NOT on the critical path; leave it alone.

Your job is **top-level integration**, in this order:

1. **INT-2 — pin-contract table** (`docs/pin_contracts.md`): all three block interfaces above, plus how they wire together: BIT_i → DAC B_i; comparator VOUT→CMP_OUT (single-ended — decide and document which VOUT polarity, check `sar_logic` expects CMP_OUT=1 to KEEP the trial bit, i.e. VIN>VDAC); DAC_TOP → comparator VIN1 with VIN2 at a mid-rail reference (Vcm ≥ 0.85 V required per COMP-5); SAMPLE/CLK/RST_N phasing (SAMPLE is the DAC's top-plate TG control; SAR RST_N doubles as start-of-conversion; comparator CK must strobe between SAR clock edges — propose a scheme). EOC timing: rises 8 CLK edges after RST_N release.
2. **COMP-10 — sync `comparator/schematic/strongarm.sch` to the LVS-proven `strongarm.spice`**: fix the unit-less `L=0.28` typo on M1 (line ~93) and retie all bulks to VSS/VDD rails (no per-device bulk nets — unbuildable without deep-nwell). Verify by re-netlisting and diffing against `strongarm.spice` (topology + W/L must match). Do this BEFORE stitching, or the comparator regresses.
3. **Create `sar_logic/sar_designs/sar_logic.sym`** (14 pins, port order must match the netlist: VDD VSS BIT_7..BIT_0 EOC RST_N CMP_OUT CLK) — none exists yet.
4. **INT-3/4/5 — stitch `adc_top.sch` + symbol + integration TB** and run a full conversion at TT (Gate 3 = INT-6: DNL/INL < 0.5 LSB via the 256-code sweep; reuse `designs/scripts/extract_dnl_inl.py`). Then INT-7 corners (Gate 4).
5. If you get that far: INT-8 / Gate 5 chip-level assembly (dummy fill + COMP-11 substrate taps close out here).

**Environment/workflow facts (hard-won, don't rediscover):**
- Host Mac has NO EDA tools. Everything runs in docker image `hpretl/iic-osic-tools:chipathon26`. Start one-shot: `docker run -d --user 501:20 -v "$(pwd)":/foss/designs --name sar_sim hpretl/iic-osic-tools:chipathon26`, then `docker exec -e HOME=/headless -e USER=headless <name> bash -lc '<cmd>'`.
- Headless netlisting: `XSCHEM_USER_LIBRARY_PATH=/foss/designs xschem --rcfile /foss/designs/designs/.config/.xschem/xschemrc -n -q -x -o <outdir> <sch>`. Subckt-ify a top-level netlist by uncommenting `**.subckt`/`**.ends` and dropping the trailing `.end`.
- ngspice batch: replace `plot` with `wrdata` in the `.control` block; models at `/foss/pdks/gf180mcuD/libs.tech/ngspice/`.
- DRC/LVS: `designs/scripts/run_dac_drc.sh` / `run_dac_lvs.sh` (work for any block despite the name), **variant=D always**, lvs_sub=VSS. LVS references must use native M/C elements (X-calls to undefined subckts silently extract to 0 devices = false pass).
- xschem instance names in schematics must start with x (S*/C* netlist as SPICE switch/capacitor primitives).
- macOS bind-mount can serve stale files right after host-side `sed -i` — if a netlist looks wrong, just re-run the netlist step.
- SAR layout generator: `designs/scripts/gen_sar_layout.py` (channel router; see docstrings for the DRC rule lessons). If the chip floorplan needs a squarer SAR block, fold the top row there.

**Conventions:** update PROGRESS.md rows + the critical-path section as you close items; commit style `sar:`/`comp:`/`dac:`/`int:` prefixes with detailed bodies; verify every claim by running the tool, never by eyeballing; branch off `main` (after PR #6 merges — it contains ALL of the SAR work and the `comparator_alt/` reorg, so pull first).

**Still-undefined specs to nail down with the team (blocks a clean Gate-4 story):** target ENOB and conversion/sample rate.
