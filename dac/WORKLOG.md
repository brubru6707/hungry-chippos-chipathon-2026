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
