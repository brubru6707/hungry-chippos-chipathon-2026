#!/usr/bin/env python3
"""ADC-level supply/temperature sweeps (the INT-7 low-risk follow-up).

Same per-code constant-VIN methodology and trusted sim settings as
gen_adc_sweep_tt.py (0.05n max step + reltol=1e-4, .save limited), with
two extra axes at TT models:
  --vdd   supply (V). The DAC reference IS VDD, so the transfer is
          ratiometric: code centers use V_LSB = vdd*(3.293/3.3)/256
          (3.293 = measured FS at 3.3 V, DAC-9). CLK/RST_N swings scale.
  --temp  die temperature (C), via .temp.

A reduced 19-code subset (default) spans the full range incl. the
low-Vcm dead-zone boundary (codes ~39-48 at TT) and both extremes --
enough to confirm monotonic behavior, the offset band and the range
limits per condition without 256 runs x 4 conditions.

Generate:  python3 gen_adc_sweep_vt.py <outdir> --vdd 3.0 --temp 27
Run:       cd <outdir> && ls code_*.spice | xargs -P 8 -I{} sh -c \
             'ngspice -b {} > {}.log 2>&1'
Check:     python3 gen_adc_sweep_vt.py <outdir> --vdd 3.0 --check
"""
import argparse
import glob
import os
import re
import sys

FS_RATIO = 3.293 / 3.3
TSAMPLE = 950e-9
DEFAULT_CODES = [2, 8, 16, 32, 40, 44, 48, 64, 80, 96, 112, 128,
                 144, 160, 176, 192, 208, 224, 240, 248, 255]

DECK = """* supply/temp sweep: code {k} (TT, VDD={vdd} V, {temp} C, 10 MHz)
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice mimcap_typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice cap_mim
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/smbb000149.ngspice typical

.include ../adc_top_subckt.spice

.temp {temp}
VVDD VDD 0 {vdd}
VCLK CLK 0 PULSE(0 {vdd} 0 1n 1n 49n 100n)
VRST RST_N 0 PULSE({vdd} 0 0 1n 1n 120n 1200n)
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


def gen(outdir, vdd, temp, codes):
    vlsb = vdd * FS_RATIO / 256.0
    os.makedirs(outdir, exist_ok=True)
    for k in codes:
        bitmeas = "\n".join(
            ".meas tran b%d_%d FIND V(BIT_%d) AT=%.0fn"
            % (b, k, b, TSAMPLE * 1e9) for b in range(8))
        deck = DECK.format(k=k, vin=(k + 0.5) * vlsb, ts=TSAMPLE * 1e9,
                           bitmeas=bitmeas, vdd=vdd, temp=temp)
        with open(os.path.join(outdir, "code_%03d.spice" % k), "w") as f:
            f.write(deck)
    print("wrote %d decks to %s (VDD=%g, %gC)" % (len(codes), outdir, vdd, temp))


def check(outdir, vdd):
    thr = vdd / 2.0
    vals = {}
    for log in glob.glob(os.path.join(outdir, "code_*.spice.log")):
        for line in open(log, errors="replace"):
            m = re.match(r"\s*(eoc|b\d)_(\d+)\s*=\s*([-\d.eE+]+)", line)
            if m:
                vals.setdefault(int(m.group(2)), {})[m.group(1)] = float(m.group(3))
    rows, bad = [], []
    for k in sorted(vals):
        v = vals[k]
        if "b7" not in v or v.get("eoc", 0) < thr:
            bad.append((k, "no result / EOC low"))
            continue
        code = sum((1 if v["b%d" % b] > thr else 0) << b for b in range(8))
        rows.append((k, code, code - k))
    print("k, code, err")
    prev = None
    mono = True
    for k, code, err in rows:
        print("%4d %4d %+d" % (k, code, err))
        if prev is not None and code < prev:
            mono = False
        prev = code
    if bad:
        print("BAD:", bad)
    errs = [e for k, c, e in rows if c != 0]
    print("monotonic:", mono, "| nonzero-code err range:",
          (min(errs), max(errs)) if errs else None)
    return 0 if mono and not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--vdd", type=float, default=3.3)
    ap.add_argument("--temp", type=float, default=27.0)
    ap.add_argument("--codes", default=None,
                    help="comma-separated code list (default reduced 21)")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        sys.exit(check(args.outdir, args.vdd))
    codes = ([int(c) for c in args.codes.split(",")] if args.codes
             else DEFAULT_CODES)
    gen(args.outdir, args.vdd, args.temp, codes)


if __name__ == "__main__":
    main()
