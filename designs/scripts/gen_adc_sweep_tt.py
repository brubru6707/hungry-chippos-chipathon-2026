#!/usr/bin/env python3
"""INT-6 / Gate 3 -- generate the 256-code TT sweep decks for adc_top.

One full conversion per code, VIN at the code centers of the MEASURED DAC
transfer (FS = 3.293 V from DAC-9, so V_LSB = 3.293/256 = 12.8633 mV --
this is the standard gain-corrected grid: Gate 3 judges linearity, the
~0.2% FS gain gap is a separate, already-understood artifact of the
20 fF comparator load on C_total).

Sweep is split into NCHUNK independent ngspice decks (conversions are
independent -- each chunk restarts from t=0 with its own VIN PWL) so they
run in parallel in the container. Codes are sampled with .meas FIND ...
AT= statements instead of wrdata to keep outputs tiny.

Timing per conversion (per docs/pin_contracts.md section 5):
  t0 = k*1.2us, CLK 10 MHz (high [0,49n] of each period),
  RST_N low [t0, t0+120n] (released in a CLK-HIGH phase),
  EOC rises at t0+901n, bits sampled at t0+950n.

Usage:  python3 gen_adc_sweep_tt.py <outdir>
Then:   run each chunk_*.spice with ngspice -b; parse with
        designs/scripts/check_adc_sweep.py
"""
import os, sys

NCODES   = 256
NCHUNK   = 8
PER      = NCODES // NCHUNK
TCONV    = 1.2e-6
VLSB     = 3.293 / 256          # measured-FS code width (DAC-9)
TSAMPLE  = 950e-9               # after t0: EOC+~50ns
TSTEP    = "0.1n"               # INT-5 finding: 0.5n corrupts near-rail decisions

HEADER = """* INT-6 Gate-3 sweep chunk {c}: codes {k0}..{k1} (TT, 3.3 V, 10 MHz)
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice mimcap_typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice cap_mim
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/smbb000149.ngspice typical

.include ../adc_top_subckt.spice

VVDD VDD 0 3.3
VCLK CLK 0 PULSE(0 3.3 0 1n 1n 49n 100n)
VRST RST_N 0 PULSE(3.3 0 0 1n 1n 120n 1200n)
{vin}

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

.tran {tstep} {tstop}
"""

def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    for c in range(NCHUNK):
        k0, k1 = c * PER, c * PER + PER - 1
        pts = []
        for i in range(PER):
            k = k0 + i
            vin = (k + 0.5) * VLSB
            t0 = i * TCONV
            if i == 0:
                pts.append(f"0 {vin:.6f}")
            else:
                pts.append(f"{t0*1e9:.0f}n {vin:.6f}")
            pts.append(f"{(t0+TCONV)*1e9-2:.0f}n {vin:.6f}")
        vinsrc = "VVIN vin 0 PWL(" + " ".join(pts) + ")"
        meas = []
        for i in range(PER):
            k = k0 + i
            t = i * TCONV + TSAMPLE
            meas.append(f".meas tran eoc_{k} FIND V(EOC) AT={t*1e9:.0f}n")
            for b in range(8):
                meas.append(f".meas tran b{b}_{k} FIND V(BIT_{b}) AT={t*1e9:.0f}n")
        deck = HEADER.format(c=c, k0=k0, k1=k1, vin=vinsrc, tstep=TSTEP,
                             tstop=f"{PER*TCONV*1e6:.1f}u")
        deck += "\n".join(meas)
        deck += "\n.control\nset num_threads=1\nrun\n.endc\n.end\n"
        with open(os.path.join(outdir, f"chunk_{c}.spice"), "w") as f:
            f.write(deck)
    print(f"wrote {NCHUNK} chunks x {PER} conversions to {outdir}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "adc_top/sim/sweep_tt")
