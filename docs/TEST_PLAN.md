# Post-silicon test plan — A13 Hungry Chippos 8-bit SAR ADC

Bench characterization of the `adc_top` block after the January 2027 GF180MCU
shuttle. Testing happens at Brown University (School of Engineering labs) by
the team listed in the [README](../README.md). Every measurement below has a
simulated target in the README headline table, so each result is reported as
measured vs. simulated.

## Interface under test

| Pin | Type | Use during test |
| :--- | :--- | :--- |
| VDD / VSS | power / ground | Single 3.3 V supply; VDD is also the DAC reference |
| CLK | input (Schmitt) | 10 MHz nominal; 12 CLK cycles per conversion (833 kS/s) |
| RST_N | input | Active-low reset of the SAR logic |
| VIN | analog (secondary ESD) | Single-ended input, quoted range 0.70–3.25 V |
| EOC | output | End-of-conversion strobe; latch BIT_7..BIT_0 on it |
| BIT_7..BIT_0 | outputs | Parallel 8-bit result, BIT_7 = MSB |

## Equipment

- Bench supply with current readout (3.3 V, ±10 % sweep)
- Function generator for CLK (square, 1–10+ MHz) and VIN (low-distortion sine)
- Precision DC source or 16-bit DAC for slow VIN ramps
- Logic analyzer or MCU/FPGA capture board triggered on EOC
- Oscilloscope, DMM
- Test PCB with socket, decoupling on VDD, RC anti-alias filter on VIN

## Procedure

1. **Power-up and current.** Ramp VDD to 3.3 V with current limit set low.
   Record static current with CLK stopped and RST_N low, then dynamic current at
   10 MHz. Pass: no latch-up, current stable.
2. **Reset and handshake.** Hold RST_N low, release, apply CLK. Confirm EOC
   toggles once every 12 CLK cycles and BIT_7..BIT_0 change only around EOC.
3. **Functional sanity.** Apply DC VIN at 0.70 V, mid-scale, and 3.25 V. Confirm
   codes near the bottom, middle, and top of the range and that they track VIN
   monotonically.
4. **Static transfer (DNL / INL).** Sweep VIN slowly across the full range
   (ramp or ≥ 16× oversampled steps), capture codes, and compute DNL/INL with
   the histogram method. Pass: monotonic, no missing codes across the quoted
   range.
5. **Dynamic performance (SNDR / ENOB).** Apply a coherently sampled sine near
   full scale at 833 kS/s, capture ≥ 4096 codes, FFT. Report SNDR, SFDR, ENOB.
   Target: ENOB ≈ 7.2 b.
6. **Supply and clock sweeps.** Repeat steps 3–5 at VDD = 3.0, 3.3, 3.6 V and
   at CLK = 1, 5, 10 MHz (and above 10 MHz until conversions fail) to find
   margins.
7. **Input range.** Find the lowest and highest VIN that still give monotonic
   codes; compare against the quoted 0.70–3.25 V.
8. **Multiple dies.** Repeat steps 1–5 on every die received to see
   part-to-part spread (comparator offset, gain error).

## Deliverables

Raw captures, analysis scripts, and a results summary go in `results/silicon/`
in this repo, and get shared with the Chipathon organizers.
