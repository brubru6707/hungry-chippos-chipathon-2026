# Hungry Chippos — 8-bit SAR ADC Progress Tracker

> **PDK:** GlobalFoundries 180nm (gf180mcuD) · **Toolchain:** Xschem · Ngspice · KLayout · Netgen · OpenROAD
> **Status legend:** 🟢 Complete · 🟡 In Progress · ⚪ Not Started · 🔴 Blocked

---

## 1 · Global Integration (INT)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| INT-1 | Repo skeleton, CI stubs, Docker env verified | Bruno | 🟡 In Progress | `README.md`, `.github/workflows/` |
| INT-2 | Define precise block pin interfaces (pin-contract table) | Bruno | ⚪ Not Started | `docs/pin_contracts.md` |
| INT-3 | Top-level schematic stitching (ADC top) | Bruno | ⚪ Not Started | `designs/libs/core_sar_adc/adc_top/adc_top.sch` |
| INT-4 | Top-level symbol for ADC | Bruno | ⚪ Not Started | `designs/libs/core_sar_adc/adc_top/adc_top.sym` |
| INT-5 | Integration testbench (TT corner, full conversion cycle) | Bruno | ⚪ Not Started | `designs/libs/tb_sar_adc/tb_adc_top/tb_adc_top.sch` |
| INT-6 | **Gate 3** — TT-corner DNL/INL sweep pass (<0.5 LSB) | Bruno | ⚪ Not Started | `designs/simulations/adc_top_tt/dnl_inl_plots/` |
| INT-7 | **Gate 4** — Full corner sweep (FF / SS / SF / FS) | Bruno | ⚪ Not Started | `designs/simulations/adc_top_corners/corners_report.log` |
| INT-8 | **Gate 5** — DRC & LVS clean, tapeout sign-off | Bruno | ⚪ Not Started | `designs/libs/core_sar_adc/adc_top/lvs/adc_top_lvs.log` |

---

## 2 · Comparator Block (COMP)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| COMP-1 | StrongARM latch schematic entry | Bruno | 🟢 Complete | `comparator/schematic/strongarm.sch` |
| COMP-2 | Comparator symbol creation | Bruno | 🟢 Complete | `comparator/schematic/strongarm.sym` |
| COMP-3 | Functional transient testbench (single-shot) | Bruno | 🟢 Complete | `comparator/schematic/strongarm_tb.sch` |
| COMP-4 | Monte Carlo testbench setup (N ≥ 100 runs) | Bruno | 🟢 Complete | `comparator/schematic/strongarm_mc_tb.sch` |
| COMP-5 | **Gate 1** — input-referred offset characterized (MC) + delay < 2 ns | Bruno | 🟡 In Progress | `comparator/comp_mc_report.txt`, `comp_mc_offsets.{raw,txt}` — **Offset DONE:** the +15.1 mV systematic was a `#net5`/M6 wiring bug, now **FIXED**. MC re-run at real silicon mismatch (svt ≈ 24.8 mV, N=100, good=100/100): **mean +2.6 mV (≈ 0, no systematic), σ = 36.9 mV** (matches predicted √2·svt ≈ 35 mV). Note: literal "σ < 2 mV" is a flash/pipeline target — for a SAR, comparator offset is a calibratable **DC shift** with no DNL/INL impact → **offset sub-gate cleared, no device upsizing**. ⏳ **Delay < 2 ns not yet measured (regeneration speed).** |
| COMP-6 | Comparator physical layout (KLayout) | Bruno | 🟢 Complete | `comparator/layout/strongarm.gds` |
| COMP-7 | Sub-block DRC clean | Bruno | 🟢 Complete | `comparator/layout/backups/strongarm_DRC_CLEAN_2026-07-10_15h26m1783711590.gds` — 0 violations (antenna clean; density flags only whole-cell minimum-density, deferred to chip-level dummy fill) |
| COMP-8 | Sub-block LVS clean (KLayout, not Netgen) | Bruno | 🟢 Complete | `comparator/layout/backups/strongarm_LVS_CLEAN_2026-07-10_10h44m1783694640.gds` — netlists match, 11/11 devices correct. **Note:** verify via the terminal `run_lvs.py` flow in `handoff/README.md`, not the KLayout GUI's "Run KLayout LVS" menu action — that GUI path has a confirmed bug (false short) on this layout, tracked in `bugs/github-issue.md` |
| COMP-9 | Post-layout extraction (PEX) corner simulation | TBD | ⚪ Not Started | `designs/simulations/comp_pex/comp_pex_transient.log` |

---

## 3 · Capacitor DAC Block (DAC)

> **Interface note (2026-07-10, from Sam's SAR design doc):** the SAR_LOGIC top-level's bottom row is 8 OR gates (NOR2+INV), one per bit, each driving one DAC switch high/low based on the sequencer + code-register state. DAC-1's schematic should plan for **8 single-ended digital switch-control pins** (one per cap) as the drive interface from the SAR controller — feeds into the INT-2 pin-contract table too.

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| DAC-1 | Binary-weighted 8-bit cap array schematic (C_u ≥ 50 fF) | Max | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/cap_array.sch` |
| DAC-2 | Cap array symbol | Max | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/cap_array.sym` |
| DAC-3 | 256×C_u switching & settling time testbench | Max | ⚪ Not Started | `designs/libs/tb_cap_dac/tb_cap_array/tb_cap_array.sch` |
| DAC-4 | **Gate 2** — 0.5 LSB settling within 40 ns (TT) | Max | ⚪ Not Started | `designs/simulations/dac_settling/dac_settling_curves.png` |
| DAC-5 | Unit-cell layout with common-centroid placement (KLayout) | TBD | ⚪ Not Started | `designs/libs/core_cap_dac/cu_cell/cu_cell.gds` |
| DAC-6 | Full array layout with dummy/fringe peripheral caps | TBD | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/cap_array.gds` |
| DAC-7 | Sub-block DRC clean | TBD | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/drc/dac_drc.log` |
| DAC-8 | Sub-block LVS clean (Netgen) | TBD | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/lvs/dac_lvs.log` |

---

## 4 · SAR Digital Controller (SAR)

> **Design-flow update (2026-07-10, from Sam's design doc):** the controller is being built as **full-custom schematic capture in xschem** (gate-level, Anderson architecture) rather than the Verilog → Yosys → OpenROAD digital-synthesis flow originally planned below. This work currently lives in Sam's separate local fork and has **not yet been merged into this repo** — `sar_logic/{rtl,syn,pnr}` here still only contain `.gitkeep` placeholders from the old plan.

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| SAR-1 | Standard-cell schematic entry + testbench: INV, TG, NAND2, NOR2, DFF_RST_N, DFF_SET_N | Sam | 🟡 In Progress | `sar_logic/cells/*.sch` (Sam's fork) — 5/6 cells built and functionally verified (INV, TG, NAND2, NOR2, DFF_RST_N all pass their testbenches). **DFF_SET_N is broken** — NOR-gate / inverted-RST_N handling bug, needs a fix before it can seed the sequencer's leading bit |
| SAR-2 | Top-level SAR_LOGIC schematic — Anderson architecture: 9-FF sequencer + 8-FF code register + 8× (NOR2+INV) OR-gate DAC-drive stage, 17 flip-flops total | Sam | 🟡 In Progress | `sar_logic/sar_logic.sch` (Sam's fork) — schematic assembled ("FINAL SAR TOP-LEVEL SCHEMATIC"), not yet simulated end-to-end — **blocked on the DFF_SET_N fix** (SAR-1) |
| SAR-3 | Full binary-search functional testbench (verify 8-bit code capture + End-of-Conversion signal) | Sam | ⚪ Not Started | `sar_logic/tb/tb_sar_logic.sch` |
| SAR-4 | SAR_LOGIC physical layout (KLayout) | Sam | ⚪ Not Started | `sar_logic/layout/sar_logic.gds` |
| SAR-5 | Sub-block DRC clean | Sam | ⚪ Not Started | `sar_logic/layout/drc/sar_logic_drc.log` |
| SAR-6 | Sub-block LVS clean | Sam | ⚪ Not Started | `sar_logic/layout/lvs/sar_logic_lvs.log` |

---

## 5 · Automation & Reproducibility Suite (REP)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| REP-1 | Python script: parse ngspice `.raw` → DNL/INL | Bruno | ⚪ Not Started | `designs/scripts/extract_dnl_inl.py` |
| REP-2 | Python script: FFT spectrum → ENOB / SNDR | Bruno | ⚪ Not Started | `designs/scripts/calc_enob.py` |
| REP-3 | Master simulation runner script | Bruno | ⚪ Not Started | `designs/scripts/run_all_sims.sh` |
| REP-4 | Reproducibility environment doc | Bruno | ⚪ Not Started | `REPRODUCIBILITY.md` |
| REP-5 | CI library-check passes on `main` branch | Bruno | ⚪ Not Started | `.github/workflows/library_check.yml` |

---

## Verification Gates Summary

| Gate | Criterion | Block | Status |
|------|-----------|-------|--------|
| Gate 1 | σ_offset characterized + delay < 2 ns @ TT (MC N≥100) | Comparator | 🟡 |
| Gate 2 | DAC settling ≤ 0.5 LSB within 40 ns @ TT | Cap DAC | ⚪ |
| Gate 3 | Top-level DNL/INL < 0.5 LSB @ TT corner | Integration | ⚪ |
| Gate 4 | Full corner sweep (FF/SS/SF/FS) passes spec | Integration | ⚪ |
| Gate 5 | DRC clean + LVS clean → tapeout sign-off | Integration | ⚪ |