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
