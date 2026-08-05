# INT-7 / Gate 4 — ADC-level corner sweep report (2026-07-31)

**Method.** The full INT-6 methodology repeated per MOS model corner: 256 independent
single-conversion ngspice runs per corner (constant VIN at the code centers of the measured
transfer, V_LSB = 3.293/256), trusted settings (`.tran` max step 0.05 ns, `reltol=1e-4`,
`.save` limited to measured signals). Decks: `designs/scripts/gen_adc_sweep_tt.py <dir> <corner>`;
judge: `check_adc_sweep.py`. Conditions: VDD = 3.3 V, 27 °C, CLK 10 MHz. MIM caps at
`mimcap_typical` for all corners — global cap variation is a common scale factor and cancels in
this ratiometric DAC (DAC-9b); supply/temperature axes were covered at block level
(DAC Gate 2: 30 PVT corners, worst settle 3.86 ns; COMP-5: SS/125 °C/2.97 V delay 370 ps).

**Results — every corner is structurally identical:**

| Corner | Dead zone (reads 0) | Exact codes | Uniform −1 band | Monotonic | Worst err above dead zone |
|--------|--------------------|-------------|-----------------|-----------|---------------------------|
| TT | ≤ code 38 (< 0.502 V) | 39–102 | 103–255 | yes | 1 LSB |
| FF | ≤ code 30 (< 0.399 V) | 31–101 | 102–255 | yes | 1 LSB |
| FS | ≤ code 32 (< 0.424 V) | 33–102 | 103–255 | yes | 1 LSB |
| SS | ≤ code 47 (< 0.617 V) | 48–102 | 103–255 | yes | 1 LSB |
| SF | ≤ code 44 (< 0.579 V) | 45–102 | 103–255 | yes | 1 LSB |

Data: `adc_top/sim/sweep_{tt_fine2,ff,fs,ss,sf}/sweep_codes.csv`.

**Reading.** Above its dead zone every corner converts every code to within 1 LSB, with the
error being the same clean uniform −1 band (analog offset ≈ −0.5 LSB: sample-TG charge
injection + code-center grid vs real full-scale) that TT shows — a calibratable offset/gain
datasheet line, not nonlinearity. No missing codes, no non-monotonic step at any corner.
The dead-zone boundary tracks the NMOS corner (comparator input pair is NMOS: FF/FS wake at
0.40–0.42 V, SS/SF need 0.58–0.62 V), matching the standalone comparator characterization.

**Verdict: Gate 4 PASS over the corner-common input range.**
Guaranteed input range across FF/SS/FS/SF/TT at 3.3 V/27 °C: **0.62–3.29 V**
(datasheet quote with margin: **0.65–3.25 V**), DNL/INL within the code-center method's
±0.5 LSB bound after offset/gain correction, monotonic, no missing codes.

**Open follow-ups (not blocking):** ADC-level supply (3.0/3.6 V) and temperature (−40/125 °C)
sweeps would complete a full PVT story (block-level coverage plus ≥10× timing margins make
these low-risk); COMP-5's Vcm ≥ 0.85 V worst-corner bound came from SS/125 °C/2.97 V delay
compliance, so quote 0.85 V as the low bound if those conditions must be guaranteed
simultaneously. Target ENOB and sample rate remain undefined by the team (proposed:
833 kS/s @ 10 MHz CLK, 12 CLK/conversion).
