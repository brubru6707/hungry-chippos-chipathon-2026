#!/usr/bin/env python3
"""REP-2: FFT spectrum -> SNDR / ENOB.

Two modes:

1) --codes <csv>: FFT a captured output-code series (one code per line,
   or CSV with a 'code' column) sampled coherently at --fs with input
   --fin. For future silicon / long transient captures.

2) --transfer <sweep_codes.csv> (the Gate-3/4 per-code sweep format
   k,vin,code,err): STATIC-TRANSFER-PROJECTED ENOB. Reconstructs the
   ADC's transition thresholds from the measured code-center transfer
   (code changes between adjacent centers place a threshold at their
   midpoint), applies them sample-wise to an N-point coherent sine
   spanning --vlo..--vhi, and FFTs the resulting code series.

   This is the DC/slow-signal linearity figure: it captures every
   static INL/DNL/offset/gain effect the sweep measured and explicitly
   ignores dynamic errors -- the ADC has no input S/H, so full-swing
   sine operation is only physical below ~1.5 kHz (pin_contracts
   section 2); flag both numbers in the datasheet.

SNDR convention: coherent sampling, rectangular window; signal = the
input bin; noise+distortion = every other bin in (0, N/2] except DC.
Offset shows up in DC (excluded); gain error scales the signal bin
(standard). ENOB = (SNDR_dB - 1.76) / 6.02.

Example (the datasheet run):
  python3 calc_enob.py --transfer adc_top/sim/sweep_tt_fine2/sweep_codes.csv \
      --vlo 0.65 --vhi 3.25 --n 8192 --j 127
"""
import argparse
import csv
import math
import sys

import numpy as np


def load_transfer(path):
    ks, vins, codes = [], [], []
    with open(path) as f:
        for row in csv.DictReader(f):
            ks.append(int(row["k"]))
            vins.append(float(row["vin"]))
            codes.append(int(row["code"]))
    order = np.argsort(vins)
    return np.array(vins)[order], np.array(codes)[order]


def thresholds_from_centers(vins, codes):
    """T[c] = input voltage where output first reaches >= c, inferred
    from code-center samples: when code steps between adjacent centers,
    put the threshold(s) at the midpoint. Monotonicity of the measured
    transfer (Gate 3/4 PASS) makes this well-defined."""
    T = np.full(257, np.nan)
    for i in range(1, len(vins)):
        lo, hi = codes[i - 1], codes[i]
        if hi > lo:
            mid = 0.5 * (vins[i - 1] + vins[i])
            for c in range(lo + 1, hi + 1):
                T[c] = mid
    T[0] = -np.inf
    # codes never reached keep nan -> quantizer clips below/above
    return T


def quantize(v, T):
    codes = np.zeros(len(v), dtype=int)
    valid = np.where(~np.isnan(T))[0]
    for i, x in enumerate(v):
        c = 0
        for cc in valid:
            if x >= T[cc]:
                c = cc
            else:
                break
        codes[i] = c
    return codes


def sndr_enob(code_series, j):
    x = np.asarray(code_series, dtype=float)
    n = len(x)
    spec = np.fft.rfft(x - x.mean())
    p = (np.abs(spec) ** 2)
    p[0] = 0.0
    sig = p[j]
    noise = p.sum() - sig
    sndr = 10.0 * math.log10(sig / noise)
    enob = (sndr - 1.76) / 6.02
    return sndr, enob


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codes", help="captured code series (csv/lines)")
    ap.add_argument("--transfer", help="Gate-3 sweep_codes.csv")
    ap.add_argument("--n", type=int, default=8192)
    ap.add_argument("--j", type=int, default=127,
                    help="signal bin (odd, coprime to n => coherent)")
    ap.add_argument("--vlo", type=float, default=0.65)
    ap.add_argument("--vhi", type=float, default=3.25)
    ap.add_argument("--fs", type=float, default=833.333e3,
                    help="sample rate for reporting (12 CLK @ 10 MHz)")
    args = ap.parse_args()

    if args.transfer:
        vins, codes = load_transfer(args.transfer)
        T = thresholds_from_centers(vins, codes)
        amp = 0.5 * (args.vhi - args.vlo)
        off = 0.5 * (args.vhi + args.vlo)
        t = np.arange(args.n)
        vin = off + amp * np.sin(2 * math.pi * args.j * t / args.n)
        series = quantize(vin, T)
        sndr, enob = sndr_enob(series, args.j)
        fin = args.fs * args.j / args.n
        print("static-transfer-projected ENOB (from %s)" % args.transfer)
        print("  sine %.3f..%.3f V (%.0f%% of the 3.293 V FS), N=%d, "
              "bin %d (fin=%.2f kHz @ fs=%.1f kS/s)" % (
                  args.vlo, args.vhi,
                  100 * 2 * amp / 3.293, args.n, args.j,
                  fin / 1e3, args.fs / 1e3))
        print("  SNDR = %.2f dB   ENOB = %.2f bits" % (sndr, enob))
        print("  NOTE: static figure -- no-S/H input BW limit ~1.5 kHz "
              "for full-swing sines (pin_contracts sec.2)")
    elif args.codes:
        vals = []
        with open(args.codes) as f:
            first = f.readline()
            f.seek(0)
            if "code" in first:
                vals = [int(r["code"]) for r in csv.DictReader(f)]
            else:
                vals = [int(float(l.split(",")[-1])) for l in f if l.strip()]
        sndr, enob = sndr_enob(vals, args.j)
        print("SNDR = %.2f dB   ENOB = %.2f bits (N=%d, bin %d)" % (
            sndr, enob, len(vals), args.j))
    else:
        ap.error("need --transfer or --codes")


if __name__ == "__main__":
    main()
