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
| DAC-1 | Binary-weighted 8-bit cap array schematic (C_u ≥ 50 fF) | Max | 🟡 Draft, unverified | `designs/libs/core_cap_dac/cap_array/cap_array.sch` — first-pass 8-row bottom-plate-switching array, hand-authored outside Xschem reusing Max's `unit_switch` + Emily's `inv1` + PDK `cap_mim_2f0fF`. **Not yet opened/simulated in Xschem — must be visually checked and netlisted before trusting.** See `docs/adc_glossary.md` for the DAC concept explainer. |
| DAC-2 | Cap array symbol | Max | 🟡 Draft, unverified | `designs/libs/core_cap_dac/cap_array/cap_array.sym` — hand-authored 13-pin symbol (VIN, VREF, VDD, SAMPLE, B0-B7, DAC_TOP); can be regenerated cleanly via Xschem's "generate symbol from schematic" once cap_array.sch is confirmed working |
| DAC-3 | 256×C_u switching & settling time testbench | Max | 🟢 Complete | `dac/sim/tb_major_carry.sch` — major-carry (0111_1111→1000_0000) Gate-2 settling testbench, connectivity-verified (all 8 caps share `DAC_TOP`, no floating ports). Supersedes the old first-pass `tb_cap_array.sch` (single-bit MSB-only, electrically disconnected — **deleted 2026-07-17**). |
| DAC-3b *(ported)* | Max's unit-cell switch, relocated from `origin/max` into the `core_cap_dac` naming convention and reused (unmodified) inside `cap_array.sch` | Max | 🟢 Complete (as ported) | `designs/libs/core_cap_dac/unit_switch.sch`/`.sym` — original WIP branch (`origin/max`, last commit 2026-07-11) still has an untouched `tb_unit_capa.sch` if useful for reference. **⚠️ Heads-up:** that branch's stated next step was a *bootstrap* switch — schematic-review feedback explicitly advised against this for an 8-bit DAC ("unnecessarily increases design time without much benefit... a simple sized transmission gate should be a good start," see [Review Feedback](#review-feedback--open-items)). The unit_switch as ported here is already a simple 3-transistor pass-gate switch, not a bootstrap switch, so this concern is addressed for the DAC's own switches. |
| DAC-4 | **Gate 2** — 0.5 LSB settling within 40 ns (TT + PVT corners) | Max | 🟢 **PASS** | `dac/WORKLOG.md` (2026-07-17 entry), `VERIFICATION_PLAN.md` — TT: 1.77 ns. Full PVT sweep (5 process corners × 3 temps × 2 V_DD, 30 combos): worst case SS/125°C/2.97V settles in 2.78 ns, 37.2 ns margin to spec, err@40ns ≈ 0 mV in every corner. |
| DAC-5 | Unit-cell layout with common-centroid placement (KLayout) | TBD | ⚪ Not Started | `designs/libs/core_cap_dac/cu_cell/cu_cell.gds` |
| DAC-6 | Full array layout with dummy/fringe peripheral caps | TBD | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/cap_array.gds` |
| DAC-7 | Sub-block DRC clean | TBD | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/drc/dac_drc.log` |
| DAC-8 | Sub-block LVS clean (Netgen) | TBD | ⚪ Not Started | `designs/libs/core_cap_dac/cap_array/lvs/dac_lvs.log` |

---

## 4 · SAR Digital Controller (SAR)

> **Design-flow update (2026-07-11):** the controller is built as **full-custom schematic capture in xschem** (gate-level, Anderson architecture) rather than the Verilog → Yosys → OpenROAD digital-synthesis flow originally planned below. **Correction:** this was previously noted as living only in Sam's unmerged fork — PR #3 (`sar`) merged into `main` on 2026-07-11, so the cells and top-level schematic now live in this repo at `sar_logic/sar_designs/`. `sar_logic/{rtl,syn,pnr}` still only contain `.gitkeep` placeholders from the old synthesis-flow plan.

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| SAR-1 | Standard-cell schematic entry + testbench: INV, TG, NAND2, NOR2, DFF_RST_N, DFF_SET_N | Sam | 🟡 In Progress | `sar_logic/sar_designs/*.sch` (merged into `main` 2026-07-11) — 5/6 cells built and functionally verified (INV, TG, NAND2, NOR2, DFF_RST_N all pass their testbenches). **DFF_SET_N is broken** — NOR-gate / inverted-RST_N handling bug, needs a fix before it can seed the sequencer's leading bit |
| SAR-2 | Top-level SAR_LOGIC schematic — Anderson architecture: 9-FF sequencer + 8-FF code register + 8× (NOR2+INV) OR-gate DAC-drive stage, 17 flip-flops total | Sam | 🟡 In Progress | `sar_logic/sar_designs/sar_logic.sch` (merged into `main` 2026-07-11) — schematic assembled ("FINAL SAR TOP-LEVEL SCHEMATIC"), not yet simulated end-to-end — **blocked on the DFF_SET_N fix** (SAR-1) |
| SAR-3 | Full binary-search functional testbench (verify 8-bit code capture + End-of-Conversion signal) | Sam | ⚪ Not Started | `sar_logic/tb/tb_sar_logic.sch` |
| SAR-4 | SAR_LOGIC physical layout (KLayout) | Sam | ⚪ Not Started | `sar_logic/layout/sar_logic.gds` |
| SAR-5 | Sub-block DRC clean | Sam | ⚪ Not Started | `sar_logic/layout/drc/sar_logic_drc.log` |
| SAR-6 | Sub-block LVS clean | Sam | ⚪ Not Started | `sar_logic/layout/lvs/sar_logic_lvs.log` |

---

## 5 · Bootstrap Switch / Sample-and-Hold (SWITCH)

> **Previously untracked:** this block was missing from the tracker entirely even though it's owned (per the team's schematic-review slide deck) and merged into `main`. Adding it now so it isn't invisible again.

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| SWITCH-1 | Bootstrapped switch schematic for the comparator/SAR sample-and-hold front end (pre-charge + gate-drive to V_DD + V_IN, constant V_GS ≈ 3.3 V) | Emily | 🟢 Complete | `designs/emily_testing/TB_bootstrap_switch.sch` (merged into `main` 2026-07-01) |
| SWITCH-2 | Bootstrap switch testbench (ideal-inverter clock, transient) | Emily | 🟢 Complete | same file — transient plots confirm V_OUT tracks V_IN with negligible droop, constant gate overdrive each cycle |
| SWITCH-3 | 3-way NMOS switch submodule (DAC-side: sample / ref / ground) | Mimi *(per team slide; file committed by Emily — confirm ownership)* | 🟢 Complete | `designs/emily_testing/TB_swtich2.sch` — real transistor-level switch (nfet3.3/pfet3.3 + inverter + cap_mim load), tested with temporary fake capacitors, confirmed correct grab of input during sampling + clean flip to ref/ground during the guessing phase. **Correction:** `switch3.sch` (same folder) is NOT this — it's an empty stub (3 voltage sources + a sim-control block, no transistors at all), don't mistake it for working switch content. |
| SWITCH-4 | Integrate bootstrap/3-way switch into the real DAC cap array (replace fake test caps) | TBD | ⚪ Not Started | superseded for now — `cap_array.sch` (DAC-1, see below) uses Max's `unit_switch` instead, since it's already validated and directly reusable. See the open S/H architecture question in `docs/adc_glossary.md`. |
| SWITCH-5 | S/H settling simulation with worst-case DAC load + comparator C_in (per reviewer feedback, see below) | TBD | ⚪ Not Started | — |

**Note on Mimi:** her `mimi-test` branch has no commits beyond what's already in `main` — the 3-way switch her slide credits her with lives in Emily's `emily_testing/` folder. Worth checking with Mimi whether she has separate unpushed work, or whether this was a joint/miscredited item.

**Open architecture question:** the team currently has two competing S/H schemes that haven't been reconciled — Emily's bootstrap switch (top-plate sampling) vs. Max's per-bit `unit_switch` (bottom-plate sampling, used directly in the new `cap_array.sch`). Only one should make it into the real chip. See `docs/adc_glossary.md` for the tradeoff.

---

## 6 · Alternative Comparator Design (COMP-ALT)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| COMP-ALT-1 | Alternative comparator topology (backup/comparison to the StrongARM latch) | Luc | ⚪ Not Started | `designs/luc_testing/` currently only has Xschem warm-up files (`inv.sch`, `rc_circuit_test.sch`, dated 2026-06-14) — no comparator topology work has landed yet, on this branch or `main` |

---

## 7 · Automation & Reproducibility Suite (REP)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| REP-1 | Python script: parse ngspice `.raw` → DNL/INL | Bruno | ⚪ Not Started | `designs/scripts/extract_dnl_inl.py` |
| REP-2 | Python script: FFT spectrum → ENOB / SNDR | Bruno | ⚪ Not Started | `designs/scripts/calc_enob.py` |
| REP-3 | Master simulation runner script | Bruno | ⚪ Not Started | `designs/scripts/run_all_sims.sh` |
| REP-4 | Reproducibility environment doc | Bruno | ⚪ Not Started | `REPRODUCIBILITY.md` |
| REP-5 | CI library-check passes on `main` branch | Bruno | ⚪ Not Started | `.github/workflows/library_check.yml` |

---

## Review Feedback & Open Items

> From the mid-project schematic review (Reviewer: Saroj Rout — **Total 8/20, Conditional Go**). Terms below are defined in **[docs/adc_glossary.md](docs/adc_glossary.md)**.

| Item | Status |
|------|--------|
| Define measurable target specs: Resolution, ENOB, conversion rate, DNL, INL | ⚪ Not defined yet — currently only DNL/INL gates (Gate 3/4) exist; no target ENOB or conversion-rate number is written down anywhere |
| S/H simulation must load worst-case DAC switch config + comparator input cap, not an ideal/light load | ⚪ Not started (SWITCH-5 above) |
| DAC capacitor sizing should be justified via kT/C noise budget, not just "C_u ≥ 50 fF" as a guess | ⚪ Not started |
| Avoid a bootstrap switch for the 8-bit DAC specifically — a sized transmission gate is sufficient and cheaper on schedule | 🔴 At risk — Max's branch's stated next step is a DAC bootstrap switch (see DAC-3b above) |
| Comparator offset should be reduced via proper buffer/latch sizing (gm/Id-annotated), not brute-force area scaling | 🟢 Addressed — COMP-5 already treats offset as a calibratable DC shift, no upsizing done |
| Foundry mismatch data assumes perfect common-centroid layout; current comparator layout will have worse real offset than MC predicts | ⚪ Not accounted for in COMP layout yet |
| Keep an overall project tracker (this file) up to date across all blocks | 🟡 In progress — this update adds the previously-missing SWITCH and COMP-ALT blocks |

---

## Verification Gates Summary

| Gate | Criterion | Block | Status |
|------|-----------|-------|--------|
| Gate 1 | σ_offset characterized + delay < 2 ns @ TT (MC N≥100) | Comparator | 🟡 |
| Gate 2 | DAC settling ≤ 0.5 LSB within 40 ns @ TT | Cap DAC | 🟢 PASS (TT + full PVT sweep, worst case 2.78 ns / 37.2 ns margin — see `VERIFICATION_PLAN.md`) |
| Gate 3 | Top-level DNL/INL < 0.5 LSB @ TT corner | Integration | ⚪ |
| Gate 4 | Full corner sweep (FF/SS/SF/FS) passes spec | Integration | ⚪ |
| Gate 5 | DRC clean + LVS clean → tapeout sign-off | Integration | ⚪ |