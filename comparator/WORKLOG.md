# Comparator (StrongARM) — WORKLOG

Running notes for the comparator block, mirroring `dac/WORKLOG.md`. Task status
lives in `PROGRESS.md` §2 (COMP-*); this file holds the how/why detail.

## Block snapshot (as of 2026-07-19)

- **DUT:** `comparator/schematic/strongarm.sch` / `.sym` — classic single-stage
  StrongARM latch, 11 devices (all 3.3V): NMOS input pair M10 (VIN1) / M8
  (VIN2), NMOS tail M11 (gate CK), cross-coupled NMOS M9/M1 + PMOS M2/M7,
  four PMOS precharge switches M3/M6 (outputs) and M4/M5 (internal nodes
  net3/net1), all gated by CK.
- **Decision convention:** CK **low** = reset/precharge — VOUT1, VOUT2 and the
  internal nodes precharge **high to VDD**. Decision on CK **rising** edge
  (NMOS tail turns on). The **losing** output falls to 0, winner returns to
  VDD. VIN1 > VIN2 ⇒ **VOUT1 falls** (left branch VOUT1–M9–net3–M10–net2
  discharges first).
- **Sim netlist:** `comparator/schematic/strongarm.spice` (bulk-fixed; the
  pre-fix copy is `.bak_pre_bulk_fix`). NOTE: it is M-prefixed (LVS style);
  for ngspice the devices must be **X-prefixed** (GF180 models are
  subckt-based) — that's why the MC tb alters `@m.x1.xm10.m0[delvto]`.
- **Offset (COMP-5, done):** `strongarm_mc_tb.sch`, N=100 @ svt=24.8mV:
  mean **+2.6 mV**, σ = **36.9 mV** (`comp_mc_report.txt`). Treated as a
  calibratable DC shift for the SAR — no upsizing.
- **Layout:** DRC + LVS clean at variant=D (see COMP-7/COMP-8 backups under
  `comparator/layout/backups/`). Use the terminal `run_lvs.py` flow from
  `handoff/README.md`, **not** the KLayout GUI LVS (known false-short bug).
- **Known issue:** full-rail Vcm problem — comparator misbehaves with inputs
  at the rails; plan is a mid-rail threshold fix later. Until then all delay
  work is done at **mid-rail Vcm = 1.65 V**.
- **Env:** all tools (ngspice/xschem/KLayout + gf180mcuD PDK) live in Docker
  container `iic-osic-tools_xvnc_uid_501`; repo mounts at `/foss/designs`.
  Host mac has no EDA tools. ngspice needs full path `/foss/tools/bin/ngspice`
  under `bash -c` (or use a login shell).

## 2026-07-19 — decision delay t_clk→Q vs overdrive (schematic-level, first numbers)

New tb: `comparator/sim/tb_comp_delay.spice` (standalone ngspice deck; DUT
subckt copied 1:1 from `strongarm.spice` with M→X prefix, **no schematic
touched**). TT / 27 °C / VDD = 3.3 V, Vcm = 1.65 V (mid-rail, see known issue),
VIN1 = Vcm + od, VIN2 = Vcm. CK: precharge 0–5 ns, rising edge at 5 ns
(PULSE 0→3.3, 200 ps edges). Loads: 10 fF on each output — **nominal fallback**
for the SAR-logic input (a couple of 3.3 V gate inputs ≈ 1–2 fF each + wiring;
no extracted SAR value yet), deliberately conservative.

Delay = CK crossing 1.65 V rising → losing output (VOUT1) crossing 1.65 V
falling:

```
meas tran t_clk2q trig v(ck) val=1.65 rise=1 targ v(out1) val=1.65 fall=1
```

Results (`comparator/sim/comp_delay_results.txt`):

| overdrive | t_clk→Q | OUT1 @14n | OUT2 @14n |
|---|---|---|---|
| 6.457 mV (0.5 LSB) | **201.9 ps** | 0 V | 3.3 V |
| 12.914 mV (1 LSB) | 198.3 ps | 0 V | 3.3 V |
| 100 mV | 166.9 ps | 0 V | 3.3 V |

Monotonic (smaller od → longer delay) and correct decision polarity every run.
~10× margin to the 2 ns Gate-1 spec **at schematic level** — not claiming the
spec yet; needs post-layout + corners + mismatch-slowed worst case (offset
σ=36.9mV means near-zero effective overdrive happens, i.e. metastability-limit
runs should be checked before sign-off).

**Post-layout status:** `comparator/layout/strongarm_extracted.cir` (dated
15/07) is from the *shorted* layout — nets `VOUT2|VSS` merged — **do not
simulate it**. A clean extraction must be re-run from the LVS-clean GDS
(`layout/backups/strongarm_LVS_CLEAN_2026-07-10_10h44m…gds`) before the
sign-off delay pass.

Sim gotchas honored: no `save all` (explicit save list), no `.ic`-in-control
(precharge phase from t=0 op with CK=0 makes ICs unnecessary), tools run in
the container.

## 2026-07-19 — delay corners + metastability + Vcm window (schematic-level, targets for extracted sign-off)

Tb **parameterized**: `tb_comp_delay_param.spice.template` +
`tb_comp_vcm_sweep.spice.template`, driven by `run_comp_delay_sweeps.sh`
(sed-generates `gen_tb_<tag>.spice`, runs in container). Vcm, the CK trigger
threshold and the VOUT target threshold are all **VDD/2 of the corner in
use** — no more hardcoded 1.65 V (SS runs at VDD=2.97 → 1.485 V). Tolerances
tightened (`reltol=1e-4 vntol=1nV`) so µV overdrives aren't swallowed by the
default 1 µV vntol. TT rerun reproduces the 201.9 ps baseline exactly.

All numbers in `comparator/sim/comp_delay_corner_summary.txt` (per-run files
`comp_delay_<tag>.txt` / `comp_vcm_<tag>.txt`). Headlines, od = 0.5 LSB:

- **Corners:** TT/27/3.3 = 201.9 ps; **SS/125/2.97 = 362.1 ps (binding)**;
  FF/−40/3.63 = 124.9 ps; SS/125/3.3 = 308.7 ps (so temp+process ≈ 107 ps,
  VDD droop ≈ 53 ps). All ≪ 2 ns spec, correct polarity everywhere.
- **Metastability (SS/125/2.97):** delay *saturates* at ~370.6 ps as od → 0;
  measured flat from 1 mV down to 0.1 µV (solver floor). overdrive@1ns /
  @2ns **not reachable** — even an offset-cancelled input (σ=36.9 mV sample
  nearly nulling the signal) resolves in ~371 ps. Metastability is not the
  schematic-level hazard; margin 5.4× at the floor.
- **Vcm window (SS/125/2.97):** spec-compliant for **Vcm ≥ 0.85 V** up to at
  least VDD−0.3; slow-but-correct 0.7–0.8 V; hard fail (no decision) ≤ 0.6 V
  — quantifies the known low-rail Vcm issue. Mid-rail SAR operating point
  (VDD/2) sits comfortably inside with 362 ps.
- **Worst case for extracted sign-off:** SS / 125 °C / 2.97 V, Vcm = VDD/2,
  effective od ≤ 0.1 mV → ~370.6 ps schematic. Extracted pass must beat 2 ns
  there (recall: extraction must come from the LVS-clean GDS, *not* the
  stale shorted `strongarm_extracted.cir`).

No schematic touched.

## 2026-07-19 — fresh LVS-clean StrongARM extraction (checkpoint)

Re-extracted from
`layout/backups/strongarm_LVS_CLEAN_2026-07-10_10h44m1783694640.gds` with the
documented `run_lvs.py` terminal flow, variant D, flat mode, and `VSS` as the
LVS substrate. The fresh run is retained at
`layout/klayout_lvs_run_postlayout_20260719/`.

- **LVS:** `INFO : Congratulations! Netlists match.`
- **Connectivity:** VOUT2 and VSS are distinct in the raw extracted deck;
  no `VOUT2|VSS` merged net appears.
- **Devices:** 11 MOSFETs (6 PFET + 5 NFET), matching the schematic.
- **Extraction content:** device-level connectivity/geometry only; no
  extracted interconnect capacitance or resistance. Therefore subsequent
  delay values are device-level post-layout/LVS-clean measurements, not
  full-RC-extracted timing.
- **Simulation deck:** `layout/strongarm_extracted_clean.spice` is the
  checked-in, X-prefixed simulation conversion of the raw KLayout deck;
  it preserves extracted W/L and topology while omitting KLayout MOS-only
  AS/AD/PS/PD annotations that GF180's subckt models do not accept. The stale
  `layout/strongarm_extracted.cir` remains unused because it contains the
  historical VOUT2|VSS short.

## 2026-07-19 — post-layout decision-delay sign-off (device-level extraction)

The parameterized delay template now instantiates the fresh clean extracted
deck with the unchanged 10 fF/output load. CK, Vcm, and the output threshold
were all held at VDD/2 for each corner; only `v(ck)`, `v(out1)`, and
`v(out2)` were saved. Results are measured CK rising VDD/2 → losing VOUT1
falling VDD/2:

| condition | overdrive | extracted t_clk→Q | schematic reference | delta |
|---|---:|---:|---:|---:|
| SS / 125 C / 2.97 V, Vcm=1.485 V | 0.5 LSB (6.457 mV) | **362.078 ps** | 362.1 ps | −0.022 ps |
| SS / 125 C / 2.97 V, Vcm=1.485 V | 0.1 mV | **370.455 ps** | 370.5 ps | −0.045 ps |
| TT (`typical`) / 27 C / 3.3 V, Vcm=1.65 V | 0.5 LSB (6.457 mV) | **201.855 ps** | 201.9 ps | −0.045 ps |

All runs resolve with VOUT1 low and VOUT2 high at 14 ns. The binding
near-zero SS result is 370.455 ps, a 5.40x margin to the 2 ns requirement:
**Gate-1 delay is PASS.** The essentially zero measured penalty is expected
because `run_lvs.py` produces an LVS device-level deck without parasitic C or
R; this is not a full-RC PEX claim. Comparator offset acceptability remains a
separate Gate-1 consideration.

## 2026-08-04 — COMP-ALT: CKL re-sweep, root-cause of invalid MC results, tail fix (Gate-1 offset PASS)

**Headline:** two-stage offset MC at CKL=2.8n: N=100, good=100/100,
mean = −0.28 mV, σ = 1.09 mV → 34× below the 36.9 mV StrongARM baseline,
45% margin to the 2 mV target. COMP-ALT-7 caveats (latch resize, bulk ties) covered.

**Root cause of weeks of bad numbers:** the layout-driven nf→m edit (COMP-ALT-8
lesson) is NOT electrically neutral in ngspice: `W=4u nf=16` is 4 µm total,
`W=4u m=16` is 64 µm. The edit multiplied the preamp pair ×16 and tail ×5.
Preamp integration collapsed from ~3 ns to ~0.4 ns; at every swept CKL (2.7–4.5n)
the latch fired into dead (fully-discharged) preamp outputs. All MC "results" in
that regime came from a reset-overlap artifact: CK fell while CKL was still high,
the preamp precharge snapped DIP1/2 to VDD, and the latch "decided" from residue
~1 ns after CK fell. Symptoms for future reference: means pinned near the ±10 mV
ramp endpoint, missing-measure runs, and vout transitions timestamped after CK's
falling edge. The 07-31 comp2 (σ=1.30 mV) run is retroactively untrustworthy.

**Fixes:**
1. Preamp tail MT1: was W=2u/L=0.4u m=5 (10 µm, accidental) → now W=2u/L=1u m=1
   (2 µm, ~12× weaker). Integration peak −221 mV at ~1.7 ns after CK (gain ≈ 22 at
   peak); usable window restored. Input pair m=16 kept (offset budget needs 64 µm²).
2. CKL pulse width 8n → 5n so the latch window always closes before CK falls —
   makes the reset-overlap artifact structurally impossible.
3. MC tb: `tran 10p 1u` → `tran 1n 1u` (10p forced ≥100k steps/transient for
   ~µV-irrelevant precision; ~40× runtime saving).

**Design insight (exposure, not just timing):** the latch needs its input drive
*held* ~0.5–1 ns to regenerate past the point of no return, and this preamp's
differential peak coincides with near-empty (CM < 1 V) outputs by construction.
So CKL must fire BEFORE the peak, where signal and common-mode are both healthy:
at 2.8n the latch samples ~−98 mV at CM ≈ 2.5 V and resolves in ~0.26 ns.

**CKL sweep (N=30/point, tran 1n, seed 12345 paired across points):**
σ = 0.92 / 0.92 / 0.94 / 0.94 / 0.96 mV at CKL = 2.6/2.7/2.8/2.9/3.0n — flat,
forgiving window. Hard cliff at ≥3.1n (misses + endpoint-contaminated mean).
CKL = 2.8n chosen for margin on both sides, not for σ.
Decision completes ~1.0 ns after CK edge (TT, −10 mV od) — informal; Gate-1
delay corners remain COMP-ALT-10.

**Artifacts:** `comparator_alt/results/mc_ckl2p8_n100_{report,offsets}.txt`,
`comparator_alt/sim/ckl_sweep/` (deck generators, debug decks, logs).
NOTE: `DESIGN_LOG.md` referenced by PROGRESS.md §6 is absent from the repo —
possibly never committed; this entry is the standing COMP-ALT record until found.
