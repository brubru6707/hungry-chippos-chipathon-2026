# Verification Plan

> Companion to `PROGRESS.md`. `PROGRESS.md` tracks block-by-block task status;
> this file records the actual spec numbers and pass/fail verdicts for each
> verification gate as they're closed out.

---

## Capacitor DAC (DAC) — Gate 2: settling time

**Spec:**

| Parameter | Value |
|---|---|
| Full scale (FS) | 3.3 V |
| Resolution | 8-bit (256 codes) |
| 1 LSB | FS / 256 = 12.9 mV |
| Gate-2 criterion | settle to within 0.5 LSB (6.45 mV) of final value in **< 40 ns** |
| Corner (baseline) | TT, 27 °C, V_DD = 3.3 V |

**Testbench:** `dac/sim/tb_major_carry.sch` — major-carry step (code `0111_1111` held
600 ns → steps to `1000_0000` at t0=700n with 50 ps edges), SAMPLE held low
(hold phase), 20 fF comparator-input placeholder load on `DAC_TOP`. Per-bit
switch sizing (`W = 2^i * W_unit`, `W_unit = 0.42 µm`) implemented in
`cap_array.sch` (commit `aa7caef`). `dac/sim/tb_cap_array.sch` (first-pass,
single-bit MSB-only check) has been deleted — its schematic-level `lab=`
annotations were cosmetic only and it netlisted with disconnected nodes;
`tb_major_carry.sch` is the authoritative Gate-2 testbench.

**Status: 🟢 PASS — verified 2026-07-17, all 30 PVT corners.**

- **TT, 27 °C, 3.3 V:** settle = 1.77 ns, err@40ns ≈ 0 mV (commit `aa7caef`).
- **Full PVT sweep** (process: typical/ss/ff/sf/fs × temp: -40/27/125 °C ×
  V_DD: 3.3 V/2.97 V, 30 combinations, same `tb_major_carry.sch` stimulus):
  every corner settles well under 40 ns and every err@40ns is effectively 0 mV
  (≤ 0.0001 mV). Full table in `dac/WORKLOG.md` (2026-07-17 entry).
- **Worst-case corner: SS, 125 °C, V_DD = 2.97 V** (slowest switch nfet:
  weak process + lowest gate overdrive + highest temperature) — settle =
  **2.784 ns**, margin to spec = **37.22 ns**, err@40ns ≈ 0 mV.

**Verdict: Gate 2 PASS across TT and all sampled PVT corners.**

---

## Verification Gates Summary

| Gate | Criterion | Block | Status |
|------|-----------|-------|--------|
| Gate 1 | σ_offset characterized + delay < 2 ns @ TT (MC N≥100) | Comparator | 🟡 |
| Gate 2 | DAC settling ≤ 0.5 LSB (6.45 mV) within 40 ns, TT + PVT corners | Cap DAC | 🟢 **PASS** (worst case SS/125°C/2.97V: 2.78 ns, 37.2 ns margin) |
| Gate 3 | Top-level DNL/INL < 0.5 LSB @ TT corner | Integration | ⚪ |
| Gate 4 | Full corner sweep (FF/SS/SF/FS) passes spec | Integration | ⚪ |
| Gate 5 | DRC clean + LVS clean → tapeout sign-off | Integration | ⚪ |
