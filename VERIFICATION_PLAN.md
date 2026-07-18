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

## Capacitor DAC (DAC) — Gate 3 (partial): 256-code nominal INL/DNL

**Testbench:** `dac/sim/tb_inl_dnl.sch` — one 64 µs stepped transient, 256
codes × 250 ns/code (100 ns SAMPLE=1 sample phase with a **fixed VIN=0V**
input, 150 ns SAMPLE=0 convert phase driving B0-B7 to the code). Sample
point per code: 245 ns into its period (5 ns before the next sample phase
begins). `designs/scripts/extract_dnl_inl.py` computes FS span, DNL, INL
(endpoint-line + best-fit-line), monotonicity, missing codes.

**Status: 🟡 DAC-only nominal sweep PASS; full linearity limit (cap
mismatch) and full ADC-level (with comparator + sequencing) integration
still pending.**

| metric | value | spec | verdict |
|---|---|---|---|
| measured FS span (V[255]-V[0]) | 1.6465 V | 3.3 V (intended) | ratio 0.499 ≈ 1/2 — **gain/reference mismatch, flagged** (see below), not a linearity defect |
| max \|DNL\| | 0.00673 LSB @ code 161 | < 0.5 LSB | PASS |
| monotonic | yes (all steps > 0) | required | PASS |
| missing codes | none | required | PASS |
| max \|INL\| (endpoint line) | 0.00768 LSB @ code 161 | < 0.5 LSB | PASS |
| max \|INL\| (best-fit line) | 0.00593 LSB @ code 161 | < 0.5 LSB | PASS |

- **VREF vs FS reconciliation:** the DAC's bottom-plate reference is
  `VREF=1.65V`, half of `VDD=3.3V`, so its native output span is ~VREF —
  a gain mismatch against the 3.3V FS spec, not a cap-array defect.
  Flagged for the team (integration-level question: should VREF be tied
  to the 3.3V rail for a true 3.3V-FS DAC?).
- **This is a structural-correctness result, not the real matching
  limit.** Nominal (perfectly-matched schematic caps) INL/DNL is expected
  to be near-zero — it proves no settling/charge-injection/code-dependent
  artifacts, not that real silicon will hit 0.5 LSB. The real limit is
  **capacitor mismatch**, characterized in Step 2 (not yet run — see
  `dac/WORKLOG.md`).
- Full detail, snags fixed, and caveats (fixed-VIN charge-injection
  note, mid-code ripple) in `dac/WORKLOG.md`'s 2026-07-17 Step 1 entry.

---

## Verification Gates Summary

| Gate | Criterion | Block | Status |
|------|-----------|-------|--------|
| Gate 1 | σ_offset characterized + delay < 2 ns @ TT (MC N≥100) | Comparator | 🟡 |
| Gate 2 | DAC settling ≤ 0.5 LSB (6.45 mV) within 40 ns, TT + PVT corners | Cap DAC | 🟢 **PASS** (worst case SS/125°C/2.97V: 2.78 ns, 37.2 ns margin) |
| Gate 3 | Top-level DNL/INL < 0.5 LSB @ TT corner | Integration | 🟡 DAC-only nominal sweep PASS (max\|DNL\|=0.007, max\|INL\|=0.008 LSB); cap-mismatch (Step 2) and full ADC-level integration still pending |
| Gate 4 | Full corner sweep (FF/SS/SF/FS) passes spec | Integration | ⚪ |
| Gate 5 | DRC clean + LVS clean → tapeout sign-off | Integration | ⚪ |
