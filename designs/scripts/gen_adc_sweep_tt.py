#!/usr/bin/env python3
"""INT-6/INT-7 (Gate 3/4) -- generate per-code decks for the 256-code sweep.

Optional second arg = MOS corner section (typical/ff/ss/fs/sf; default
typical). MIM caps stay at mimcap_typical for all corners: global cap
variation is a common scale factor and cancels in this ratiometric DAC
(see DAC-9b); VDD=3.3/27C here -- supply/temp axes were covered per-block
(DAC Gate 2: 30 PVT corners; COMP-5: SS/125C/2.97V delay).

One ngspice run per code, CONSTANT VIN (code center of the measured DAC
transfer, V_LSB = 3.293/256). Constant VIN avoids the PWL-step
convergence failure that killed the chunked variant at tight tolerances
("timestep too small ... trouble with node vvin#branch" at a staircase
edge, which aborts the run and loses every .meas in the chunk).
Runs are independent -> parallelize with xargs -P.

Verified-trustworthy sim settings (see PROGRESS INT-6): .tran max step
0.05n + reltol=1e-4; .save limited to the 9 measured signals (without it
ngspice tries to store every node at every point and dies allocating).

Usage:  python3 gen_adc_sweep_tt.py <outdir>
Run:    cd <outdir> && ls code_*.spice | xargs -P 10 -I{} sh -c \
          'ngspice -b {} > {}.log 2>&1'
Check:  python3 designs/scripts/check_adc_sweep.py <outdir>
"""
import os, sys

VLSB    = 3.293 / 256
TSAMPLE = 950e-9

DECK = """* Gate-3/4 per-code conversion: code {k} (corner {corner}, 3.3 V, 10 MHz)
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice {corner}
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice mimcap_typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice cap_mim
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/smbb000149.ngspice typical

.include ../adc_top_subckt.spice

VVDD VDD 0 3.3
VCLK CLK 0 PULSE(0 3.3 0 1n 1n 49n 100n)
VRST RST_N 0 PULSE(3.3 0 0 1n 1n 120n 1200n)
VVIN vin 0 {vin:.6f}

Xadc VDD 0 vin CLK RST_N BIT_7 BIT_6 BIT_5 BIT_4 BIT_3 BIT_2 BIT_1 BIT_0 EOC adc_top

CB7 BIT_7 0 20f
CB6 BIT_6 0 20f
CB5 BIT_5 0 20f
CB4 BIT_4 0 20f
CB3 BIT_3 0 20f
CB2 BIT_2 0 20f
CB1 BIT_1 0 20f
CB0 BIT_0 0 20f
CEOC EOC 0 20f

.option reltol=1e-4
.save V(EOC) V(BIT_7) V(BIT_6) V(BIT_5) V(BIT_4) V(BIT_3) V(BIT_2) V(BIT_1) V(BIT_0)
.tran 0.05n 1.0u

.meas tran eoc_{k} FIND V(EOC) AT={ts:.0f}n
{bitmeas}
.control
set num_threads=1
run
.endc
.end
"""

def main(outdir, corner="typical"):
    os.makedirs(outdir, exist_ok=True)
    for k in range(256):
        bitmeas = "\n".join(
            f".meas tran b{b}_{k} FIND V(BIT_{b}) AT={TSAMPLE*1e9:.0f}n"
            for b in range(8))
        deck = DECK.format(k=k, vin=(k + 0.5) * VLSB, ts=TSAMPLE*1e9,
                           bitmeas=bitmeas, corner=corner)
        with open(os.path.join(outdir, f"code_{k:03d}.spice"), "w") as f:
            f.write(deck)
    print(f"wrote 256 per-code decks to {outdir}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "adc_top/sim/sweep_tt",
         sys.argv[2] if len(sys.argv) > 2 else "typical")
