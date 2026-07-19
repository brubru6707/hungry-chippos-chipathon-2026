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
