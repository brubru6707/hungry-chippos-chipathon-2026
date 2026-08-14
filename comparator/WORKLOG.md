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

## 2026-08-05 — COMP-ALT-10: delay + corner-window sign-off (schematic level) — PASS, no caveats

**Corner problem found and fixed.** With the original W=2u tail, the whole preamp
trajectory speeds up ~35% at FF/−40°C/3.63V and the CKL window's cliff (~2.7n)
fell below the fixed CKL=2.8n strobe — **no decision at FF**. Fix: preamp tail
MT1 halved again, **W=2u→1u (now 1µm/1µm, m=1)**. Half the drain rate doubles
every corner's window in time; the FF cliff now sits beyond 3.0n and CKL=2.8n
is mid-window at all three corners. Principle: a fixed strobe survives corners
only if the window is much wider than the ±35% corner time-scaling — bought
here with margin. (If COMP-ALT-11's wider sweeps ever pinch these margins, the
by-construction fallback is self-timed CKL: a skewed NOR across DIP1/DIP2 fires
the latch at a fixed point on the bucket trajectory instead of a fixed time.)

**Delay results** (`comparator_alt/sim/run_comp2_delay_corners.sh`, measured CK
rising VDD/2 → losing VOUT1 falling VDD/2, Vcm=VDD/2, loads per tb):

| corner | CKL=2.6n | CKL=2.8n (design) | CKL=3.0n | od=0.1mV @2.8n |
|---|---|---|---|---|
| FF/−40C/3.63V | 741 ps | **950 ps** | 1174 ps | 989 ps |
| TT/ 27C/3.30V | — | **1024 ps** | — | 1078 ps |
| SS/125C/2.97V | 1110 ps | **1274 ps** | 1435 ps | 1283 ps |

Worst case at the design point: **1.27 ns (SS), 36% margin to the 2 ns spec**;
near-zero-overdrive runs resolve in ~1.0–1.3 ns everywhere (no schematic-level
metastability hazard). All runs od=0.5LSB=6.457mV unless noted.

**Offset MC re-run after the resize** (tb Simulate, N=100, good=100/100,
CKL=2.8n): **mean = −0.296 mV, σ = 1.128 mV** — vs 1.088 mV before the resize;
0.04 mV of σ traded for the corner margin. 33× below the 36.9 mV baseline,
44% margin to the 2 mV target. Gate-1 (alt) offset + delay both PASS at
schematic level.

**Reminder:** `comparator_alt/layout/preamp_dyn.gds` tail device is now two
revisions stale (m=5→m=1, then W=2u→1u) — redraw before COMP-ALT-12/13. PEX
(COMP-ALT-14) remains the post-layout confirmation of both numbers.

## 2026-08-05 — COMP-ALT-11: full operating-grid characterization, CKL retuned 2.8n → 3.1n — CLOSED

**Method:** two 120-point functional screens (5 corners incl. sf/fs × VDD 3.0/3.3/3.6 ×
8 input points, single-shot, polarity-aware verdicts sampled late in the strobe window),
plus boundary probes, delay re-cert, and deep MC. Harnesses:
`comparator_alt/sim/run_alt11_screen.sh` (pure common-mode, both inputs together — a
stress test beyond what the ADC can produce) and `run_alt11_screen_realistic.sh`
(VIN2 pinned to VDD/2 as in the SAR, VIN1 swept 3–97% of VDD — every condition the ADC
CAN produce).

**Finding 1 — low-Vcm wrong-polarity zone (pure-Vcm screen).** Below a corner-dependent
common-mode (~0.7–1.6 V), the preamp input pair cannot conduct; the latch then fires
into two undrained (full-VDD) inputs and decides by its own internal asymmetry —
**deterministic wrong answers, not non-decisions**. Boundary tracks VT: worst at
ss/3.0V (needs ≥1.3V at CKL=3.1n), best at ff (≥0.7V). This is device physics (NMOS
input pair), same class as COMP-5's documented ≥0.85V limit; unfixable by sizing.

**Finding 2 — the realistic-drive screen caught a real ADC-level bug at CKL=2.8n.**
With VIN2=VDD/2, the ss/3.0V row still failed WRONGPOL for inputs ≤0.30·VDD: at that
triple pileup, mid-rail (1.5V) itself drives the reference-side pair so weakly that the
correct differential develops too slowly for a 2.8n strobe — the latch fires while the
buckets are still nearly equal. The "one faucet is always open" argument was falsified
by measurement at exactly one row of fifteen. Fix: strobe later.

**Window edges measured** (probe scripts `probe_ckl_retune.sh` / `probe_ckl_edges.sh`):
ss/3.0 floor between 2.8–2.9n (below: wrong answers); FF ceiling ≈3.25n for 0.1mV
overdrive (~3.35n at 0.5LSB; above: no decision). **Global fixed-strobe window ≈
(2.9, 3.25) ns. CKL retuned to 3.1n**, biased away from the floor because its failure
mode (systematic wrong codes over an input range) is worse than the ceiling's
(occasional non-decision on ~0.1mV ties). tb_2stage.sch updated.

**Re-certification at CKL=3.1n:**
- Realistic-drive grid: **all 15 corner×supply rows PASS over the full input range.**
  Correct decision for every input the ADC can present — no restrictions.
- Pure-Vcm grid: dead-zone boundary improves ~one column at every corner vs 2.8n
  (later strobe gives weak drive more time); ss/3.0 boundary 1.65→1.3V.
- Delay (od=0.5LSB / 0.1mV): TT 1.32/1.38 ns; **SS 1.52/1.58 ns (binding, 21% margin
  to 2 ns)**; FF 1.29/1.36 ns. Budget split ≈1.05ns strobe wait + ≈0.5ns latch.
- Offset MC: **TT N=200, 200/200 good: mean −0.12 mV, σ = 1.141 mV** (sign-off number;
  consistent with N=100 runs 1.10–1.13). **Worst survivor ss/125C/3.0V, N=100, ramp
  re-centered to 1.5V (`make_mc_ss30_deck.sh`): mean −0.21 mV, σ = 1.287 mV** — 36%
  margin to 2 mV even there (0.11 LSB at that supply's 11.7mV LSB).

**Standing notes for layout/PEX and integration:**
1. Parasitics slow the preamp and slide the whole CKL window later — re-map the edges
   at COMP-ALT-14 and retune the number if needed. The deliverable is the WINDOW MAP,
   not the 3.1n constant: whoever designs the on-chip CKL generator designs against it.
2. If post-layout margins pinch, the by-construction fallback is a self-timed strobe:
   a skewed NAND across DIP1/DIP2 (fires when EITHER bucket crosses trip — a NOR would
   deadlock on the ss/3.0 slow-drip case, which this campaign is what taught us).
3. The pure-Vcm dead zone stays out of PROGRESS-level caveats because the ADC cannot
   reach it (reference input is hard-wired to VDD/2) — but any future reuse of this
   comparator in another context must re-check input common-mode against the pure grid.

**Artifacts:** `comparator_alt/sim/alt11_screen{,_realistic}/` (grids + CSVs; grid-file
titles from before 2026-08-05 may carry a stale hardcoded "CKL=2.8n" label — runs after
the tb update used 3.1n; scripts now self-label from the netlist),
`alt11_probe_{retune,edges}/`, `comp2_delay/comp2_delay_corners_summary.txt`,
`comparator_alt/results/{comp2_mc_*,mc_ss30_*}`.

## 2026-08-06 — COMP-ALT-12/13: two-stage top-level layout — DRC/LVS clean, polarity verified in extracted metal

**Assembly:** `comparator_alt/layout/comparator_2stage.gds` — vertical stack (preamp
below, latch above), both verified bricks placed as instances. DIP1/DIP2 risers are
mirror-image Metal2 twins about the shared symmetry axis (DIP1→VIN1, DIP2→VIN2, same
order both cells — no crossing), each crossing the mid VDD rail identically. CK made
to cross both twins at equal width (equal coupling → common-mode, cancels). VDD/VSS
strapped on BOTH sides symmetrically (VSS inner / VDD outer verticals, 2×2 via arrays).
DRC clean. Flat LVS (per-cell-reference-assembled netlist
`comparator_2stage.spice`): netlists match.

**Challenges worth remembering:**
1. **PCell regeneration on cross-layout paste.** PDK transistors are parametric
   cells; GUI copy-paste re-runs their generators in the target layout's context. A
   new layout accidentally created at DBU 0.01 (bricks are 0.005) regenerated every
   PCell at the wrong scale — devices shrank while hand-drawn wires stayed put.
   Rules: match DBU before importing; verify a known device dimension with the ruler
   after any cross-layout move; batch-mode file merges avoid regeneration entirely.
2. **Inherited labels & crossed net names.** Both cells internally name their inputs
   VIN1/VIN2 and their clock CK, so flat extraction sees duplicate names on different
   nets — tolerated (topology decides matching; names are bookkeeping). Separately,
   the schematic's lab_wire names DIP1/DIP2 are crossed relative to the pin-to-pin
   connectivity (diagonal wires + labels cancel): electrically straight, visually
   misleading. TODO (post-deadline): rename the lab_wires so net names match pins.
3. **THE catch — swapped CK/CKL labels, and what LVS cannot promise.** Both cells
   call their clock pin "CK"; the two top-level clock texts ended up on each other's
   nets (CKL on the preamp clock, CK on the latch clock). **LVS passed anyway** —
   KLayout pairs top-level pins topologically, and the netlists are isomorphic under
   a CK↔CKL identity exchange. The extracted-netlist behavior check
   (`comparator_alt/sim/run_polarity_check.sh`, drives ports BY NAME) immediately
   produced consistent wrong-direction decisions; reading the extracted X-lines
   showed CKL on the preamp instance's clock pin. Fix: swap the two texts (zero
   metal). At SAR integration the wrong-named clock would have been a chip-level
   timing bug. **Lesson: LVS validates the graph; labels are identity; only a
   behavioral simulation validates intent.**

**Final verification:** LVS re-run clean with corrected labels; polarity check on
`comparator_2stage_extracted.cir` (device-level extraction, M→X + AS/AD/PS/PD-strip
conversion automated in the script): **PASS both directions** (VIN1<VIN2 → VOUT1
falls; VIN1>VIN2 → VOUT2 falls) at the CKL=3.1n design point. Twins confirmed
straight in extracted connectivity (preamp DIP1→latch VIN1 via net $3).

**Standing notes:** standalone `strongarm_2.gds` is the pre-clock-symmetry-edit
archive — the assembly's copy is the living version. Next: COMP-ALT-14 PEX — re-verify
offset σ, delay, and the CKL window edges with parasitics, plus the twins' extracted
C-symmetry (the one asymmetry source device-level extraction cannot see).

## 2026-08-11 — COMP-ALT-16 step 1: polarity wrapper `comparator_alt` — built and verified

**What:** new cell `comparator_alt/schematic/comparator_alt.sch`/`.sym` — contains
`comparator_2stage` with the **outputs deliberately crossed** (instance VOUT2 → wrapper
VOUT1 and vice versa), so the block presents COMP-5's convention required by the glue:
**VIN1 > VIN2 ⇒ VOUT1 falls ⇒ SR latch CMP_OUT=1 = keep** (docs/pin_contracts.md §1/§4).
CKL remains a pin for now; the ALT-16 delay chain replaces it next, and the symbol's
port order gets reshuffled to the contract's strongarm order at the same time.

**Verified** with `comparator_alt/sim/run_wrapper_polarity.sh` (drives ports by name,
expects COMP-5 convention, prints which netlist + DUT line it checked):
- negative control, bare `tb_2stage`: STILL-ALT-CONVENTION both cases ✓
- `tb_comparator_alt` (wrapper): **PASS both cases** ✓

**Debug story worth keeping:** the first wrapper run ALSO reported STILL-ALT with
waveforms bit-identical to the bare run — same digits = same circuit (determinism as a
fingerprint). Cause: after a symbol regeneration, the testbench's VOUT labels had been
re-attached by position, crossing the outputs a second time — two swaps cancel. Fix:
reattach tb labels by name. Related detour: an earlier "both PASS" was a run mix-up the
script couldn't expose because it didn't say what it checked — it now self-labels
(netlist path + DUT instance line in every verdict block).

**xschem gotchas recorded:** `vdd.sym`/`gnd.sym` are global-net symbols, not pins — use
`iopin` for supplies that must appear on a generated symbol; "Make schematic from
symbol" is the REVERSE of "Make symbol from schematic" (key `a`); placed instances keep
a cached symbol after regeneration — close/reopen the schematic to refresh.
Also: `grep -l comparator_alt` false-matched a netlist via its sch_path comment (the
FOLDER is named comparator_alt) — grep the instance line, not any substring.

**Environment note:** the repo lives in iCloud-synced Documents; macOS had evicted
PROGRESS.md/WORKLOG.md (and previously the COMP-5 sim templates + handoff README) to
placeholders. Hydrate with `brctl download <repo>` (find -exec for full recursion).
Long-term fix (post-deadline): move git repos out of iCloud-synced paths.

## 2026-08-14 — COMP-ALT-17: native-VT spike PASS, after a day of ghosts

Result: `nfet_06v0_nvt` pair (4u/2u, nf=1 m=16, 128 µm²) → **floor ≤0.4 V at every
corner** (was 1.0–1.3 V), **σ = 1.27–2.21 mV TT** (assumption bracket, N=200),
2.04 mV at ss/125°C/3.0V. Corner timing closes under the tracking CKL chain with a
RE-MAPPED spec: TT ≈1.2n / ff ≤0.8n / ss 1.6–2.6n / sf ≤2.3n, tfall <0.3n.
ALT now beats COMP-5 on BOTH input range and offset. Row: PROGRESS COMP-ALT-17.

The traps, in the order they bit:

1. **GHOST CAMPAIGN.** A full screen + probes + MC ran against a week-old netlist
   (03v3 pair). Caught by the determinism fingerprint: MC σ printed 1.14137 mV —
   the old baseline, digit for digit. Identical digits = identical circuit.
   **NEW RULE: no campaign starts until the netlist fingerprints** (grep for the
   device that is supposed to be in it + check the file mtime).
2. **TAB TRAP.** xschem's Netlist button netlists the ACTIVE TAB; the wrapper tb
   was active, so tb_2stage.spice stayed a week stale while the button went green.
   CLI netlisting is deterministic:
   `xschem --netlist --quit --no_x -o <simdir> <sch>`.
3. **`model=` ATTRIBUTE TRAP.** After replacing the pair symbol, the canvas showed
   `nfet_06v0_nvt.sym` but the instances still carried `model=nfet_06v0` (and one
   device had been auto-renamed M1P→M1, which would have silently broken the MC
   alter paths). The netlister emits `model=`, not the symbol name. The netlist is
   the circuit; the canvas is a picture.
4. **Multi-line netlist lines:** `grep "^XM1P"` misses `+` continuation lines —
   the m=16 was there all along. Use `grep -A`.
5. **nvt BIN FLOOR:** the model exists only for **L ≥ 1.8u** ("could not find a
   valid modelname" on every deck at L=1u). Fix L=2u — which doubled pair area and
   clawed back most of the native matching penalty. (Related recorded gotcha: the
   03v3 trips "u0 not positive" at L=2u — tune chain delay by STAGE COUNT, not L.)
6. **PDK ships NO mismatch statistics for nfet_06v0_nvt** (bare subckt, no
   mis_vth — unlike 03v3's `agauss(0,var_vth,1)`). σ built from the foundry
   coefficient of the regular 6V NMOS (par_vth=0.01155 → 8.17 mV·µm per device,
   ×0.7071 per the PDK's own var_vth formula) with a **2× native penalty as a
   stated assumption**, bracketed by a 1× run (1.27 mV). The PDK's 03v3
   coefficient (5.05 mV·µm/dev) independently validates our long-standing
   6.2 mV·µm as ~20% conservative.
7. **Mac disk at 99%** silently truncated sim logs mid-line through the grpcfuse
   mount (no ngspice error — the RESULT line just never landed) and drove the
   iCloud eviction wave. Sims now write to container-local disk first.
8. **Repo moved out of iCloud → `~/Developer/`** (mid-session). Note: iCloud's
   "Desktop & Documents" sync covers `~/Documents`, so a GitHub/ folder there was
   still being evicted. Docker mount fixed by container remove + recreate from the
   new cwd (`start_chipathon_vnc.sh` mounts `$(pwd)`; a restart keeps the old
   mount). The eviction era should be over.

Also drawn today (harness-ready even though Bruno built his own chain): `inv_slow`
(1u/1u + 2u/1u), `ckl_gen` (6× inv_slow + NAND2 + INV, all verified topology),
`tb_ckl_gen` — plus lessons: fresh-placed devices need `spiceprefix=X` added, and a
tb VSS *label* floats — use the gnd symbol (tb_2stage pattern) or a Vvss source.
Bruno's chain must be characterized against the NEW delay spec above
(`run_cklgen_corners.sh`); a chain sized to the old ~1.05n target may strobe ff late.

Open items out of the spike: ss×−40°C floor probe (the corner that set the ADC's
0.70 V bound — if nvt holds ≤0.6 there, promotion WIDENS the ADC input range);
chain characterization + drop into tb_2stage replacing the ideal Vckl; PEX (ALT-14)
re-check with nvt; layout pair redraw 4u×2u×16 (ALT-15).
