# INT-2 — ADC Top-Level Pin Contracts & Wiring Map

> Status: **decided 2026-07-30** (this document is the contract for INT-3/4/5 stitching).
> Sources of truth: `comparator/schematic/strongarm.spice` (LVS-proven), `sar_logic/sim/sar_logic_subckt.spice`
> (SAR-3-verified), `dac/layout/dac_top_ref.spice` (Gate-5 LVS reference). Port orders below are copied
> verbatim from those netlists — **instantiate in exactly this order**.

---

## 1 · Block interfaces (as built and signed off)

### DAC — `cap_array` / `dac_top_floorplan` (12 pins)

```
.subckt dac_top_floorplan VIN VDD SAMPLE B0 B1 B2 B3 B4 B5 B6 B7 DAC_TOP
```

| Pin | Dir | Function |
|-----|-----|----------|
| VIN | in (analog) | TG-sampled onto DAC_TOP while SAMPLE=1. **Tied to VSS at ADC top** (see §3) — SAMPLE becomes a reset-DAC_TOP-to-0V phase. |
| VDD | supply | 3.3 V. Also the DAC reference (VREF=VDD rework, DAC-3b). |
| SAMPLE | in (digital) | 1 → TG closes (DAC_TOP:=VIN) **and** all bottom plates forced to GND (`BOTn = Bn AND SAMPLE_N`). 0 → convert: `BOTn = Bn·VDD`. |
| B0…B7 | in (digital) | Bit switch controls, B7 = MSB (weight 128·Cu). |
| DAC_TOP | out (analog) | Common top plate. After a SAMPLE with VIN=VSS: `V = code/256 · VDD · C_tot/(C_tot+C_par)` (measured FS 3.293 V, DAC-9). |
| *(no VSS pin)* | — | Ground is the **global `0` net** inside the DAC subckt (gnd.sym instances). At ADC top, VSS must be the same node as SPICE ground `0`. |

### Comparator — `strongarm` (7 pins)

```
.subckt strongarm VDD CK VOUT2 VOUT1 VIN1 VIN2 VSS
```

| Pin | Dir | Function |
|-----|-----|----------|
| CK | in | 1 → evaluate, 0 → precharge/reset (both outputs precharge **high**). |
| VIN1 / VIN2 | in (analog) | NMOS input pair (M10 / M8). Vcm compliance ≥ 0.85 V worst corner (COMP-5); hard fail ≤ 0.6 V. |
| VOUT1 / VOUT2 | out | **Polarity (from netlist topology): VIN1 > VIN2 ⇒ VOUT1 falls to 0, VOUT2 stays/latches 1.** (M10 gate=VIN1 discharges net3, M9 pulls VOUT1 low.) So the logic-high indicator of "VIN1 wins" is **VOUT2**. Re-verify by sim in the INT-5 TB before trusting downstream. |
| VDD / VSS | supply | 3.3 V / 0. |

### SAR controller — `sar_logic` (14 pins)

```
.subckt sar_logic VDD VSS BIT_7 BIT_6 BIT_5 BIT_4 BIT_3 BIT_2 BIT_1 BIT_0 EOC RST_N CMP_OUT CLK
```

| Pin | Dir | Function |
|-----|-----|----------|
| CLK | in | All 17 FFs clock on **rising** edges. 10 MHz verified (SAR-3). |
| RST_N | in | Async, active-low. Doubles as start-of-conversion: release starts the MSB trial shift. During reset: BIT_7=1 (S7 is a `dff_set_n`), BIT_6..0=0, EOC=0. |
| CMP_OUT | in | **1 = KEEP the trial bit = "VIN > VDAC"** (verified: SAR-3 codes = floor(VIN·256/3.3) with this convention). Must be valid *before* each rising CLK edge and stable through it (code FFs C_i clock on sequencer taps that fire on CLK rising edges). |
| BIT_7..0 | out | Trial/kept code, straight binary, drives DAC B7..B0. |
| EOC | out | Rises on the **8th rising CLK edge after RST_N release** (~901 ns in the SAR-3 TB with release at 150 ns, T=100 ns). C0 latches the LSB decision on the EOC rising edge; code then holds. |

---

## 2 · The conversion scheme (decided)

**DAC runs as a pure VDAC generator; the ADC input goes directly to the comparator.**

Why (and why not the alternatives): as built, the DAC forces **all bottom plates to GND during
SAMPLE** (`BOTn = Bn AND SAMPLE_N`) and top-plate-samples its VIN pin. Charge conservation then gives
`V(DAC_TOP) = VIN_sampled + VDAC(code)` during conversion. Therefore:

- *Sampling the ADC input on the array* (VIN_adc → DAC.VIN) pushes DAC_TOP to `VIN + 1.65 V` on the
  MSB trial — up to **4.95 V**, forward-biasing the sample-TG PMOS drain→nwell diode (nwell at VDD,
  clamps ~3.9 V) and destroying the sampled charge for any VIN > ~2.25 V. Rejected.
- *A fixed mid-rail reference on VIN2* carries no VIN information: with VIN only on the array,
  `[DAC_TOP > 1.65]` cannot compute `[VIN > VDAC]` over the full range. Rejected.
- The classic McCreary bottom-plate-sampling arrangement would fix both, but the signed-off DAC has
  no VIN path to the bottom plates anymore (removed in the VREF=VDD rework). Not available.

The chosen scheme is **exactly the configuration in which every existing sign-off was run**:
DAC-9's INL/DNL sweep (sample VIN=0, DAC_TOP = code·V_LSB) and SAR-3's binary search
(CMP_OUT = [VIN > VDAC], VDAC from 0). Nothing is re-qualified, everything composes.

**Consequence (deliberate scope decision):** there is **no on-chip S/H of the ADC input** — VIN_adc
must stay within ±½ LSB (±6.5 mV) during the 8-trial conversion (~0.8 µs @ 10 MHz ⇒ full-scale
sinusoid BW limit ≈ 1.5 kHz; DC/stepped inputs, as used for INL/DNL testing, are unaffected).
The DAC's TG + SAMPLE phase is retained as the DAC_TOP **reset-to-0V** switch (hold-droop and
charge-injection numbers from DAC-4c still apply).

---

## 3 · Net-by-net wiring map (`adc_top`)

| Net (adc_top) | From | To |
|---|---|---|
| `VIN` (ADC analog input pad) | pad | comparator `VIN1` |
| `DAC_TOP` | DAC `DAC_TOP` | comparator `VIN2` |
| `VSS` | rail | DAC `VIN` (reset reference = 0 V), comparator `VSS`, sar_logic `VSS`, glue-cell VSS. Must be SPICE node `0` (DAC internal grounds are global `0`). |
| `BIT_i` (i=0..7) | sar_logic `BIT_i` | DAC `B_i` — **straight, no inversion** (BIT_7→B7=MSB). Also to output pads. |
| `CMP_OUT` | SR-latch `Q` (glue, §4) | sar_logic `CMP_OUT` |
| `VOUT1`, `VOUT2` | comparator | identical inverter buffers → NOR SR latch (§4) |
| `CK` | glue: `CK = INV(CLK)` | comparator `CK` |
| `SAMPLE` | glue: `SAMPLE = INV(RST_N)` | DAC `SAMPLE` |
| `CLK`, `RST_N` | pads | sar_logic + glue |
| `EOC` | sar_logic `EOC` | pad |

**Comparator polarity check:** keep ⇔ VIN_adc > VDAC ⇔ VIN1 > VIN2 ⇒ VOUT1 falls, VOUT2 = 1
⇒ SR latch must set `CMP_OUT = 1` when **VOUT1** falls (see §4). This matches the SAR's
"CMP_OUT=1 = keep" convention.

### ADC top-level pin list (13 pins — fits padring slot B, 16 available)

`VDD, VSS, VIN, CLK, RST_N, EOC, BIT_7..BIT_0` (SAMPLE and CK are derived on-chip; no external
reference pin is needed — a deliberate benefit of the chosen scheme).

---

## 4 · Glue logic (new, schematic-level, lives in `adc_top`)

Three tiny cells, reusing existing proven sub-cells:

1. **CK inverter** — `CK = INV(CLK)` (sar_logic `inv` cell). Comparator evaluates during the CLK-low
   half-period, resets during CLK-high.
2. **Decision latch — buffered NOR SR latch** (2× sar_logic `inv` + 2× sar_logic `nor2`):
   `V1B = INV(VOUT1)`, `V2B = INV(VOUT2)`, then `CMP_OUT = Q = NOR(V2B, QB)`, `QB = NOR(V1B, Q)`.
   StrongARM precharge (both VOUT high ⇒ both V*B low) = NOR-latch hold state, so the decision
   survives the comparator's reset phase and the C_i-latch race the SAR-3 TB had to model with a
   1 ns RC is eliminated structurally. VOUT1 falls (keep) → V1B=1 → QB=0 → Q=1; VOUT2 falls → Q=0.
   ⚠️ **Do not connect the comparator outputs directly to a NAND SR latch.** Found in INT-5 sim:
   the NAND whose second input is enabled by the *held* state presents a larger (Miller) input
   capacitance than the disabled one, so the comparator sees state-dependent asymmetric loads. In
   the low-gain near-rail regime this biased every decision toward repeating the previous one
   (sticky keeps ratcheted VIN=3.25 V to code 255). The identical inverter buffers make both
   outputs see the same state-independent load.
3. **SAMPLE inverter** — `SAMPLE = INV(RST_N)` (reset phase = DAC_TOP reset phase).

## 5 · Phasing

```
CLK      ‾\__/‾‾\__/‾‾\__/‾‾\__ ...            (10 MHz, T=100 ns; FF edges on ↑)
RST_N    ____/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾ ...            (release during a CLK-HIGH phase — see below)
SAMPLE   ‾‾‾‾\________________ ...            (= ~RST_N: DAC_TOP reset ends at release)
trial i        [BIT set on CLK↑]--DAC settles (≤3.9 ns worst corner)--
CK       __/‾\__/‾\__/‾\__ ...                (= ~CLK: strobe on CLK↓, mid-trial)
CMP_OUT        [SR latch updates ≤1 ns after CK↑; stable through next CLK↑]
EOC      ______________________/‾‾  (8th CLK↑ after release; code valid & held)
```

- **RST_N release phasing constraint:** RST_N must be released during a **CLK-high** half-period.
  The comparator strobes on CLK falling edges (CK=~CLK); the MSB trial's B7 asserts at RST_N release
  (S7 is set during reset), so the release must happen *before* the falling-edge strobe of its own
  trial window. Releasing during CLK-low would make trial 7 latch a stale pre-release comparison
  (DAC_TOP still at 0 V ⇒ MSB always kept). Release early in the CLK-high phase leaves ≥45 ns for
  the MSB settle before the strobe.
- Trial bit asserts on a rising CLK edge → DAC has a **half period (50 ns)** to settle
  (needs 3.9 ns worst corner, Gate 2) → comparator strobes at the falling edge → decision latched in
  the SR latch ~370 ps later (worst corner, COMP-5) → SAR C_i FF captures it on the next rising edge
  with ~49 ns of margin. Timing closes with >10× slack at 10 MHz; nothing here limits CLK below
  ~100 MHz except re-verification effort.
- One full conversion: RST_N low ≥ 1 CLK period, then 8 trial edges + EOC. **Proposed rate spec:
  12 CLK per conversion ⇒ 833 kS/s @ 10 MHz** (pending team ratification — sample-rate/ENOB targets
  are still the open spec items).

## 6 · Caveats / open items

1. **Comparator valid common-mode window — low end only** *(final, from the INT-6 definitive
   sweep + standalone characterization; supersedes the earlier "high-end inversion" note).*
   *Low end (real):* the NMOS-input StrongARM does not resolve below Vcm ≈ 0.5–0.6 V at TT
   (standalone characterization: dead ≤ 0.5 V, perfect 0.6–3.3 V down to ±3.2 mV). In-system,
   codes 1–38 (VIN < 0.50 V) read 0. COMP-5's worst-corner compliance bound is Vcm ≥ 0.85 V.
   ⇒ **TT input range: 0.50–3.29 V** (codes 39–255, every one within 1 LSB incl. the top code);
   worst-corner guaranteed range to be set by Gate 4 (expect ≥ 0.85 V low bound per COMP-5).
   *High end:* **no upper restriction.** The "StrongARM inverts decisions near VDD" finding
   reported during INT-5 was a **simulation artifact of coarse settings** (0.1–0.5 ns max step /
   default reltol corrupt the sub-ns regeneration); at 0.05 ns + reltol=1e-4 the standalone
   comparator, the trusted-settings node trace, and the definitive 256-code sweep all agree:
   decisions are correct up to the top code. Always simulate this comparator with
   `.tran` max step ≤ 0.05 ns and `reltol=1e-4`.
2. **Input bandwidth** (no input S/H) — see §2. Fine for chipathon testing; flag in the datasheet.
3. VOUT1/VOUT2 polarity in §1 — **confirmed in-system by INT-5**: with keep wired as "VOUT1 falls"
   (via the buffered NOR latch), mid-range closed-loop conversions are exact (0.6→46, 2.9→225).
4. The glue cells (2× nand2, 2× inv) are schematic-level here; they must be added to the top-level
   layout at INT-8 (trivial area, standard cells already have proven layouts in `sar_logic`).
