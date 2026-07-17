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
