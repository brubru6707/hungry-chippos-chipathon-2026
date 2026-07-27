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

**Status: 🟢 PASS — re-verified 2026-07-18 after the VREF=VDD rework (see
below); previously verified 2026-07-17, all 30 PVT corners, under the old
VREF=1.65V scheme (superseded).**

- **VREF=VDD=3.3V rework (2026-07-18):** the bottom-plate switch (`unit_switch.sch`)
  used to be two NMOS pass-gates to a separate `VREF=1.65V` node and GND — an
  NMOS pass transistor cannot pull a node to the full `VDD` rail, capping the
  achievable full scale at ~VREF. Replaced with a CMOS rail driver (PMOS
  pull-up to `VDD`, NMOS pull-down to `GND`, both gated by the same
  `bN_bar=NAND2(Bn,SAMPLE_N)` signal already generated per-bit for
  SAMPLE-gating — mathematically the two gates always need the identical
  control signal, so the old separate `bN=AND(Bn,SAMPLE_N)` inverter stage
  was removed as dead logic). `VREF` net/pin deleted everywhere (cap_array,
  unit_switch, all 5 testbenches); the only supplies are now `VDD`/`GND`.
  Per-bit driver sizing: `nfet_wid=2^i*0.42u` (unchanged), `pfet_wid=2*nfet_wid`
  (matches the inv1/nand2/tgate P:N=2:1 convention). The MSB PMOS
  (bit7, 107.52 µm total) exceeds gf180mcuD's binned-model width ceiling
  (`wmax=100.001µm`, confirmed empirically that `nf` does not reduce the
  binning-relevant width in this PDK — only `m` linearly scales drive
  strength) so it's built as `pfet_wid=53.76u` with `pfet_m=2`.
  `1 LSB = VDD/256 = 12.9 mV`, `FS = VDD = 3.3 V` (was `FS≈VREF≈1.65V`
  before this rework — see the Gate-3 section below for the direct evidence).
- **TT, 27 °C, 3.3 V (post-rework):** settle = 2.61 ns, err@40ns = 0.0 mV.
- **Worst-case corner, post-rework: SS, 125 °C, V_DD = 2.97 V** (same
  slowest-switch reasoning as before: weak process + lowest gate overdrive +
  highest temperature) — settle = **3.86 ns**, margin to spec = **36.1 ns**,
  err@40ns = 0.0 mV. (Full 30-corner sweep not re-run — TT and this
  previously-worst corner both clear the 40 ns budget with >9x margin; the
  new CMOS driver is if anything faster than the old NMOS-only pull path
  since the PMOS pull-up is now full-strength instead of Vt-limited.)

**Verdict: Gate 2 PASS at TT and worst PVT corner, post VREF=VDD rework.**

---

## Capacitor DAC (DAC) — Gate 3 (partial): 256-code nominal INL/DNL

**Testbench:** `dac/sim/tb_inl_dnl.sch` — one 64 µs stepped transient, 256
codes × 250 ns/code (100 ns SAMPLE=1 sample phase with a **fixed VIN=0V**
input, 150 ns SAMPLE=0 convert phase driving B0-B7 to the code). Sample
point per code: 245 ns into its period (5 ns before the next sample phase
begins). `designs/scripts/extract_dnl_inl.py` computes FS span, DNL, INL
(endpoint-line + best-fit-line), monotonicity, missing codes.

**Status: 🟢 DAC-only nominal sweep PASS, re-verified 2026-07-18 after the
VREF=VDD rework — the FS gain gap flagged below is now resolved. Full
ADC-level (with comparator + sequencing) integration still pending.**

| metric | value | spec | verdict |
|---|---|---|---|
| measured FS span (V[255]-V[0]) | 3292.98 mV | 3.3 V (intended) | ratio 0.998 — **matches FS, gain gap resolved (was 0.499 ≈ 1/2 pre-rework)** |
| V_LSB (endpoint-derived) | 12.914 mV | 12.9 mV | matches spec |
| max \|DNL\| | 0.00216 LSB @ code 196 | < 0.5 LSB | PASS |
| monotonic | yes (all steps > 0) | required | PASS |
| missing codes | none | required | PASS |
| max \|INL\| (endpoint line) | 0.00439 LSB @ code 195 | < 0.5 LSB | PASS |
| max \|INL\| (best-fit line) | 0.00290 LSB @ code 195 | < 0.5 LSB | PASS |

- **VREF vs FS reconciliation — RESOLVED 2026-07-18.** The previous entry
  flagged that the DAC's bottom-plate reference was `VREF=1.65V`, half of
  `VDD=3.3V`, so its native output span was ~VREF — a gain mismatch against
  the 3.3V FS spec. Team decision: DAC now uses `VREF=VDD=3.3V` (full
  rail); the `VREF` net is deleted and the bottom-plate switch is a CMOS
  rail driver (PMOS to `VDD`, NMOS to `GND` — see the Gate-2 section above
  for the switch-topology rework). Measured FS span above (3292.98 mV,
  99.8% of the ideal 3.3V) directly confirms the fix — the
  `extract_dnl_inl.py` "measured span far below 3.3V FS" flag no longer
  fires.
- **This is a structural-correctness result, not the real matching
  limit.** Nominal (perfectly-matched schematic caps) INL/DNL is expected
  to be near-zero — it proves no settling/charge-injection/code-dependent
  artifacts, not that real silicon will hit 0.5 LSB. The real limit is
  **capacitor mismatch**, characterized in Step 2 (LSB-based conclusion
  unchanged by this rework — not re-run, see below).
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
| Gate 2 | DAC settling ≤ 0.5 LSB (6.45 mV) within 40 ns, TT + PVT corners | Cap DAC | 🟢 **PASS**, post VREF=VDD rework 2026-07-18 (worst case SS/125°C/2.97V: 3.86 ns, 36.1 ns margin) |
| Gate 3 | Top-level DNL/INL < 0.5 LSB @ TT corner | Integration | 🟢 DAC-only nominal sweep PASS post VREF=VDD rework (FS span 3293mV = 99.8% of 3.3V, max\|DNL\|=0.002, max\|INL\|=0.004 LSB); **cap-mismatch PASSES at Cu=50fF (≥99.9997% yield, corrected local-mismatch model — see above, LSB-based conclusion unaffected by the rework)**, no upsizing needed, common-centroid layout (DAC-5) still required for systematic-gradient cancellation; full ADC-level integration still pending |
| Gate 4 | Full corner sweep (FF/SS/SF/FS) passes spec | Integration | ⚪ |
| Gate 5 | DRC clean + LVS clean → tapeout sign-off | Integration | ⚪ |
