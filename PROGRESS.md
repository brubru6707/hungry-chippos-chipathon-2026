# Hungry Chippos — 8-bit SAR ADC Progress Tracker

> **PDK:** GlobalFoundries 180nm (gf180mcuD) · **Toolchain:** Xschem · Ngspice · KLayout · Netgen · OpenROAD  
> **Status legend:** 🟢 Complete · 🟡 In Progress · ⚪ Not Started · 🔴 Blocked

---

## 1 · Global Integration (INT)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| INT-1 | Repo skeleton, CI stubs, Docker env verified | Bruno | 🟡 In Progress | `README.md`, `.github/workflows/` |
| INT-2 | Define precise block pin interfaces (pin-contract table) | Bruno | ⚪ Not Started  | `docs/pin_contracts.md` |
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
| COMP-1 | Regenerative dynamic latch schematic entry | Emily | 🟡 In Progress | `designs/libs/core_comparator/comparator/comparator.sch` |
| COMP-2 | Comparator symbol creation | Emily | ⚪ Not Started | `designs/libs/core_comparator/comparator/comparator.sym` |
| COMP-3 | Functional transient testbench (single-shot) | Luc | ⚪ Not Started | `designs/libs/tb_comparator/tb_comparator/tb_comparator.sch` |
| COMP-4 | Monte Carlo testbench setup (N ≥ 200 runs) | Luc | ⚪ Not Started | `designs/libs/tb_comparator/tb_comparator_mc/tb_comparator_mc.sch` |
| COMP-5 | **Gate 1** — σ_offset < 2 mV & delay < 2 ns (MC pass) | Emily / Luc | ⚪ Not Started | `designs/simulations/comp_mc/comp_mc_distribution.png` |
| COMP-6 | Comparator physical layout (KLayout) | Emily | ⚪ Not Started | `designs/libs/core_comparator/comparator/comparator.gds` |
| COMP-7 | Sub-block DRC clean | Luc | ⚪ Not Started | `designs/libs/core_comparator/comparator/drc/comp_drc.log` |
| COMP-8 | Sub-block LVS clean (Netgen) | Luc | ⚪ Not Started | `designs/libs/core_comparator/comparator/lvs/comp_lvs.log` |
| COMP-9 | Post-layout extraction (PEX) corner simulation | Emily / Luc | ⚪ Not Started | `designs/simulations/comp_pex/comp_pex_transient.log` |

---

## 3 · Capacitor DAC Block (DAC)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| DAC-1 | Binary-weighted 8-bit cap array schematic (C_u ≥ 50 fF) | Sam | 🟡 In Progress | `designs/libs/core_cap_dac/cap_array/cap_array.sch` |
| DAC-2 | Cap array symbol | Sam | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/cap_array.sym` |
| DAC-3 | 256×C_u switching & settling time testbench | Sam | ⚪ Not Started | `designs/libs/tb_cap_dac/tb_cap_array/tb_cap_array.sch` |
| DAC-4 | **Gate 2** — 0.5 LSB settling within 40 ns (TT) | Sam | ⚪ Not Started | `designs/simulations/dac_settling/dac_settling_curves.png` |
| DAC-5 | Unit-cell layout with common-centroid placement (KLayout) | Mimi | ⚪ Not Started | `designs/libs/core_cap_dac/cu_cell/cu_cell.gds` |
| DAC-6 | Full array layout with dummy/fringe peripheral caps | Mimi | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/cap_array.gds` |
| DAC-7 | Sub-block DRC clean | Mimi | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/drc/dac_drc.log` |
| DAC-8 | Sub-block LVS clean (Netgen) | Mimi | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/lvs/dac_lvs.log` |

---

## 4 · SAR Digital Controller (SAR)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| SAR-1 | Synchronous FSM Verilog RTL coding | Max | 🟡 In Progress | `designs/libs/core_sar_ctrl/rtl/sar_ctrl.v` |
| SAR-2 | RTL functional validation — Icarus Verilog testbench | Max | ⚪ Not Started | `designs/libs/core_sar_ctrl/tb/tb_sar_ctrl.v` |
| SAR-3 | Yosys synthesis (gf180mcu standard cells) | Max | ⚪ Not Started | `designs/libs/core_sar_ctrl/syn/synth.tcl` |
| SAR-4 | OpenROAD floorplan & place-and-route | Max | ⚪ Not Started | `designs/libs/core_sar_ctrl/pnr/` |
| SAR-5 | Timing closure — 20 MHz minimum / 200 MHz target | Max | ⚪ Not Started | `designs/libs/core_sar_ctrl/pnr/timing_slack.rpt` |
| SAR-6 | Exported GDS from OpenROAD, DRC/LVS verify | Max | ⚪ Not Started | `designs/libs/core_sar_ctrl/pnr/sar_ctrl.gds` |

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
| Gate 1 | σ_offset < 2 mV, delay < 2 ns @ TT (MC N≥200) | Comparator | ⚪ |
| Gate 2 | DAC settling ≤ 0.5 LSB within 40 ns @ TT | Cap DAC | ⚪ |
| Gate 3 | Top-level DNL/INL < 0.5 LSB @ TT corner | Integration | ⚪ |
| Gate 4 | Full corner sweep (FF/SS/SF/FS) passes spec | Integration | ⚪ |
| Gate 5 | DRC clean + LVS clean → tapeout sign-off | Integration | ⚪ |
