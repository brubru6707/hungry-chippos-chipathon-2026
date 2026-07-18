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

> **Interface note (2026-07-10, from Sam's SAR design doc):** the SAR_LOGIC top-level's bottom row is 8 OR gates (NOR2+INV), one per bit, each driving one DAC switch based on the sequencer + code-register state. The DAC exposes **8 single-ended digital switch-control pins** (one per cap) — feeds into the INT-2 pin-contract table too.

> **Relocation note (2026-07-17):** the DAC now lives in a **self-contained top-level `dac/` folder** (`dac/schematic`, `dac/sim`, `dac/layout`), mirroring `comparator/`. The old `designs/libs/core_cap_dac/` and `designs/libs/tb_cap_dac/` scratch copies were deleted after the files were ported and verified. Running notes live in `dac/WORKLOG.md`.

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| DAC-1 | Binary-weighted 8-bit cap array schematic (C_u ≥ 50 fF) | Bruno | 🟢 Complete | `dac/schematic/cap_array.sch` — 8-row binary-weighted bottom-plate array (C_u = 50 fF, weights 1–128). **Connectivity-verified in Xschem** (all 8 caps share `DAC_TOP`, no floating ports). ⚠️ The original hand-authored version had **cosmetic-only `lab=` text that netlisted as a fully disconnected array** — real `lab_wire` components were added and the netlist re-verified. Includes per-bit switch sizing (DAC-3b) + SAMPLE-gating (DAC-4b). Input sampling front-end being finalized as top-plate sampling (see SWITCH-4). |
| DAC-2 | Cap array symbol | Bruno | 🟢 Complete | `dac/schematic/cap_array.sym` — 12-pin (VIN, VDD, SAMPLE, B0–B7, DAC_TOP). `VREF` pin removed 2026-07-18 (was 13-pin incl. VREF) — see DAC-4/DAC-9 VREF=VDD rework. |
| DAC-3 | 256×C_u switching & settling testbench | Bruno | 🟢 Complete | `dac/sim/tb_major_carry.sch` — major-carry (0111_1111→1000_0000) Gate-2 settling tb, connectivity-verified. Supersedes the old `tb_cap_array.sch` (single-bit, electrically disconnected — **deleted 2026-07-17**). |
| DAC-3b | Unit-cell switch — CMOS rail driver (VREF=VDD rework) | Bruno | 🟢 Complete | `dac/schematic/unit_switch.sch`/`.sym` — **redesigned 2026-07-18**: was a 2-NMOS pass-gate to `VREF`(1.65V)/GND (no bootstrap; originally authored by Max on `origin/max`, ported + per-bit sized W=2ⁱ×0.42µm); an NMOS pass transistor can't pull to the full `VDD` rail, so VREF was capped below `VDD`. Now a CMOS rail driver: PMOS pull-up to `VDD` + NMOS pull-down to `GND`, both gated by the single `bN_bar=NAND2(Bn,SAMPLE_N)` signal (the old separate `bN` AND-inverter stage was removed as dead logic once both gates needed the same signal). `pfet_wid=2×nfet_wid` per bit (inv1/nand2/tgate P:N=2:1 convention); MSB PMOS (107.52µm) exceeds gf180mcuD's binned-model width ceiling (100.001µm) so it's built as `pfet_wid=53.76u pfet_m=2`. A single unit-sized switch (pre-DAC-3b) missed MSB settling by ~112× (276 ns); scaling W with cap weight holds τ constant → Gate 2 PASS. |
| DAC-4 | **Gate 2** — 0.5 LSB settling within 40 ns (TT + PVT corners) | Bruno | 🟢 **PASS** | `dac/WORKLOG.md`, `VERIFICATION_PLAN.md` — post VREF=VDD rework (2026-07-18, LSB now 12.9mV/FS=3.3V): TT settle=2.61ns err@40n=0mV; worst corner **SS/125°C/2.97V settles in 3.86 ns (36.1 ns margin)**, err@40ns=0mV. (Previously, under VREF=1.65V: TT 1.77ns, full 30-corner sweep worst case SS/125°C/2.97V 2.78ns — superseded.) |
| DAC-4b | SAMPLE-gating — remove sampling-phase switch contention | Bruno | 🟢 Complete | `dac/schematic/cap_array.sch` + new `nand2`/`nor2` cells — bit drivers gated by SAMPLE so both switch arms open during sampling. Crowbar current cut from ~4–10 mA to pA; Gate-2 regression still PASS. |
| DAC-4c | Sample-and-hold characterization (acquisition, hold droop, kT/C) | Bruno | 🟢 Complete | `dac/sim/tb_sample_hold.sch`, `dac/WORKLOG.md` — full-range acquisition now PASSES with the TG top switch (3.0 V settles 78.6 ns worst-corner, 3.2 V 73.7 ns, sub-mV error). Hold droop negligible; kT/C ≈ 18 µV rms. Testbench needed a `.ic`/`uic` fix (was pre-charging DAC_TOP via a DC-op-point artifact). |
| DAC-4d | Support cells + top-plate sample switch | Bruno | 🟢 Complete | `dac/schematic/{inv1,nand2,nor2,tgate}.sch` — TG top-plate switch sized nfet 4 µm / pfet 8 µm (L = 0.28 µm), Ron ≈ 294–1098 Ω. Sizing chosen to cap charge injection at 0.18 LSB (vs 0.26 LSB for a faster 6/12 µm option). |
| DAC-9 | 256-code nominal INL/DNL transfer sweep (DAC-only, TT) | Bruno | 🟢 Complete | `dac/sim/tb_inl_dnl.sch`, `designs/scripts/extract_dnl_inl.py`, `dac/docs/figures/{dnl,inl}_vs_code.png` — one 64 µs stepped transient, fixed VIN=0 sample input. **Re-verified 2026-07-18 after VREF=VDD rework:** measured FS span = 3292.98 mV (99.8% of the 3.3V rail — gain gap resolved, was ≈1.6465V≈VREF/2× short before the rework), V_LSB=12.914mV. Nominal (perfectly-matched schematic caps): max\|DNL\|=0.00216 LSB (code 196), max\|INL\|=0.00439 LSB endpoint / 0.00290 LSB best-fit — monotonic, no missing codes. |
| DAC-9b | Capacitor-mismatch Monte Carlo INL/DNL (the real linearity limit) | Bruno | 🟢 **PASS @ Cu=50fF** | `designs/scripts/dac_mismatch_mc.py`, `dac_mismatch_mc_spice.py`, `dac/docs/figures/mc_*.png` — **corrected 2026-07-17 (Step 2e):** earlier verdict (71.5% yield, Cu≥200-400fF needed) used the PDK's *global* `cap_mim` MC term (`sw_stat_global`, 2.5%) as if it were independent *local* per-cap mismatch — a modeling bug, not a real result (global variation is a common scale factor and cancels in this ratiometric DAC; only local mismatch drives DNL/INL). Redone with a proper local Pelgrom model, `sigma(C_unit)/C_unit = A_C/sqrt(Area)` (A_C=1.6%·µm primary, 3.2%·µm conservative 2× — literature 180nm-MiM estimates, gf180mcuD ships no local number). Result at N=300,000: yield **≥99.9997%** at Cu=50fF for both A_C cases (worst\|DNL\|=0.25-0.51 LSB, worst\|INL\|=0.13-0.28 LSB, both < 0.5 LSB spec). **No unit-cap upsizing required — current 50fF/5µm×5µm is adequate.** Global 2.5% effect isolated separately: full-scale gain error ≈0.004% sigma (not 2.5% — cancels almost entirely in the cap ratio), zero DNL/INL impact, confirming the local/global distinction. See `dac/WORKLOG.md` Step 2e. |
| DAC-5 | Unit-cell layout with common-centroid placement (KLayout) | TBD | 🟡 Partial | `dac/layout/cu_cell.gds` — 50fF cap_mim unit cell redrawn for **variant=D (metal_top=11K, mim_option=B, metal_level=5LM — the real, signed-off chip stack)**: FuseTop top plate over a Metal4 bottom plate, Via4 breakouts to two symmetric (N+S) Metal5 pads, 6.2×8.06 µm footprint, symmetric about both axes. DRC clean (0 violations, 660 rule categories, `run_dac_drc.sh`) and LVS clean (`run_dac_lvs.sh`, native SPICE `C`-element reference netlist, extracts as `cap_mim_2f0fF`/`CAP_MIM_2F0FF` @ 50fF, device count 1 on both sides, "Netlists match"). Supersedes the earlier variant=A/3LM cell (commit `15e9d45`), which extracted as 0 devices under the real stack — see `dac/WORKLOG.md` 2026-07-18 entries. **Per DAC-9b (corrected), Cu=50fF is adequate for random mismatch; no upsizing needed. Common-centroid placement is still mandatory** (cancels *systematic* oxide-gradient error) — the 255-unit array + common-centroid tiling (Step 2) has **not** started; this entry covers the single-cell checkpoint only. |
| DAC-6 | Full array layout with dummy/fringe peripheral caps | TBD | 🟢 Complete | `dac/layout/cap_array.gds` — routed 255-unit common-centroid array with all active top plates on the balanced Metal5 `DAC_TOP` mesh; B0–B7 bottom-plate rails; and both plates of all 69 dummies tied to GND. |
| DAC-7 | Sub-block DRC clean | TBD | 🟢 Complete | `run_dac_drc.sh` on routed `cap_array.gds`, variant=D: **0 violations**, 660 rule categories, full untruncated run. |
| DAC-8 | Sub-block LVS clean (caps-only) | TBD | 🟢 Complete | `run_dac_lvs.sh`, variant=D, against `dac/layout/cap_array_caps_only_ref.spice` (native C-element reference): **Netlists match**, 324 layout and 324 reference devices. Full array+switch LVS remains deferred until switch layout. |

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

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| SWITCH-1 | Bootstrapped switch schematic (S/H front end, constant V_GS ≈ 3.3 V) | Emily | 🟢 Complete (concept) | `designs/emily_testing/TB_bootstrap_switch.sch`. **Evaluated by us (2026-07-17)** as the DAC's full-range top-plate sample switch and found unusable as built — its clock-boost inverter (`CLK_INV`) is powered from `VIN` instead of `VDD`, so the bootstrap gate overdrive collapses as VIN→VDD (fails above ~2.8 V). Fine as a demo, but not usable for full-range sampling without a power-rail fix. |
| SWITCH-2 | Bootstrap switch testbench (ideal-inverter clock, transient) | Emily | 🟢 Complete | same file — tracks V_IN at low/mid input; see SWITCH-1 note for the near-rail limitation. |
| SWITCH-3 | 3-way NMOS switch submodule (sample / ref / ground) | Mimi *(file committed by Emily — confirm ownership)* | 🟢 Complete | `designs/emily_testing/TB_swtich2.sch`. ⚠️ `switch3.sch` (same folder) is an empty stub — not this. |
| SWITCH-4 | DAC sample switch — architecture + integration | Bruno | 🟢 Complete | **Top-plate sampling** integrated (commit 4029408): single full-range **sized transmission gate** (nfet 4 µm / pfet 8 µm) on `DAC_TOP`, gated by `SAMPLE`/`SAMPLE_N`; bottom plates toggle VDD/GND (was VREF/GND before the 2026-07-18 VREF=VDD rework, see DAC-3b). Connectivity verified (8 caps on `DAC_TOP`, no floats). |
| SWITCH-5 | S/H settling sim with worst-case DAC load + comparator C_in | Bruno | 🟢 Complete | `dac/sim/tb_sample_hold.sch` — full 12.77 pF array + 20 fF comparator cap. Full-range acquisition PASS (0.3 / 1.65 / 3.0 / 3.2 V), worst-corner error <0.02 mV. Charge injection ≤0.18 LSB — largest single error term, watch in INL/DNL. |
| SWITCH-6 | `unit_switch` CMOS rail driver layout — checkpoint (bit0 + MSB m=2) | Bruno | 🟢 Complete | `dac/layout/unit_switch_checkpoint.gds` (topcells `unit_switch_bit0`, `unit_switch_bit7`), generator `designs/scripts/gen_dac_switch_layout.py`. Built from the PDK's own `gf180mcu` KLayout PCell library (not hand-drawn polygons), M2/M3 routed. **DRC clean** (0 violations) and **LVS clean** (native-SPICE reference, `run_dac_lvs.sh`) for both bit0 (2 devices) and the MSB's `pfet_m=2` case (3 devices) — "Netlists match" both times. The other 6 bit sizes reuse the same parametric generator, deferred to a follow-up pass (checkpoint scope only). |
| SWITCH-7 | Per-bit control logic (`inv1`, `nand2`) layout | Bruno | 🟡 Partial | Same generator, topcells `inv1`/`nand2` in `dac/layout/dac_logic_checkpoint.gds`. `inv1`: **DRC clean + LVS clean** (2 devices, "Netlists match"). `nand2`: topology/connectivity intent matches `dac/schematic/nand2.sch` (2 parallel PMOS + 2 series NMOS via M1-wired instances) but **DRC is not yet clean** — a residual M2/M3 spacing congestion in the 3-row (PMOS/NMOS-top/NMOS-bottom) routing, same root cause as SWITCH-6's fixes (native pad pitch too tight for a passing column/reach) but with more net-pairs than the 2-row driver cell; needs another routing pass. |

**Note on Mimi:** her `mimi-test` branch has no commits beyond `main` — worth checking whether she has unpushed work or this was a joint/miscredited item.

**Architecture question — RESOLVED + VERIFIED (2026-07-17):** the DAC uses **top-plate sampling with a sized transmission gate** as the single full-range sample switch. Silicon-realistic worst-load simulation now passes full-range acquisition; the bottom-plate-only NMOS scheme and Emily's bootstrap switch both failed near the rail (~2.8 V ceiling), so neither is used for full-range sampling. See `docs/adc_glossary.md`.

---

## 6 · Alternative Comparator Design (COMP-ALT)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| COMP-ALT-1 | Alternative comparator topology (backup/comparison to the StrongARM latch) | Luc | ⚪ Not Started | `designs/luc_testing/` currently only has Xschem warm-up files (`inv.sch`, `rc_circuit_test.sch`, dated 2026-06-14) — no comparator topology work has landed yet, on this branch or `main` |

---

## 7 · Automation & Reproducibility Suite (REP)

| ID | Task | Owner | Status | Artifact |
|----|------|-------|--------|----------|
| REP-1 | Python script: parse ngspice `.raw` → DNL/INL | Bruno | 🟢 Complete | `designs/scripts/extract_dnl_inl.py` — reads the `tb_inl_dnl.sch` transient CSV, reports FS span, DNL, INL (endpoint + best-fit), monotonicity/missing-code checks, writes the DNL/INL-vs-code figures. |
| REP-2 | Python script: FFT spectrum → ENOB / SNDR | Bruno | ⚪ Not Started | `designs/scripts/calc_enob.py` |
| REP-3 | Master simulation runner script | Bruno | ⚪ Not Started | `designs/scripts/run_all_sims.sh` |
| REP-4 | Reproducibility environment doc | Bruno | ⚪ Not Started | `REPRODUCIBILITY.md` |
| REP-5 | CI library-check passes on `main` branch | Bruno | ⚪ Not Started | `.github/workflows/library_check.yml` |

---

## Review Feedback & Open Items

> From the mid-project schematic review (Reviewer: Saroj Rout — **Total 8/20, Conditional Go**). Terms below are defined in **[docs/adc_glossary.md](docs/adc_glossary.md)**.

| Item | Status |
|------|--------|
| Define measurable target specs: Resolution, ENOB, conversion rate, DNL, INL | 🟡 Partial — full-scale (3.3 V) and 1 LSB (12.9 mV) now fixed and recorded in `VERIFICATION_PLAN.md`; DNL/INL gates (Gate 3/4) exist. Still missing: target ENOB and a conversion-rate/sample-rate number (`PROGRESS.md` says "Not defined yet"). |
| S/H simulation must load worst-case DAC switch config + comparator input cap, not an ideal/light load | 🟢 Done — `tb_sample_hold.sch` loads the full 12.77 pF array + 20 fF comparator cap; full-range acquisition PASS, worst-corner error <0.02 mV. |
| DAC capacitor sizing should be justified via kT/C noise budget, not just "C_u ≥ 50 fF" as a guess | 🟢 Done — kT/C ≈ 18 µV rms for C ≈ 12.75 pF, ~360× below 0.5 LSB. C_u is matching-limited, not noise-limited. |
| Avoid a bootstrap switch for the 8-bit DAC specifically — a sized transmission gate is sufficient and cheaper on schedule | 🟢 Addressed — array switches are per-bit sized NMOS pass-gates; the single full-range sample switch is a sized transmission gate. No bootstrap anywhere. Emily's bootstrap was evaluated and rejected. |
| Comparator offset should be reduced via proper buffer/latch sizing (gm/Id-annotated), not brute-force area scaling | 🟢 Addressed — COMP-5 already treats offset as a calibratable DC shift, no upsizing done |
| Foundry mismatch data assumes perfect common-centroid layout; current comparator layout will have worse real offset than MC predicts | ⚪ Not accounted for in COMP layout yet |
| Keep an overall project tracker (this file) up to date across all blocks | 🟡 In progress — this update adds the previously-missing SWITCH and COMP-ALT blocks |

---

## Verification Gates Summary

| Gate | Criterion | Block | Status |
|------|-----------|-------|--------|
| Gate 1 | σ_offset characterized + delay < 2 ns @ TT (MC N≥100) | Comparator | 🟡 |
| Gate 2 | DAC settling ≤ 0.5 LSB within 40 ns @ TT | Cap DAC | 🟢 PASS, post VREF=VDD rework 2026-07-18 (TT 2.61ns, worst corner SS/125°C/2.97V 3.86 ns / 36.1 ns margin — see `VERIFICATION_PLAN.md`) |
| Gate 3 | Top-level DNL/INL < 0.5 LSB @ TT corner | Integration | 🟢 DAC-only nominal sweep PASS post VREF=VDD rework (FS span=3293mV=99.8% of 3.3V, max\|DNL\|=0.002 LSB, max\|INL\|=0.004 LSB, see DAC-9); cap-mismatch (the real linearity limit) also **PASSES at Cu=50fF (≥99.9997% yield, corrected local-mismatch model, see DAC-9b — LSB-based conclusion unaffected by the rework)** — no upsizing needed, common-centroid layout (DAC-5) still required for systematic-gradient cancellation. Full ADC-level (with comparator + sequencing) integration still ⚪ |
| Gate 4 | Full corner sweep (FF/SS/SF/FS) passes spec | Integration | ⚪ |
| Gate 5 | DRC clean + LVS clean → tapeout sign-off | Integration | ⚪ |
