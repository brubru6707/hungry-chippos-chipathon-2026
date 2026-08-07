# ADC Glossary — Key Terms & Definitions

A plain-language reference for the specs and concepts that keep coming up in our
schematic reviews. Each term uses our actual 8-bit SAR ADC as the example so the
numbers are ones we'll actually see in simulation.

---

## Resolution

**What it means:** the number of bits, *N*, the ADC uses to represent the analog
input. This sets how many distinct digital output codes exist: **2^N**.

**Our chip:** 8-bit resolution → **2^8 = 256** possible output codes (0 to 255).

**Why it matters:** resolution alone doesn't tell you accuracy — it just tells you
how finely the output *scale* is divided. A comparator with too much offset can
still ruin an 8-bit converter's real-world accuracy (see ENOB below).

---

## LSB (Least Significant Bit)

**What it means:** the voltage represented by one step of the smallest bit — i.e.
the smallest voltage change the ADC can distinguish. It's the "ruler tick mark"
size of the whole converter.

**Formula:**
```
1 LSB = V_ref / 2^N
```

**Our chip:** our proposal specs an external `V_REF = 1.65 V` (supply is a
separate 3.3 V — don't mix the two up), with `N = 8`:
```
1 LSB = 1.65 V / 256 ≈ 6.45 mV
```

**Why it matters:** almost every other spec is measured *in LSBs*, not raw volts —
"DNL < 0.5 LSB" means "the step size never drifts by more than half of one 7 mV
tick." This is also why comparator offset matters: an offset bigger than ~1 LSB
starts flipping decision bits and corrupting the output code.

---

## DNL / INL (mentioned alongside ENOB — worth knowing too)

- **DNL (Differential Non-Linearity):** how much any single output step deviates
  from the ideal 1 LSB size. Ideal DNL = 0 for every step.
- **INL (Integral Non-Linearity):** the cumulative deviation of the whole transfer
  curve from a straight line, measured across all 256 codes.

**Our gate:** Gate 3 in `PROGRESS.md` requires DNL/INL < 0.5 LSB at the TT corner.

---

## DAC / CDAC (Capacitor DAC, charge-redistribution)

**What it means:** in a SAR ADC, the "DAC" isn't a separate chip block that
takes a digital code and outputs a voltage the normal way — it's an array of
**8 binary-weighted capacitors** (1×, 2×, 4×, 8×, ... 128× a unit capacitor
`C_u`) that do double duty as both the sample-and-hold *and* the digital-to-
analog part of the binary search. This is why it's usually called a **CDAC**
(capacitor DAC) or **charge-redistribution DAC**.

**How a conversion actually happens (bottom-plate switching, our scheme):**
1. **Sample phase:** every capacitor's bottom plate is switched to `V_IN`.
   All 8 top plates are tied together into one common node (`DAC_TOP` in our
   schematic) — this common node is now holding a charge proportional to
   `V_IN` across the whole 256×`C_u` array.
2. **Bit-trial phase (8 steps, one per bit, MSB first):** the SAR controller
   flips one bottom plate at a time between `V_REF` and `GND` and asks the
   comparator "did `DAC_TOP` cross the threshold?" Each flip either gets kept
   (bit = 1) or undone (bit = 0) based on the comparator's answer, exactly
   like a "guess the number" binary search.
3. After 8 trials, the kept/undone decisions *are* the 8-bit output code —
   there's no separate "convert code to voltage" step, the charge
   redistribution across the caps **is** the conversion.

**Why binary-weighted?** Each bit's capacitor is sized as a power-of-two
multiple of the unit cap, so flipping bit *i*'s switch moves the shared
top-plate node by exactly half the voltage step that flipping bit *i+1*
would — which is what makes the binary search valid. This also means the
whole 256×`C_u` array is really just **255 identical unit capacitors wired in
parallel groups** (1, 2, 4, 8 ... 128 of them per bit) rather than 8
differently-sized ones — good for matching, since fabricating many identical
small devices tracks much better across the die than fabricating capacitors
of 8 different physical sizes.

**Our chip's numbers:** `C_u ≥ 50 fF` (see the kT/C section above for why),
8 caps at weights 1×...128×`C_u`, total array capacitance ≈ 256×50 fF ≈ 13 pF.

**The switch:** each bit needs a 3-position switch selecting `V_IN` / `V_REF`
/ `GND` for its bottom plate. Max's `unit_switch` (3 NMOS pass transistors,
gated by `SAMPLE`/`B_n`/`B_n_bar`) does exactly this — see
`designs/libs/core_cap_dac/unit_switch.sch`. This is also the "S/H" the
schematic-review feedback referred to: there's no separate dedicated
sample-and-hold block in this architecture, the DAC's own sampling switches
*are* the S/H.

---

## ENOB (Effective Number of Bits)

**What it means:** the *real-world* resolution the ADC actually achieves once
you account for noise, distortion, and comparator offset — as opposed to the
8 bits "on paper." ENOB is almost always lower than the nominal resolution.

**Formula (from a measured SNDR — signal-to-noise-and-distortion ratio, in dB):**
```
ENOB = (SNDR_dB − 1.76) / 6.02
```

**Example:** if our converter measures SNDR = 44 dB:
```
ENOB = (44 − 1.76) / 6.02 ≈ 7.0 bits
```
So even though we built an "8-bit" ADC, it only *effectively* resolves ~7 bits —
the missing bit is eaten by comparator offset, DAC mismatch, and switch noise.

**Why it matters:** this is the number a reviewer actually cares about. "8-bit
resolution" is just the design target; ENOB is the report card.

---

## Conversion rate (sample rate / throughput)

**What it means:** how many complete analog-to-digital conversions the chip can
do per second, usually written in samples/second (S/s, kS/s, MS/s).

**Our chip:** a SAR ADC needs **N+1 clock cycles** per conversion (one cycle to
sample, then one comparator decision per bit). For our 8-bit design that's
**9 cycles/conversion**. If our SAR clock runs at, say, 10 MHz:
```
Conversion rate = 10 MHz / 9 cycles ≈ 1.1 MS/s
```

**Why it matters:** this is one of the "basic specs" the reviewer flagged as
missing from our proposal — conversion rate isn't just a nice-to-have number,
it also sets how fast the comparator must regenerate (Gate 1: delay < 2 ns) and
how much settling time the DAC gets (Gate 2: 0.5 LSB within 40 ns).

---

## S/H (Sample-and-Hold) simulation

**What it means:** the S/H is the front-end circuit that grabs a snapshot of
`V_IN` and holds it steady while the SAR loop does its 9-cycle binary search.
In a charge-redistribution SAR, the S/H **is** the DAC capacitor array plus
whatever switch drives charge onto it — there's no separate dedicated S/H
block downstream of a bootstrap switch.

**⚠️ Open design question, not yet reconciled:** the team currently has two
different ideas for how sampling happens, and they're mutually exclusive:
- **Max's `unit_switch`** (per-bit, in the DAC array) ties each bit's *bottom*
  plate directly to `V_IN` during the sample phase — no separate switch needed
  upstream at all (this is the scheme `cap_array.sch` below is built around).
- **Emily's bootstrap switch** (`designs/emily_testing/`) is a single
  dedicated switch meant to sample `V_IN` onto a *shared top plate* before
  conversion — a different, "top-plate sampling" architecture.
Only one of these should end up in the real chip — using both would either be
redundant or actively wrong (double-sampling the input through two different
paths). Worth a quick team conversation to pick one before more time goes
into either.

**What "worst case" means for this simulation:** the switch's on-resistance and
the DAC's total capacitance form an RC low-pass filter. The reviewer's note was
that our S/H testbench needs to load that RC with:
- the **worst-case DAC configuration** (the switch state where total resistance
  or capacitance is largest — usually the all-caps-connected code), **and**
- the **comparator's input capacitance** on top of the DAC caps (since the
  comparator is the next thing the switch has to drive).

**Why it matters:** simulating S/H with a light/ideal load gives an
overly-optimistic settling time. The real circuit has to charge the DAC caps
*and* the comparator's parasitic input cap through the switch's resistance —
that's the number that actually limits our achievable conversion rate.

---

## kT/C noise

**What it means:** every time a switch samples a capacitor, it also samples the
thermal (Johnson) noise of the switch's own resistance onto that capacitor.
This noise doesn't depend on the switch's resistance value — only on
capacitance and temperature — which is why it's called "kT/C noise" (k =
Boltzmann's constant, T = temperature, C = sampling capacitance).

**Formula (RMS noise voltage on the cap):**
```
V_noise,rms = sqrt(kT / C)
```

**Example:** at room temperature (T = 300 K, kT ≈ 4.14×10⁻²¹ J), a 500 fF
sampling cap gives:
```
V_noise,rms = sqrt(4.14e-21 / 500e-15) ≈ 91 µV rms
```
Compare that to our 1 LSB ≈ 6.45 mV — 91 µV is comfortably below 1 LSB, so a
500 fF unit cap wouldn't be noise-limited for an 8-bit design. If we shrank the
unit cap to make the array smaller, kT/C noise is the thing that eventually
puts a floor on how small we're allowed to go.

**Why it matters:** the reviewer's note ("DAC capacitor sizing based on kT/C is
not shown") was asking us to work this formula backward: pick a target noise
budget (some fraction of 1 LSB), then solve for the *minimum* C_u the array can
use. **Update:** the proposal (`agent_context/external/8-bit SAR ADC Proposal
(2).pdf`) does state this reasoning explicitly — `C_u ≥ 50 fF` was chosen to
put the kT/C noise floor "at least 6 dB below the 8-bit quantization noise
floor." The reviewer's ask was for that derivation to be *shown* (the actual
sqrt(kT/C) math above), not just the resulting number — worth adding the
worked calculation to the repo somewhere citable (this file, or
`VERIFICATION_PLAN.md` if the team creates one).

---

## Quick reference table

| Term | One-line meaning | Our chip's number (target) |
|------|-------------------|------------------------------|
| Resolution | # of bits → # of output codes (2^N) | 8-bit → 256 codes |
| LSB | Voltage size of one code step | ≈ 6.45 mV (at V_REF = 1.65 V) |
| DAC / CDAC | Binary-weighted cap array doing S/H + D/A together | 256×C_u ≈ 13 pF, C_u ≥ 50 fF |
| DNL / INL | Per-step / cumulative linearity error | < 0.5 LSB (Gate 3) |
| ENOB | Real-world resolution after noise/distortion | Target ≥ 7.5 bits (Gate 3) |
| Conversion rate | Conversions per second | ≥ 1 MS/s (stretch 10 MS/s), 9 cycles/conversion |
| S/H simulation | Sampling stage settling accuracy | Must load worst-case DAC + comparator C_in |
| kT/C noise | Thermal noise floor from sampling cap | Must be << 1 LSB |
