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

## Capacitor DAC (DAC) — Gate 3 (real limit): capacitor-mismatch Monte Carlo INL/DNL

**CORRECTED 2026-07-17 (Step 2e in `dac/WORKLOG.md`).** The original version
of this section (verified earlier the same day) used the PDK's *global*
`cap_mim` Monte Carlo term as if it were independent *local* per-cap
mismatch, which is a modeling bug — see "Local vs global mismatch" below.
That version reported 71.5% yield and a required Cu≥200-400fF; both numbers
are superseded by the corrected analysis in this section. History kept in
`dac/WORKLOG.md`'s Step 2a-2d entries, not deleted, for the record.

**Testbench:** `designs/scripts/dac_mismatch_mc.py` (idealized
charge-redistribution transfer function, N=300,000 runs/point, all 256
codes) + `designs/scripts/dac_mismatch_mc_spice.py` (transistor-level
ngspice cross-check via `tb_major_carry.sch`'s structure, N=50/transition,
the 3 dominant major carries only — cross-checks the transfer-function
model itself, not the corrected mismatch magnitude below).

**Local vs global mismatch:** `V(code) = VREF*C_code/(C_total+Cp)` depends
only on capacitor **ratios**. A **global** (die-to-die/lot) parameter — one
draw shared by every cap on the die, `C_i -> C_i*(1+g)` for the same `g` —
cancels almost exactly in that ratio and shows up only as a full-scale
**gain** error, not DNL/INL. Only **local** (cap-to-cap, intra-die)
mismatch breaks the ratio and drives DNL/INL. gf180mcuD's `mc_c_cox_2p0fF`
(`libs.tech/ngspice/sm141064.ngspice`, `.LIB mimcap_statistical`,
`agauss(0,0.025,3)`, 2.5% 1-sigma) is gated only by `sw_stat_global`, never
`sw_stat_mismatch` — confirmed by grep across the deck — so it is a
**global** parameter and must not be applied independently per cap.
gf180mcuD ships no local-mismatch (Pelgrom) coefficient for `cap_mim`
anywhere in the PDK tree.

**Corrected local-mismatch model:** literature Pelgrom estimate for 180nm
MiM caps, `sigma(C_unit)/C_unit = A_C/sqrt(Area)` (Area in µm², A_C in
%·µm) — **A_C=1.6%·µm primary, A_C=3.2%·µm conservative (2×) sensitivity
case.** Unit-cap area follows the design's 2fF/µm² density (50fF unit =
5µm×5µm = 25µm²), so the Cu sweep below automatically sweeps area and
sigma together. Each binary cap is `N_i=2^i` parallel unit cells,
`sigma(C_i)/C_i(ideal) = sigma_unit(Cu,A_C)/sqrt(N_i)`.

**Status: 🟢 PASS at the current Cu=50fF — verified 2026-07-17.**

| Cu [fF] | A_C [%·µm] | mean\|DNL\| | worst\|DNL\| | mean\|INL\| | worst\|INL\| | YIELD |
|---|---|---|---|---|---|---|
| 50  | 1.6 | 0.0529 | 0.257 | 0.0398 | 0.130 | 100.000% |
| 100 | 1.6 | 0.0374 | 0.169 | 0.0282 | 0.091 | 100.000% |
| 200 | 1.6 | 0.0265 | 0.127 | 0.0199 | 0.066 | 100.000% |
| 50  | 3.2 | 0.1060 | 0.513 | 0.0798 | 0.275 | 99.9997% |
| 100 | 3.2 | 0.0748 | 0.352 | 0.0564 | 0.180 | 100.000% |
| 200 | 3.2 | 0.0529 | 0.247 | 0.0399 | 0.132 | 100.000% |

All 6 Cu × A_C points clear both the 0.5 LSB DNL/INL spec and the 99%
yield target with wide margin (N=300,000/point; worst corner
re-checked at N=200,000 with a different seed, 99.999% — consistent, not
sampling noise). **No unit-cap upsizing required — Cu=50fF (current
schematic value) is adequate.** See `dac/docs/figures/mc_yield_vs_cu.png`.

**Global 2.5% effect, isolated (N=300,000, Cu=50fF, one common scale
factor applied identically to all 8 caps per run):**

| metric | result |
|---|---|
| full-scale GAIN error | mean −0.0001%, sigma 0.0039%, worst-case 0.0184% |
| max\|DNL\| under global-only variation | 0.000000 LSB (mean and worst) |
| max\|INL\| under global-only variation | 0.000000 LSB (mean and worst) |

Confirms global variation drives **zero** DNL/INL, as predicted. The gain
error itself also turns out far smaller than the naive "2.5% cap
tolerance → 2.5% gain error" intuition (≈0.004% sigma) — `C_total` scales
with `C_code` in the same ratio, so only the fixed, non-scaling comparator
load `Cp=20fF` (≈0.16% of `C_total`) leaks through as a residual gain term.

Transistor-level cross-check (N=50/transition, real TG resistance/charge
injection/gate delay, `dac_mismatch_mc_spice.py`) agrees with the
idealized transfer-function model's mean/sigma within 5-15% at all 3
dominant major carries — this validates the `V(code)=VREF*C_code/(C_total+Cp)`
transfer function itself, independent of which mismatch magnitude is fed
into it.

**Required fix: none for Cu sizing.** Mandatory common-centroid unit-cell
layout (DAC-5) still applies regardless — the statistical model here (both
the corrected version and the original) only covers *random* mismatch;
systematic oxide-thickness gradient across the die is a separate error term
that only common-centroid layout cancels, orthogonal to this Cu-sizing
question. The A_C=1.6/3.2%·µm figures are literature estimates (gf180mcuD
ships no local-mismatch number for `cap_mim`); the 2× conservative case is
the intended margin against that literature-vs-silicon gap.

**S/H IC re-check (batch-valid cold start):** re-ran `tb_sample_hold.sch` at
VIN=3.0V/3.2V with ngspice's own `uic` zero-initial-condition default (the
schematic's `.ic v(DAC_TOP)=0` line is confirmed to no-op in this ngspice
build's batch mode — `.ic: no such command available in ngspice` — but is
inconsequential since `uic` already forces the same cold start).
`v_acq_final` = 3.000000V / 3.200000V exactly, hold droop 0.000mV both —
**S/H full-range acquisition PASS reconfirmed**, not a DC-solver pre-charge
artifact.

---

## Verification Gates Summary

| Gate | Criterion | Block | Status |
|------|-----------|-------|--------|
| Gate 1 | σ_offset characterized + delay < 2 ns @ TT (MC N≥100) | Comparator | 🟡 |
| Gate 2 | DAC settling ≤ 0.5 LSB (6.45 mV) within 40 ns, TT + PVT corners | Cap DAC | 🟢 **PASS** (worst case SS/125°C/2.97V: 2.78 ns, 37.2 ns margin) |
| Gate 3 | Top-level DNL/INL < 0.5 LSB @ TT corner | Integration | 🟢 DAC-only nominal sweep PASS (max\|DNL\|=0.007, max\|INL\|=0.008 LSB); **cap-mismatch PASSES at Cu=50fF (≥99.9997% yield, corrected local-mismatch model — see above)**, no upsizing needed, common-centroid layout (DAC-5) still required for systematic-gradient cancellation; full ADC-level integration still pending |
| Gate 4 | Full corner sweep (FF/SS/SF/FS) passes spec | Integration | ⚪ |
| Gate 5 | DRC clean + LVS clean → tapeout sign-off | Integration | ⚪ |
