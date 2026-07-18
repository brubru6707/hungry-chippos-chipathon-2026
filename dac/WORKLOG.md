# DAC Worklog

## 2026-07-17 — Baseline checkpoint: cap array self-contained under dac/

- **Branch:** `dac-cap-array`, baseline commit `a2c4d7b` ("dac: relocate cap array into self-contained dac/, netlists clean (baseline, switch sizing pending)").
- **Files now under dac/:**
  - `dac/schematic/`: `cap_array.sch/.sym`, `unit_switch.sch/.sym`, `inv1.sch/.sym` (inv1 copied from designs/emily_testing scratch; scratch originals in `designs/libs/core_cap_dac/` and `designs/libs/tb_cap_dac/` were untracked and have been deleted)
  - `dac/sim/`: `tb_cap_array.sch`
- **Netlist status:** `cap_array.sch` netlists clean standalone (xschem -q -x -n in iic-osic-tools container, gf180mcuD). Ports: `VIN VREF VDD SAMPLE B0-B7 DAC_TOP`. Instances: 8x `unit_switch`, 8x `cap_mim_2f0fF` (m=1..128, Cu=50fF at 5u x 5u), 8x `inv1`. `tb_cap_array.sch` also netlists clean; only external symbol refs anywhere are PDK (`symbols/nfet_03v3.sym`, `symbols/pfet_03v3.sym`, `symbols/cap_mim_2f0fF.sym`) + stock ipin/iopin/opin/gnd/lab_wire/vsource/code.
- **LOCKED findings (do not re-derive):**
  - (Q1) Unit-sized switch fails MSB settling: 276 ns vs 40 ns spec. Fix = per-bit switch width W = m*W_unit, m = 1..128. Transmission gate NOT needed.
  - (Q2) Comparator input load is ~2.5 fF; keep the 20 fF placeholder load for now.

NEXT STEP: Brief #3 — implement per-bit switch sizing + build major-carry (0111_1111->1000_0000) Gate-2 settling testbench, measure <6.45mV in <40ns @ TT

## 2026-07-17 — Brief #3: per-bit switch sizing + Gate-2 major-carry PASS @ TT

- **Branch:** `dac-cap-array`, commit `aa7caef` ("dac: per-bit switch sizing (W=2^i*Wunit), Gate-2 major carry settles <40ns @ TT").
- **Connectivity fix (important):** `cap_array.sch` was authored outside Xschem; the `lab=` annotations on wire (`N`) lines are cosmetic only — Xschem netlisted every bit slice as isolated `netN` nodes (caps did NOT share DAC_TOP, ports floated). Added real `lab_wire.sym` components at every dangling endpoint + port hookup wires + gnd on each inv1 DVSS. Netlist now shows caps sharing DAC_TOP, switches on B0-B7/SAMPLE/VIN/VREF, x_inv on VDD/0. The old `tb_cap_array.sch` has the same disease (dangling source grounds, no labels) — treat its old numbers as scratch-derived; `tb_major_carry.sch` is authored with proper labels.
- **Per-bit switch sizing (W-scaling, not multi-finger):** `unit_switch.sym` now declares subckt params `nfet_wid`/`nfet_len` (defaults 0.42u/0.28u); each `x_sw{i}` in `cap_array.sch` passes `nfet_wid=2^i*0.42u`, `nfet_len=0.28u`, nf=1. Chose W-scaling because the nfets already referenced `'nfet_wid'` (ad/as/pd/ps formulas scale with W automatically); layout will finger the wide devices later.
  - x_sw0=0.42u, x_sw1=0.84u, x_sw2=1.68u, x_sw3=3.36u, x_sw4=6.72u, x_sw5=13.44u, x_sw6=26.88u, x_sw7=53.76u (verified on netlist instance lines).
- **Gate-drive check:** B7 -> inv1 -> B7_B (turns off 53.76u GND switch): 0.77 ns to 10% VDD, 0.86 ns to 5% VDD. B6_B rise (turns on 26.88u switch): 0.49 ns. Well under the ~4 ns concern threshold -> inv1 (1.7u/0.85u) left unchanged.
- **Gate-2 major-carry testbench** `dac/sim/tb_major_carry.sch` (TT, 27C, VDD=3.3, VREF=1.65, VIN=1.2, 20fF comparator placeholder on DAC_TOP): sample 0-100n, code 0111_1111 held 600 ns, step to 1000_0000 at t0=700n with 50 ps edges, SAMPLE low (hold). Sanity: v_pre=821.3mV -> v_final=827.8mV, step = +6.44 mV = 1 LSB exactly.
- **Before/after settle (last |V(DAC_TOP)-v_final| crossing of ±6.45 mV after t0):**

  | switches | settle_time | V(DAC_TOP) err @ t0+40n | verdict |
  |---|---|---|---|
  | unit-sized 0.42u (old) | 163.2 ns | −298.0 mV | FAIL |
  | per-bit W=2^i*0.42u (new) | **1.77 ns** | **~0.000 mV** (<1 µV) | **PASS** |

  ACCEPTANCE: settle 1.77 ns < 40 ns AND |err@40n| ~0 < 6.45 mV -> **Gate-2 PASS @ TT** (unsized run done on a scratch netlist copy, not committed).
- NEXT STEP: corners SS/FF (+ temp) on the major-carry tb, then INL/DNL linearity sweep over all 256 codes.

## 2026-07-17 — PVT corner sweep on Gate-2 major-carry tb: PASS across all 30 corners

- **Branch:** `dac-cap-array`, commit `34e727b` ("dac: Gate-2 settling verified across PVT corners; record spec + result").
- **Connectivity guard (re-confirmed before trusting the sweep):** re-netlisted `tb_major_carry.sch` from the repo root (`cd /foss/designs && xschem -q -x -n dac/sim/tb_major_carry.sch`) — netlisting from `dac/sim/` directly breaks the relative symbol path `dac/schematic/cap_array.sym` and silently drops the `x1` instance (`*  x1 -  cap_array  IS MISSING !!!!` in the netlist header comment) — always netlist from `/foss/designs`. Flattened `x1` subckt confirms all 8 caps (`XC0..XC7`, m=1,2,4,8,16,32,64,128) share `DAC_TOP`; every top-level pin (VIN, VREF, VDD, SAMPLE, B0-B7, DAC_TOP) is wired to a real net, no floats.
- **Sweep method:** netlisted `tb_major_carry.sch` once, then for each of 30 PVT combinations did text substitution on the flat spice deck (`.lib ... <corner>` for the digital section, `.temp <T>` inserted before `.control`, `V_VDD` source value) and ran `ngspice -b` directly — same stimulus/measures as the TT run (major-carry step at t0=700n, settle = last crossing of ±6.45mV band around v_final, err at t0+40n).
- **Corners:** process = {typical, ss, ff, sf, fs} (all 5 gf180mcuD corners, not just ss/ff — cheap to run) x temp = {-40C, 27C, 125C} x V_DD = {3.3V, 2.97V (-10%)}. V_REF fixed at 1.65V.

  | corner | temp | V_DD | settle_time (ns) | err@40ns (mV) | verdict |
  |---|---|---|---|---|---|
  | typical | -40C | 3.3V | 1.459 | 0.0000 | PASS |
  | typical | -40C | 2.97V | 1.486 | 0.0000 | PASS |
  | typical | 27C | 3.3V | 1.769 | 0.0000 | PASS |
  | typical | 27C | 2.97V | 1.801 | 0.0000 | PASS |
  | typical | 125C | 3.3V | 2.249 | 0.0001 | PASS |
  | typical | 125C | 2.97V | 2.286 | 0.0000 | PASS |
  | ss | -40C | 3.3V | 1.777 | 0.0000 | PASS |
  | ss | -40C | 2.97V | 1.819 | 0.0000 | PASS |
  | ss | 27C | 3.3V | 2.152 | 0.0000 | PASS |
  | ss | 27C | 2.97V | 2.201 | 0.0000 | PASS |
  | ss | 125C | 3.3V | 2.727 | 0.0000 | PASS |
  | **ss** | **125C** | **2.97V** | **2.784** | **0.0000** | **PASS (worst case)** |
  | ff | -40C | 3.3V | 1.224 | 0.0000 | PASS |
  | ff | -40C | 2.97V | 1.240 | 0.0000 | PASS |
  | ff | 27C | 3.3V | 1.481 | 0.0000 | PASS |
  | ff | 27C | 2.97V | 1.501 | 0.0000 | PASS |
  | ff | 125C | 3.3V | 1.883 | 0.0000 | PASS |
  | ff | 125C | 2.97V | 1.905 | 0.0000 | PASS |
  | sf | -40C | 3.3V | 1.640 | 0.0000 | PASS |
  | sf | -40C | 2.97V | 1.665 | 0.0000 | PASS |
  | sf | 27C | 3.3V | 1.988 | 0.0000 | PASS |
  | sf | 27C | 2.97V | 2.020 | 0.0000 | PASS |
  | sf | 125C | 3.3V | 2.525 | 0.0000 | PASS |
  | sf | 125C | 2.97V | 2.563 | 0.0000 | PASS |
  | fs | -40C | 3.3V | 1.316 | 0.0000 | PASS |
  | fs | -40C | 2.97V | 1.344 | 0.0000 | PASS |
  | fs | 27C | 3.3V | 1.593 | 0.0000 | PASS |
  | fs | 27C | 2.97V | 1.626 | 0.0000 | PASS |
  | fs | 125C | 3.3V | 2.023 | 0.0000 | PASS |
  | fs | 125C | 2.97V | 2.060 | 0.0000 | PASS |

  (settle_time = max of the last ±6.45mV band-crossing times after t0, matching the TT methodology from the previous entry.)

- **Worst-case corner: SS, 125C, V_DD=2.97V** — settle = 2.784 ns, margin to 40 ns spec = **37.22 ns**, err@40ns ≈ 0 mV. Matches expectation that the switch nfet (SS + weakest gate overdrive + highest temp mobility loss) dominates and is slowest here; still >13x margin under spec.
- **ACCEPTANCE: every one of the 30 corners settles <40ns AND |err@40n|<6.45mV -> Gate-2 PASS across TT + full PVT sweep.**
- **Testbench quarantine:** deleted `dac/sim/tb_cap_array.sch` (first-pass, single-bit MSB-only settling check, hand-authored outside Xschem with cosmetic-only `lab=` annotations — netlisted with disconnected nodes, same disease as the pre-fix `cap_array.sch` described in the 2026-07-17 Brief #3 entry above). `tb_major_carry.sch` is the sole, authoritative Gate-2 testbench going forward.
- **Docs:** `VERIFICATION_PLAN.md` created with the DAC spec block (FS 3.3V, 1 LSB=12.9mV, Gate-2=0.5LSB/6.45mV settle <40ns) and Gate-2 PASS status; `PROGRESS.md` DAC-3/DAC-4 rows and the Gate 2 summary line flipped to PASS.

NEXT STEP: Brief #5 — in-cell SAMPLE gating to kill sampling contention (bN = bit AND /SAMPLE, bN_bar = /bit AND /SAMPLE), keep 8-bit interface; then S/H sim; then INL/DNL over 256 codes.

## 2026-07-17 — Brief #5: in-cell SAMPLE gating removes sampling contention

- **Branch:** `dac-cap-array`, commit `02a5400` ("dac: in-cell SAMPLE gating removes sampling contention (bN=B&/SAMPLE, bN_bar=/B&/SAMPLE); 8-bit interface unchanged"). Worklog commit follows this one.
- **The bug:** during SAMPLE=1, `unit_switch`'s M1 ties the bottom plate to VIN, but `bN_bar` was `NOT bN` unconditionally (plain `inv1`, no SAMPLE awareness) — so one of M2 (VREF side)/M3 (GND side) was always on too, fighting VIN through M1. Fixed with in-cell gating, `cap_array.sch`'s 8-bit port list (`VIN VREF VDD SAMPLE B0-B7 DAC_TOP`) unchanged.
- **Gate realization chosen:** exactly the suggested Option A layout, no deviation. Per bit i: `bN_bar{i} = NOR2(B{i}, SAMPLE)` (direct 1-gate replacement of the old inv1, same downstream net `B{i}_B`). `bN{i} = AND2(B{i}, SAMPLE_N)` built as `NAND2(B{i}, SAMPLE_N)` -> `inv1` (reusing the existing inv1 cell as the second stage), output on a **new** net `B{i}G` — this required rewiring `unit_switch`'s `bN` pin from the raw `B{i}` net to `B{i}G` (the one topology change vs. before). `SAMPLE_N = NOT SAMPLE` is generated **once** by a single shared `inv1` instance (`x_sampinv`) and fanned out to all 8 NAND2 "b" inputs, saving 7 inverters vs. per-bit SAMPLE inversion.
- **New cells** (`dac/schematic/nand2.sch/.sym`, `dac/schematic/nor2.sch/.sym`), authored in the same hand-coordinate style as `inv1.sch` (PDK `nfet_03v3`/`pfet_03v3` symbols, standard ad/as/pd/ps formulas, `spiceprefix=X`), parameterized like `unit_switch` (`nfet_wid`/`pfet_wid`/`nfet_len`/`pfet_len` subckt params, so any bit's gate can be upsized later without touching the cell definition):
  - `nand2`: 2 parallel PMOS (source=DVDD, drain=y, gates=a/b) at normal inv1 pfet width (default `pfet_wid=1.7u`); 2 series NMOS (top: drain=y gate=a source=mid; bottom: drain=mid gate=b source=DVSS) at `nfet_wid=1.7u` (2x the single-inverter 0.85u, per spec, to compensate series R).
  - `nor2`: 2 parallel NMOS (source=DVSS, drain=y, gates=a/b) at `nfet_wid=0.85u` (normal); 2 series PMOS (top: source=DVDD gate=a drain=mid; bottom: source=mid gate=b drain=y) at `pfet_wid=3.4u` (2x the single-inverter 1.7u).
  - **Connectivity technique (new wrinkle vs. prior files):** these two cells use **zero drawn `N` wires** — every transistor pin gets a `lab_wire.sym` placed at its exact computed absolute coordinate (derived and cross-checked against `inv1.sch`/`unit_switch.sch`'s existing, already-working transistor placements: for `nfet_03v3`/`pfet_03v3` at rot0/flip0, `G=(ox-20,oy)`, nfet `D=(ox+20,oy-30)` `S=(ox+20,oy+30)`, pfet `D=(ox+20,oy+30)` `S=(ox+20,oy-30)`, bulk `B=(ox+20,oy)` always tied to the local supply rail, not to internal series nodes), and cell ports use `ipin`/`opin`/`iopin` placed anywhere convenient (confirmed these need not touch anything geometrically — they merge into the sheet-wide `lab=` alias exactly like `lab_wire.sym`, matching the pattern already documented for `cap_array.sch`'s top-level ports). Verified correct by inspecting the flattened netlist: `.subckt nand2 DVDD a b y DVSS ...` / `.subckt nor2 DVDD a b y DVSS ...` came out with exactly the intended transistor topology and no stray auto-generated `netNN` nodes.
- **`cap_array.sch` per-bit rewiring:** for each bit i, removed the old `x_inv{i}` plain inverter and its 5 associated connectivity lines; added `x_nor{i}` (a=B{i}, b=SAMPLE, y=B{i}_B, unchanged downstream), `x_nand{i}` (a=B{i}, b=SAMPLE_N, y=B{i}NAND), `x_andinv{i}` (vin=B{i}NAND, vout=B{i}G); relabeled the wire/`lab_wire.sym` feeding `unit_switch`'s `bN` pin from `B{i}` to `B{i}G`. Added one shared `x_sampinv` (vin=SAMPLE, vout=SAMPLE_N). Programmatic diff (Python script over the regular 8x-repeated block) removed exactly 72 lines and modified exactly 24 across the 8 bits, matching hand-derived expectations exactly before writing back.
- **CONNECTIVITY GUARD: PASS.** Re-netlisted `tb_major_carry.sch` from repo root. Flattened `.subckt cap_array`: all 8 caps (`XC0..XC7`, m=1,2,4,8,16,32,64,128) still share `DAC_TOP`; every top-level port (VIN VREF VDD SAMPLE B0-B7 DAC_TOP) wired to a real net (confirmed via the `x1 VIN VREF VDD SAMPLE B0 ... DAC_TOP cap_array` instance line). New gate instances show real, purposeful node names on every pin (e.g. `x_nor0 VDD B0 SAMPLE B0_B 0 nor2`, `x_nand0 VDD B0 SAMPLE_N B0NAND 0 nand2`, `x_andinv0 VDD B0NAND B0G 0 inv1`) — no floating/auto-generated `netNN` names anywhere in the new gates (the only `netN` names present, `net1..net8`, are the pre-existing, correctly-connected bottom-plate nodes, unchanged from before).
- **Truth-table verification (new `dac/sim/tb_gate_truth.sch`, DC-style PWL steps through all 4 (SAMPLE,B) combinations, bit0 and bit7 probed via `x1.B0G`/`x1.B0_B`/`x1.B7G`/`x1.B7_B`):**

  | SAMPLE | B | bN (B{i}G) | bN_bar (B{i}_B) | expected | bit0 | bit7 |
  |---|---|---|---|---|---|---|
  | 1 | 0 | 0 | 0 | both LOW | 6.6nV / 6.8nV | 6.6nV / 6.8nV |
  | 1 | 1 | 0 | 0 | both LOW | 30nV / 23.8µV | 29nV / 23.9µV |
  | 0 | 0 | 0 | VDD | bN=B, bN_bar=/B | 8.7nV / 3.300V | 6.9nV / 3.300V |
  | 0 | 1 | VDD | 0 | bN=B, bN_bar=/B | 3.300V / 107µV | 3.300V / 123µV |

  All values within a few tens of nV to ~100µV of ideal 0/3.3V — **PASS**, matches spec truth table exactly for both bits.
- **Contention proof (before/after), SAMPLE=1, B=1, measured via branch current of `V_VREF`/`V_VIN` on a scratch flattened-netlist copy with the OLD plain-`inv1` `cap_array` subckt reconstructed by text substitution — no files under `dac/` were used to represent the old behavior, per instructions):**

  | design | i(V_VREF) | i(V_VIN) | verdict |
  |---|---|---|---|
  | OLD (plain inv1, bN=B direct) | **-4.10 mA** | **-9.82 mA** | crowbar current confirmed (VIN/VREF sources fighting through M1+M2, both on) |
  | NEW (SAMPLE-gated) | **-15.4 pA** | **-126 pA** | leakage only — **contention eliminated (~5-6 orders of magnitude reduction)** |

- **MSB gate-drive delay regression (B7, the largest/slowest 53.76u switch load), `tb_major_carry.sch`, TT/27C/3.3V:** `bN_bar` path (B7_B fall, via new `nor2`): 0.86ns/0.96ns (10%/5% VDD) vs. 0.77ns/0.86ns pre-gating — small increase from the extra gate, as expected. New `bN` path (B7G rise, via `nand2`+`inv1`, 2 extra stages): 0.66ns/0.72ns (90%/95% VDD). Bit6 `bN_bar` delay: 0.54ns (vs. 0.49ns pre-gating). All comfortably under the ~4ns informal threshold — **no gate upsizing needed** for bit 7 (the `nand2_wid`/`nor2_wid` params exist precisely so this could be done per-instance later if a corner ever demanded it, but it isn't needed now).
- **Gate-2 regression (`tb_major_carry.sch`, unmodified stimulus/measures):**

  | corner | settle_time before | settle_time after | delta | err@40n before | err@40n after | margin to 40ns spec | verdict |
  |---|---|---|---|---|---|---|---|
  | TT / 27C / 3.3V | 1.769 ns | **1.856 ns** | +0.087 ns | 0.0000 mV | **0.0000 mV** | 38.14 ns | PASS |
  | SS / 125C / 2.97V (worst corner) | 2.784 ns | **3.819 ns** | +1.035 ns | 0.0000 mV | **0.0000 mV** | 36.18 ns | PASS |

  Both corners settle well under the 40ns spec with >36ns margin (>9x); the worst-corner delta (+1.035ns) is marginally over the informal "<1ns" expectation but is two extra static-CMOS gate stages' worth of delay at the slowest PVT corner and does not threaten the spec in any way. **Gate-2 PASS at both corners.**

NEXT STEP: Brief #6: real sample-and-hold sim (SAMPLE high->sample VIN, SAMPLE low->convert), measure S/H accuracy incl. kT/C noise; then INL/DNL sweep over 256 codes.

## 2026-07-17 — Brief #6: sample-and-hold characterization — acquisition FAILS near full-scale (architectural gap, not sizing)

- **Branch:** `dac-cap-array`, commit (this entry's HEAD after committing `dac/sim/tb_sample_hold.sch` + `dac/sim/tb_ktc_noise.sch`). New, standalone S/H analysis — first time this array has been driven with a real acquire/hold cycle instead of a fixed hold-phase code.

- **Step 0a — topology (inspected, not assumed): there is NO top-plate switch anywhere in this design.** Grepped every `.sch` in the repo for `DAC_TOP` — it appears only in `cap_array.sch` (the 8 cap top plates + the `DAC_TOP` opin, wired with plain `N`/`lab_wire` nets, zero switch/transistor components on that node) and the two DAC testbenches. No top-level integration schematic connecting `DAC_TOP` to the comparator exists yet either. `docs/adc_glossary.md`'s own "S/H simulation" section already flags this as an **open, unreconciled design question**: Max's `unit_switch` (bottom-plate-only sampling, what's actually built) vs. Emily's bootstrap switch (`designs/emily_testing/`, a *top-plate* sampling architecture, currently unused/orphaned). `DAC_TOP` is a purely passive, floating node — its voltage during "sample" is whatever charge-conservation dictates given the bottom-plate switching, not a driven/reset value. Sampling is 100% bottom-plate: SAMPLE=1 ties every bit's bottom plate straight to VIN via `unit_switch`'s M1 (in-cell SAMPLE-gated, contention-free per commit `02a5400`).
- **Step 0b — no sample-rate/conversion-rate/acquisition-time budget exists.** `VERIFICATION_PLAN.md` only has Gate 2 (settling <40ns per bit-trial); `PROGRESS.md` explicitly lists conversion rate as "⚪ Not defined yet — currently only DNL/INL gates (Gate 3/4) exist; no target ENOB or conversion-rate number is written down anywhere." `docs/adc_glossary.md` gives only an *illustrative, non-binding* example (10 MHz SAR clock / 9 cycles ≈ 1.1 MS/s → ~100 ns/cycle) — not an approved spec. Per the task instructions, proceeded without inventing an official budget; acquisition times below are reported on their own merits (and are, where they pass, >50x faster than that illustrative 100 ns/cycle figure for reference only).

- **`dac/sim/tb_sample_hold.sch`** (new, standalone, not derived from `tb_major_carry.sch`'s stimulus): 0-20n clean pre-sample state (SAMPLE=0, code=0 → bottom plates + DAC_TOP settle to 0V, a well-defined DC start point). 20n SAMPLE→1 (acquire) for 150n. 170n SAMPLE→0 (hold), code held at 0 for the rest of the run (bottom plates → GND). `VIN_TARGET`/`VDD_VAL` are `.param`s; swept via text substitution on the flat netlist (same technique as the PVT sweep, not re-netlisted per run) across VIN={0.3, 1.65, 3.0}V x corner={TT/27C/3.3V, SS/125C/2.97V}. **Connectivity guard: PASS** — re-netlisted from repo root, flattened `x1` line confirms all 8 caps share `DAC_TOP`, B0-B7 tied to a real ground net (not floating), VIN/VREF/VDD/SAMPLE on real sources.
- **Methodology note:** ngspice `.measure ... WHEN ... CROSS=LAST` proved fragile at this signal's very small overshoot-free settling profile (spurious/missing crossings). Switched to `wrdata`-based transient dump + direct Python post-processing (finds the first time the signal enters the ±6.45mV band around its own end-of-acquire value *and stays there*) — more robust and transparent; used for all numbers below.

- **Acquisition results (settle = time after SAMPLE↑ to enter and hold the ±6.45mV/0.5LSB band around the value DAC_TOP itself reaches at end of the 150ns acquire window; gap_to_vin = that end value minus the literal VIN target, i.e. the residual error against the real target rather than against its own asymptote):**

  | VIN target | corner | acquire settle | v_acq_final | gap to VIN target | verdict |
  |---|---|---|---|---|---|
  | 0.3 V | TT/27C/3.3V | 1.25 ns | 0.29957 V | −0.43 mV | PASS |
  | 0.3 V | SS/125C/2.97V | 1.43 ns | 0.29957 V | −0.43 mV | PASS |
  | 1.65 V | TT/27C/3.3V | 1.51 ns | 1.64763 V | −2.37 mV | PASS |
  | 1.65 V | SS/125C/2.97V | 1.81 ns | 1.64763 V | −2.37 mV | PASS |
  | 3.0 V | TT/27C/3.3V | (120 ns, still crawling — see below) | 2.82008 V | **−179.9 mV** | **FAIL** |
  | 3.0 V | SS/125C/2.97V | (127 ns, still crawling) | 2.81038 V | **−189.6 mV** | **FAIL** |

  **Root cause of the VIN=3.0V failure (a second architectural gap, distinct from 0a): NMOS-only bottom-plate switch loses gate overdrive near VDD.** `unit_switch`'s M1 is a single NMOS pass transistor with its gate tied to SAMPLE (=VDD=3.3V when sampling). As the bottom plate charges up toward VIN, M1's own Vgs = VDD − V_bottomplate shrinks; conduction collapses once V_bottomplate approaches VDD − Vth_n (~2.8V, matching the simulated ceiling almost exactly: TT gives 2.820V, SS/125C — higher Vth from the slow corner — gives an even lower 2.810V, precisely the expected direction). This is not a settling-time problem fixable by waiting longer or resizing switches: **2.82V is a hard ceiling** the single-NMOS switch asymptotically approaches via ever-slower subthreshold conduction, never actually reaching 3.0V. 28-29 LSBs of error at the top of the range is a real, silent accuracy failure, not a corner-case rounding issue. Note this directly resolves *part of* the open design question in `docs/adc_glossary.md`: Emily's bootstrapped switch (`designs/emily_testing/`, already built, gives "constant V_GS ≈ 3.3V" regardless of input level) is the textbook fix for exactly this failure mode — worth resurrecting rather than inventing a transmission-gate fix from scratch. **Did not attempt a fix here** — out of scope per instructions (no switch/cap/gate resizing), flagging only.

- **Step 2 — hold droop, 320ns conversion window (8 bits x 40ns Gate-2 ceiling, conservative proxy given no committed conversion-rate spec):** code held constant at 0 through the whole hold phase; `v_hold_ref` sampled at hold_start+50ns (safely past Gate-2's own few-ns charge-redistribution settling transient, isolating pure leakage drift afterward) vs. `v_hold_end` 320ns later.

  | VIN target | corner | droop over 320ns window |
  |---|---|---|
  | 0.3 V | TT/27C/3.3V | −2.1e-9 mV |
  | 0.3 V | SS/125C/2.97V | −6.9e-9 mV |
  | 1.65 V | TT/27C/3.3V | −2.9e-9 mV |
  | 1.65 V | SS/125C/2.97V | −6.2e-9 mV |
  | 3.0 V | TT/27C/3.3V | −7.6e-9 mV |
  | 3.0 V | SS/125C/2.97V | −2.1e-7 mV (worst) |

  Worst droop (SS/125C/2.97V) is 2.1e-7 mV ≈ 3.2e-8 x 0.5 LSB — computationally indistinguishable from zero at this precision. **Hold droop PASS by an enormous margin at both corners; off-device subthreshold leakage is not a practical concern for this design on a 320ns timescale.**

- **Step 3 — kT/C sampling noise.** Analytical: C_sample ≈ full array ≈ 255×C_u = 255×50fF = 12.75pF; kT = 1.380649e-23 × 300K = 4.142e-21 J → **V_noise,rms = sqrt(kT/C) = 18.0 µV rms**, matching the ~18µV ballpark exactly.
  New `dac/sim/tb_ktc_noise.sch`: SAMPLE held DC-high (steady acquire operating point, all 8 M1 in triode, M2/M3 off), `V_VIN` carries `ac=1` for the transfer function, `.noise v(DAC_TOP) V_VIN dec 20 1 100g` — ngspice's transistor-level cross-check gives **onoise_total = 97.8 µV rms**, ~5.4x the idealized figure. Traced the gap: **not flicker/1/f noise** — re-running the integral starting at 10 kHz instead of 1 Hz (well past the observed 1/f knee around 1 kHz in the raw spectrum) changes the total by <0.1%. The excess is the **8-parallel-branch topology**: 8 independent R_i-C_i thermal noise sources (very different per-branch resistances, R_i ∝ 1/2^i, converging on one shared floating node) departing from the textbook single-R/single-C assumption behind the `sqrt(kT/C)` mnemonic — a real, second-order effect of this specific binary-weighted array, not a simulation error. **Either number clears the bar comfortably:** 6.45mV / 97.8µV ≈ 66x margin using the conservative (larger) transistor-level number. **kT/C noise PASS — confirms C_u is matching-limited, not noise-limited, either way.**

- **Overall S/H verdict: FAIL — blocked on the VIN=3.0V acquisition ceiling.** Hold droop and kT/C noise both pass with huge margin; acquisition passes cleanly at 0.3V and 1.65V. The near-full-scale failure is a genuine architectural gap (NMOS-only bottom-plate pass-switch, ~28 LSB error, hard ceiling not a slow-settling issue) layered on top of the already-flagged missing-top-plate-switch gap from Step 0a — both trace back to the same unresolved "Max's bottom-plate scheme vs. Emily's bootstrap scheme" question in `docs/adc_glossary.md`. Flagging both for a team decision rather than silently working around them.

NEXT STEP: resolve the S/H architecture question (bottom-plate-only vs. reviving Emily's bootstrap switch for near-rail acquisition) before trusting any full-range (0-3.3V) conversion result; once resolved, Brief #7: INL/DNL linearity sweep over all 256 codes (can proceed now for the sub-2.8V range where acquisition is proven to work, but full-scale codes should be treated as suspect until the switch gap is addressed).

## 2026-07-17 — Brief #9 checkpoint: top-plate switch device evaluation (bootstrap vs TG) — DECISION: build a sized TG, do not adopt the bootstrap switch

- **DECISION (approved, this session):** move to top-plate sampling — one full-range switch between VIN and DAC_TOP, closed on SAMPLE=1; all bottom plates driven to GND during sample; bottom plates switch VREF/GND per bit during convert (bN=B, bN_bar=NOT B, no more SAMPLE gating needed on the bottom plates). This checkpoint covers Step 1 only (device evaluation) — **integration (Steps 2-4) has NOT started**, per instructions to stop and report if the bootstrap switch proved fundamentally unusable.

- **Recon: `designs/emily_testing/` is not a reusable subckt.** `TB_bootstrap_switch.sch` (the file that actually contains the bootstrap transistors — confusingly, `switch3.sch` is a near-empty stub with sources but no switch devices, likely abandoned scratch) is authored as a monolithic testbench: `VIN`/`VCLK`/`VDD` sources are wired directly to internal nodes with no `ipin`/`opin` ports at all. There is nothing to instantiate as-is; using it means either extracting the device-level netlist into a proper subckt (what this eval does) or rebuilding the schematic with ports from scratch.

- **Method:** netlisted `TB_bootstrap_switch.sch` via `xschem -q -x -n` from `/foss/designs` to get xschem's own flattened device netlist (`/headless/.xschem/simulations/TB_bootstrap_switch.spice`), then hand-wrapped the transistor-level content (M1,M3-M8,C2, and the `x1` CLK→CLK_INV inverter) into a ported `.subckt bootstrap_sw VIN VOUT CLK VDD DVSS`, replacing Emily's tiny 2fF test cap with a lumped 12.77pF load (255×50fF array + 20fF comparator placeholder — valid stand-in for the real `cap_array` during SAMPLE, since with the new bottom-plates-to-GND scheme every cap sits simply from DAC_TOP to ground). Full deck committed at `dac/sim/eval_bootstrap_switch.spice`; VIN swept 0.3/1.65/3.0/3.2V by text substitution, TT/27C/3.3V only (Step 1 recon, not the full corner sweep — that's Step 3 territory and only applies once/if a device is chosen and integrated).

- **False start (a real bug in my own evaluation, not Emily's schematic):** the `x1` inverter that generates `CLK_INV` for the M8 bootstrap-pump gate is powered from `VIN`, not `VDD` (`DVDD=VIN` in Emily's netlist). This reads exactly like a wiring mistake, so the first pass "fixed" it to `DVDD=VDD` — that change makes the switch **never turn on at all, at any VIN** (`VBS` sits at ~0V through the whole transient, `VOUT` never moves off its reset value even against a light 2fF load). Reverting to the original `DVDD=VIN` wiring restored correct bootstrapping. Lesson: the VIN-referenced supply is load-bearing for this specific topology, not a bug — don't "fix" it if this subckt is ever reused.

- **Result with the load-bearing wiring restored, driving the real 12.77pF load:**

  | VIN target | v_final | error vs target | settle to 0.5LSB band | verdict |
  |---|---|---|---|---|
  | 0.3 V | 0.29998 V | −0.25 mV | 330.6 ns | PASS |
  | 1.65 V | 1.64998 V | −0.02 mV | 838.8 ns | PASS |
  | 3.0 V | 0.3706 V | **−2629.4 mV** | never settles (times out) | **FAIL** |
  | 3.2 V | 0.3660 V | **−2834.0 mV** | never settles (times out) | **FAIL** |

  Charge injection at switch turn-off (VOUT step measured right at the CLK-opens edge) is negligible for the passing cases: −25 µV (VIN=0.3V), −20 µV (VIN=1.65V) — not a concern either way.

- **Root cause of the 3.0V/3.2V failure (traced via internal node probes, `xsw.vbs`/`xsw.vc`/`xsw.clk_inv`): the same near-rail Vgs-collapse failure mode we are trying to escape, just relocated to a different node.** `M8` (pfet, `S=Vc, G=CLK_INV, D=VBS`) is the device that pumps the bootstrap cap's charge onto `VBS`; it needs `Vsg = Vc − CLK_INV` above ~|Vtp| to conduct. `Vc` sits at VDD (3.3V, precharged by M7). But because `CLK_INV`'s inverter is powered from `VIN` (see above), `CLK_INV`'s high level *is* VIN — so as VIN approaches VDD, `Vc − CLK_INV → VDD − VIN → 0`. At VIN=1.65V this gives M8 a healthy 1.65V of overdrive and VBS pumps up to ~3.7V (Vgs on the sampling FET M6 ≈ 2.05V, plenty). At VIN=3.0V, M8's overdrive collapses to ~0.3V — too little to conduct — so VBS never rises past ~0.82V, M6's Vgs stays deeply negative, and the switch simply never turns on. This is structurally the same class of bug as the original bottom-plate-NMOS ceiling (a single-ended pass device losing gate overdrive as its source approaches VDD), just moved from M6 (bottom-plate case) to M8 (this bootstrap pump). Fixing it for real would mean redesigning the CLK_INV generation (e.g. a proper VDD-referenced level shifter instead of a VIN-supplied inverter) without breaking the low-VIN behavior that currently depends on it — a real analog redesign, not a parameter tweak.

- **Additional reasons against adopting as-is even where it does pass:** every device is minimum-size (W=0.22u/L=0.28u), validated by Emily only against a ~2fF test load — 3-4 orders of magnitude lighter than the real 12.77pF array. Where it works it's already slow (330-840ns to settle a fixed DC level with the real load — no established acquisition-time budget exists yet per Brief #6, but this is far slower than the sub-2ns settling the existing per-bit switches achieve), and speeding it up would require re-sizing the whole bootstrap pump network (M1/M5/M7/M8 and the C2 pump cap ratio), which is unvalidated territory.

- **DECISION: build a sized transmission gate (NMOS+PMOS in parallel) in `dac/schematic/` instead of adopting the bootstrap switch.** Rationale: a TG's complementary devices don't share a single near-rail collapse mode — the PMOS conducts well exactly where the NMOS's Vgs collapses (near VDD) and vice versa near GND — so it doesn't reproduce either failure mode seen above (the original bottom-plate ceiling or this session's M8-pump ceiling). It also reuses the exact hand-coordinate/`lab_wire` authoring style and PDK symbols (`nfet_03v3`/`pfet_03v3`) already proven to netlist cleanly in this repo (`inv1.sch`, `nand2.sch`, `nor2.sch`, `unit_switch.sch`), versus productizing (add ports, fix the CLK_INV generation, resize the whole pump network) an unfamiliar multi-stage analog block under this session's remaining budget.

- **Stopping here per instructions.** This entry closes Step 1 only. Step 2 (add the TG top-plate switch, rework bottom-plate control to the revised SAMPLE=1→bN=0 truth table, remove VIN from the bottom-plate switches) is NOT started.

## 2026-07-17 — Brief #10: TG top-plate switch integrated — full-range VIN acquisition PASS

- **Branch:** `dac-cap-array`, commit `4029408` ("dac: top-plate sampling via sized TG (4u/8u) — full-range VIN acquisition PASS"). Closes Steps 1-4 of the Brief #9 top-plate-sampling plan.

- **Step 1 — TG cell (`dac/schematic/tgate.sch`/`.sym`, new):** parallel `nfet_03v3` (gate=SAMPLE) + `pfet_03v3` (gate=SAMPLE_N), parameterized `nfet_wid`/`pfet_wid`/`nfet_len`/`pfet_len` like `unit_switch`/`nand2`/`nor2`. Pins `A B SAMPLE SAMPLE_N DVDD DVSS` (A/B both `iopin` — bidirectional switch, not a fixed-direction pass gate). Authored with the established pin-coincident `lab_wire.sym` convention (zero drawn `N` wires); netlisted standalone (`xschem -q -x -n dac/schematic/tgate.sch`) and hand-verified against the coordinate formulas in the Brief #5 entry: `XM1 A SAMPLE B DVSS nfet_03v3`, `XM2 B SAMPLE_N A DVDD pfet_03v3` — correct TG topology, no floats.
- **Sizing sweep** (`dac/sim/eval_tgate.spice`, standalone ngspice deck, ideal complementary SAMPLE/SAMPLE_N sources driving the TG into a lumped 12.77pF load = 255×50fF array + 20fF comparator placeholder, same load model as the Brief #9 bootstrap eval): swept `nfet_wid`/`pfet_wid` at VIN={0.3,1.65,3.0,3.2}V × corner={TT/27C/3.3V, SS/125C/2.97V}. Worst case across the whole sweep is always VIN=1.65V (mid-rail, where neither device has maximal overdrive) at SS/125C/2.97V.
  - 4u/8u (nfet/pfet) chosen over 6u/12u specifically to **balance speed vs charge injection** per instructions: 6u/12u settles faster (worst-case 51ns) but injects up to 0.26 LSB at VIN=3.2V; 4u/8u settles in 77ns (still comfortably inside the 50-100ns target) while capping injection at ~0.18 LSB — better margin against the 0.5 LSB budget for the same qualitative acquisition-speed outcome.
  - **Final sizing: nfet_wid=4u, nfet_len=0.28u, pfet_wid=8u, pfet_len=0.28u.** Ron (fitted from the RC charging time constant, tau=Ron·C) ranges ~294-1098Ω across VIN/corner — worst (highest) Ron at VIN=1.65V/SS/125C/2.97V.

  | VIN | TT/27C/3.3V settle | TT Ron | SS/125C/2.97V settle | SS Ron |
  |---|---|---|---|---|
  | 0.3V | 21.2ns | 444Ω | 25.0ns | 527Ω |
  | 1.65V | 44.5ns | 774Ω | **76.99ns (worst)** | **1098Ω (worst)** |
  | 3.0V | 54.1ns | 826Ω | 61.1ns | 1054Ω |
  | 3.2V | 51.4ns | 816Ω | 56.8ns | 1021Ω |

- **Step 2 — integration into `cap_array.sch`:** TG instance `x_tg` wired `A=VIN, B=DAC_TOP, SAMPLE=SAMPLE, SAMPLE_N=SAMPLE_N` (reusing the existing shared `x_sampinv`), `DVDD=VDD`, `DVSS=0`. `unit_switch.sch`/`.sym`: removed `M1` (the old VIN pass-nfet) and its `VIN`/`SAMPLE` pins entirely — bottom plate now only ties to VREF (M2, gate=bN) or GND (M3, gate=bN_bar); `unit_switch` netlists down to 2 transistors, 5 pins (`VOUT bN bN_bar VREF GND`).
  - **Control-logic simplification (not just a rewire):** with M1 gone there is no more sampling-phase bottom-plate contention to gate against, so the Brief #5 `bN_bar = NOR2(B, SAMPLE)` construction is now *wrong* for the new truth table (`SAMPLE=1: bN_bar=1`, not 0) and was replaced — **not with a new gate, but by reusing the existing NAND2 output directly**: `bN_bar{i} = NAND2(B{i}, SAMPLE_N)` (previously only an intermediate signal feeding `bN` via `inv1`). Truth check: SAMPLE=1 → SAMPLE_N=0 → NAND(B,0)=1 for any B (bottom plate → GND, matches spec) ✓; SAMPLE=0 → SAMPLE_N=1 → NAND(B,1)=NOT B (matches spec) ✓. Since `bN = INV(bN_bar)` always (same `x_andinv{i}` stage as before), `bN` and `bN_bar` are now true complements unconditionally — exactly the simplification the new spec implies. **All 8 `nor2` instances (and their `lab_wire`/`gnd` helpers, 6 lines × 8) were deleted**; `unit_switch`'s `bN_bar` pin is rewired straight to the pre-existing `B{i}NAND` net (a lab-rename only, zero new gates).
- **Testbench net-name fixups (required, not optional):** `tb_major_carry.sch`'s gate-drive probes (`v(x1.B7_B)`, `v(x1.B6_B)`) referenced the now-deleted `nor2` output nets — renamed to `v(x1.B7NAND)`/`v(x1.B6NAND)` (same electrical signal/polarity as before, just relabeled, per the truth-table equivalence above).
- **`tb_sample_hold.sch` simulation-setup fix (found via a wrong first-pass number, not assumed):** without `uic`, ngspice's default DC operating-point solve is a **true t=∞ steady state** — since the TG's off-state leakage is now the *only* resistive path to `DAC_TOP` (the caps block DC current to the grounded bottom plates), any finite off-leakage still forces zero net current at DC equilibrium, which pins `V(DAC_TOP)=VIN` exactly *before the transient even starts*, independent of SAMPLE's t=0 value. First-pass numbers showed a suspiciously fast "8ns acquisition settle" that turned out to be the solver re-entering a band it was already inside. Fixed with `.ic v(DAC_TOP)=0` + `tran ... uic` so the transient genuinely exercises the TG's charging path from a cold start (matches the discipline already used in `eval_tgate.spice`).

- **Step 3a — connectivity guard: PASS.** Re-netlisted `tb_major_carry.sch` from repo root; flattened `cap_array` subckt shows `x_tg VIN DAC_TOP SAMPLE SAMPLE_N VDD 0 tgate`, all 8 caps (`XC0-XC7`) still share `DAC_TOP`, every top-level pin (VIN VREF VDD SAMPLE B0-B7 DAC_TOP) on a real net — no floats.

- **Step 3b — full-range acquisition (`tb_sample_hold.sch`, 20-170ns SAMPLE-high window, own-final-value settle convention as Brief #6): ALL PASS, including the previously-failing 3.0V/3.2V cases:**

  | VIN target | corner | acquire settle | v_final | err vs VIN target | verdict |
  |---|---|---|---|---|---|
  | 0.3 V | TT/27C/3.3V | 23.90 ns | 0.300000 V | 0.00 mV | PASS |
  | 0.3 V | SS/125C/2.97V | 34.02 ns | 0.300000 V | 0.00 mV | PASS |
  | 1.65 V | TT/27C/3.3V | 49.71 ns | 1.650000 V | 0.00 mV | PASS |
  | 1.65 V | SS/125C/2.97V | 75.24 ns | 1.649980 V | −0.02 mV | PASS |
  | **3.0 V** | TT/27C/3.3V | 60.39 ns | 3.000000 V | 0.00 mV | **PASS** |
  | **3.0 V** | SS/125C/2.97V | **78.62 ns (worst)** | 2.999987 V | −0.013 mV | **PASS** |
  | **3.2 V** | TT/27C/3.3V | 57.43 ns | 3.200000 V | 0.00 mV | **PASS** |
  | **3.2 V** | SS/125C/2.97V | 73.72 ns | 3.199995 V | −0.005 mV | **PASS** |

  This directly resolves the Brief #6 finding (NMOS-only bottom-plate switch hit a hard ~2.82V ceiling, 28-29 LSB error, never reaching 3.0V/3.2V at all) and the Brief #9 bootstrap-switch finding (same near-rail Vgs-collapse failure relocated to the CLK_INV pump, also never settling above ~0.37V for VIN≥3.0V). Worst-case settle across the whole sweep is 78.62ns — inside the 50-100ns target with ~21ns margin. Hold droop (measured 220n→540n, same 320ns conservative window as Brief #6): all corners ≤0.013 mV, i.e. still practically zero — unaffected by the topology change.

- **Step 3c — charge injection (turn-off transient, v(DAC_TOP) at SAMPLE-fall ±: real integrated circuit, real `x_sampinv`-driven SAMPLE_N, not the idealized sizing-eval sources):**

  | VIN | TT/27C/3.3V | SS/125C/2.97V |
  |---|---|---|
  | 0.3 V | −0.28 mV (0.044 LSB) | −0.35 mV (0.055 LSB) |
  | 1.65 V | +0.23 mV (0.036 LSB) | +0.18 mV (0.028 LSB) |
  | 3.0 V | +1.15 mV (0.178 LSB) | +0.79 mV (0.122 LSB) |
  | 3.2 V | +1.16 mV (0.180 LSB) | +0.79 mV (0.122 LSB) |

  Worst case 0.18 LSB (VIN=3.2V, TT) — comfortably inside the 0.5 LSB budget (≥0.32 LSB margin left for every other error source combined) but **not negligible**: it consumes roughly a third of the total error budget at full-scale codes and is the single largest identified error term in this design (vs. ~0.003-0.015 LSB for kT/C noise per Brief #6). **Flagging, not fixing:** candidate for a dummy/compensation switch if INL/DNL characterization (next step) shows it biting; matches the instruction not to over-engineer this now.

- **Step 3d — Gate-2 major-carry regression (`tb_major_carry.sch`, same 0111_1111→1000_0000 stimulus, unmodified spec: settle <40ns, err@40ns <6.45mV):**

  | corner | settle after t0 | err@40ns | margin to 40ns spec | verdict |
  |---|---|---|---|---|
  | TT/27C/3.3V | 2.12 ns | 0.000 mV | 37.9 ns | PASS |
  | SS/125C/2.97V (worst) | 4.22 ns | 0.000 mV | 35.8 ns | PASS |

  `v_final` itself (~2.026V) is naturally different from the pre-TG-era numbers since the architecture is now top-plate sampling, not bottom-plate — expected, not a regression; the acceptance criteria (settle time, err@40ns) are unchanged and both pass with large margin. MSB gate-drive delay (`B7NAND` fall, 10%/5% VDD): 0.73ns/0.93ns (TT) and 0.96ns/1.38ns (SS/125C/2.97V) — both well under the ~4ns informal threshold, consistent with Brief #5's numbers for the equivalent (renamed) signal.

- **Overall verdict: top-plate sampling via a sized TG (4u/8u) resolves the full-range acquisition failure. Gate 2 unaffected. Charge injection is real but well within budget.**

NEXT STEP: INL/DNL sweep over 256 codes on the top-plate-sampling structure (now that full-range VIN acquisition is proven end-to-end); factor the ~0.18 LSB charge-injection error into the linearity budget when interpreting results.

## 2026-07-17 — Tooling fix + figures export for team update

- **`designs/.config/.xschem/xschemrc`:** added `$env(DESIGNS)/dac` and `$env(DESIGNS)/dac/schematic` to `XSCHEM_LIBRARY_PATH` (confirmed `$env(DESIGNS)=/foss/designs` inside the container). Note: the actual symbol resolution for `cap_array.sch`/`tb_major_carry.sch` currently works via the explicit `dac/schematic/*.sym` relative paths baked into each `.sch`'s `C {...}` lines (see the Brief #4 connectivity-guard entry above: these paths resolve relative to cwd, so **xschem/ngspice must always be launched from `/foss/designs`**, per the standing convention) — confirmed by re-testing from `dac/sim/` with the new library-path entries in place, which still drops `x1` (`* x1 - cap_array IS MISSING !!!!`). The `XSCHEM_LIBRARY_PATH` addition is correct/defensive per instructions but does not by itself make these specific literal relative paths cwd-independent; only launching from repo root does.
- **Verification (from `/foss/designs`):** `xschem -q -x -n --rcfile designs/.config/.xschem/xschemrc dac/schematic/cap_array.sch` and `... dac/sim/tb_major_carry.sch` both netlist with zero "IS MISSING" lines and zero warnings/errors. Resolved symbol set — `cap_array.sch`: `dac/schematic/{inv1,nand2,tgate,unit_switch}.sym` + `symbols/cap_mim_2f0fF.sym` + stock (`gnd`,`ipin`,`opin`,`lab_wire`); `tb_major_carry.sch`: `dac/schematic/cap_array.sym` + stock (`capa`,`code`,`gnd`,`lab_wire`,`vsource`).
- **PNG export method that actually works in this container:** xschem's `--png`/`--svg` CLI flags (`xschem -q --png --plotfile out.png ...`) hang indefinitely here — traced to the interactive print path, not a headless/display issue (confirmed a real Xtigervnc is already up on `:1`). The reliable path: `xschem --rcfile <rc> --command "xschem print svg <out.svg>; exit" <sch>` (drives the same C-level `print` command xschem's own PNG-export menu item uses, via `--command` instead of the hanging CLI flags), then rasterize with `cairosvg` (present in this image; `gm`/`convert`/`rsvg-convert` are not) since xschem's native PNG path itself shells out to `gm convert`, which is also absent. Exported `dac/docs/figures/{cap_array,tb_major_carry}_schematic.png` this way; both render with the correct topology, no red missing-symbol placeholder boxes (visually confirmed).
- **Waveform figures:** re-simulated `tb_major_carry.spice` (TT/27C/3.3V, current TG-integrated netlist) via `ngspice -b` with a `wrdata` dump of `v(DAC_TOP)` (had to trim `save all` down to just the needed nodes — `save all` at the deck's native 0.02ns timestep over 1.05µs blew ngspice's default output-memory limit). Confirms the Step 3d TT number: **settle 2.12 ns, err@40ns 0.000 mV** (`v_final`=2.02645V) — this is the **current, TG-based-design** number, not the pre-TG **1.77 ns** figure from Brief #3 (the design changed from bottom-plate-only to top-plate TG sampling between those two entries; flagging since the team-update ask referenced the older 1.77 ns figure specifically). `dac/docs/figures/gate2_major_carry_settling.png`: V(DAC_TOP)-v_final vs time, full transient + a zoomed panel, with the 40ns budget line and ±6.45mV/0.5LSB band both marked.
- **Before/after switch-sizing overlay:** the original unit-sized run (163.2ns/−298.0mV, Brief #3) was never committed as a saved netlist/trace ("done on a scratch netlist copy, not committed" per that entry), so reproduced it faithfully on the **current** netlist instead of inventing numbers: text-substituted all 8 `x_sw{0..7}` `unit_switch` instances in the flat `tb_major_carry.spice` down to a uniform `nfet_wid=0.42u` (undoing the `W=2^i*0.42u` per-bit scaling only — TG top-plate switch and all gate logic untouched), re-ran `ngspice -b`. Result: **settle 163.4 ns, err@40ns −299.7 mV** — matches the historical Brief #3 numbers (163.2ns/−298.0mV) closely, confirming the reproduction is faithful despite the intervening TG rework. `dac/docs/figures/switch_sizing_before_after.png` overlays this unit-sized trace against the current per-bit-sized trace (2.12ns), full window + zoom.
- **Figures committed:** `dac/docs/figures/cap_array_schematic.png`, `dac/docs/figures/tb_major_carry_schematic.png`, `dac/docs/figures/gate2_major_carry_settling.png`, `dac/docs/figures/switch_sizing_before_after.png`.

## 2026-07-17 — Step 1: 256-code nominal INL/DNL transfer sweep (DAC-only, TT) — PASS (structural), gain mismatch flagged

- **Branch:** `dac-cap-array`. New files: `dac/sim/tb_inl_dnl.sch`, `designs/scripts/extract_dnl_inl.py`, `dac/docs/figures/{dnl,inl}_vs_code.png`.

- **Testbench (`dac/sim/tb_inl_dnl.sch`):** ONE 64 µs stepped transient covers all 256 codes — no per-code re-simulation. Period = 250 ns/code: `[0,100n)` SAMPLE=1 sample phase, TG closed, bottom plates forced to GND regardless of B (the SAMPLE-gated NAND2/NOR2 logic makes B a don't-care here), DAC_TOP resets toward a **fixed VIN=0V input** (isolates DAC capacitor linearity from input-dependent effects, per the task's own framing); `[100n,250n)` SAMPLE=0 convert phase, B0-B7 driven to that code's bits (bit set → VREF=1.65V, bit clear → GND) via `pwl()` sources that only transition where a bit actually flips vs the previous code (511 breakpoints for B0 down to 3 for B7 — a plain binary counter, generated programmatically, not hand-authored). VDD=3.3V, VREF=1.65V fixed. 20fF comparator-input placeholder load on DAC_TOP, same as every prior testbench in this series.
- **Two netlisting/run snags, both fixed:**
  1. `.ic v(DAC_TOP)=0` inside `.control` (the pattern used in `tb_sample_hold.sch`) throws `.ic: no such command available in ngspice` in this ngspice build when run via `ngspice -b` batch mode — non-fatal here (VIN=0 already matches the desired cold-start value under `uic`'s default zero-IC behavior) but removed for a clean run; **`tb_sample_hold.sch`'s own `.ic` line is unverified in batch mode** and should be rechecked if it's ever re-run standalone.
  2. `save all` at this 64 µs / 1 ns-print-step duration exceeds ngspice's default output-memory limit (`Error: memory required (178454400 Bytes) is more than memory available`) — same failure mode already documented in the 2026-07-17 figures-export entry above. Fixed by `save v(dac_top)` (only the node this analysis needs).
- **Connectivity guard: PASS.** Netlisted from `/foss/designs` (`designs/simulations/tb_inl_dnl.spice`): `x1 VIN VREF VDD SAMPLE B0 B1 B2 B3 B4 B5 B6 B7 DAC_TOP cap_array`, flattened `cap_array` subckt shows all 8 caps (`XC0-XC7`, m=1..128) sharing `DAC_TOP`, `x_tg` TG on `VIN/DAC_TOP/SAMPLE/SAMPLE_N`, no floats.
- **Run:** `ngspice -b designs/simulations/tb_inl_dnl.spice` — 8.2s wall time, 74585 transient rows, `wrdata dac/sim/tb_inl_dnl_tran.csv v(DAC_TOP)` (not committed — 2.4MB raw transient dump, same treatment as `.raw` files elsewhere in this repo; regenerate by re-running the netlist+ngspice commands above).
- **`designs/scripts/extract_dnl_inl.py`** (satisfies REP-1): interpolates `v(DAC_TOP)` at each code's sample point (245ns into its 250ns period, 5ns margin before the next code's sample phase begins — comfortably past the TG's worst-case TT settle of ~54-60ns from the Brief #10 sizing sweep), then computes:

  | metric | value |
  |---|---|
  | measured FS span (V[255]-V[0]) | **1.6465 V** |
  | intended FS (spec) | 3.3 V |
  | ratio measured/intended | **0.499** |
  | V_LSB (endpoint-derived) | 6.457 mV |
  | max \|DNL\| | 0.00673 LSB @ code 161 |
  | monotonic (all steps > 0) | **True** |
  | missing codes (any DNL ≤ -1) | **None** |
  | max \|INL\| (endpoint line) | 0.00768 LSB @ code 161 |
  | max \|INL\| (best-fit line) | 0.00593 LSB @ code 161 |

- **VREF=1.65V vs FS=3.3V reconciliation (flagged, exactly as anticipated):** measured/intended ratio is 0.499 ≈ 1/2 — the DAC's bottom-plate reference is `VREF=1.65V` (half of `VDD=3.3V`), so its native output span is ~VREF, not the full 3.3V rail. This is a **gain/reference mismatch**, not a linearity defect — every other number above is self-consistent (endpoint-derived `V_LSB` already absorbs it). Whether the full-ADC top level compensates (e.g. VREF should actually be tied to VDD=3.3V for a true 3.3V-FS DAC, or the spec's 3.3V FS assumption needs revisiting) is an integration-level question, not a DAC-block defect — flagging for the team, not fixing here.
- **Nominal linearity: PASS, as expected.** max|DNL| and max|INL| (0.007-0.008 LSB) are far under the 0.5 LSB spec, monotonic, no missing codes — this proves **structural correctness** (no settling artifacts, no charge-injection-driven non-monotonicity, no code-dependent bugs) with perfectly-matched schematic caps. It is **not** the real matching limit — that requires cap mismatch (Step 2, capacitor sigma/C budget or Monte Carlo), not yet run.
- **Charge injection note:** VIN is fixed at 0V during every sample phase in this testbench, so the ~0.18 LSB sample-switch charge-injection error found in Brief #10 (Step 3c) shows up here only as a constant DC offset — removed by both the endpoint-line and best-fit-line INL referencing. Its *input-dependent* component (charge injection varies with VIN, per the Brief #10 table) does not appear in a DAC-only sweep with fixed VIN; it will only show up in a full-ADC transfer-curve test with a swept input. Noting this so the near-zero INL/DNL numbers above aren't misread as already including that error term.
- **Small mid-code ripple (codes ~130-170, visible in the figures):** ≤0.01 LSB peak-to-peak, well inside spec — settling-residual artifact from simultaneous multi-bit transitions in that range, not a structural defect.

NEXT STEP: Step 2 — capacitor mismatch analysis (the real linearity limit): check for a gf180 `cap_mim` statistical/Monte-Carlo model; if present, MC (N≥100) focused on the major-carry transitions (0x7F→0x80, 0x3F→0x40, 0xBF→0xC0); if absent, an analytical Pelgrom-based cap-matching budget for the 50fF/5µm×5µm unit cap vs the <0.5 LSB @ 8-bit requirement.
