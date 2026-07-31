#!/usr/bin/env python3
"""INT-6 / Gate 3 -- parse the 256-code sweep chunk logs and judge the result.

Reads .meas outputs (eoc_k, b0_k..b7_k) from chunk_*.log produced by the
decks from gen_adc_sweep_tt.py. For each code k the ADC converted
VIN_k = (k+0.5)*V_LSB_meas (code center of the measured transfer), so a
perfectly linear ADC returns code == k. The code-center test bounds every
transition level to (k, k+1) => |INL| < 0.5 LSB and |DNL| < 1 LSB for
every code that reads back exactly.

Reports: per-code errors, first/last exact code (valid input window),
monotonicity, missing codes, and the max |code error| inside the valid
window.

Usage: python3 check_adc_sweep.py <sweep_dir> [--csv out.csv]
"""
import glob, os, re, sys

def parse(sweep_dir):
    vals = {}
    for log in glob.glob(os.path.join(sweep_dir, "chunk_*.log")):
        for line in open(log, errors="replace"):
            m = re.match(r"\s*(eoc|b\d)_(\d+)\s*=\s*([-\d.eE+]+)", line)
            if m:
                sig, k, v = m.group(1), int(m.group(2)), float(m.group(3))
                vals.setdefault(k, {})[sig] = v
    return vals

def main():
    sweep_dir = sys.argv[1] if len(sys.argv) > 1 else "adc_top/sim/sweep_tt"
    vals = parse(sweep_dir)
    if not vals:
        sys.exit(f"no .meas results found in {sweep_dir}/chunk_*.log")
    codes, eoc_bad, missing = {}, [], []
    for k in range(256):
        if k not in vals or "b7" not in vals[k]:
            missing.append(k)
            continue
        v = vals[k]
        codes[k] = sum((1 if v[f"b{b}"] > 1.65 else 0) << b for b in range(8))
        if v.get("eoc", 0) < 1.65:
            eoc_bad.append(k)
    if missing:
        print(f"WARNING: no data for codes: {missing}")
    if eoc_bad:
        print(f"WARNING: EOC low at sample time for codes: {eoc_bad}")

    errs = {k: codes[k] - k for k in codes}
    exact = [k for k, e in errs.items() if e == 0]
    ks = sorted(codes)
    seq = [codes[k] for k in ks]
    nonmono = [(ks[i], seq[i], seq[i+1]) for i in range(len(seq)-1) if seq[i+1] < seq[i]]
    got = set(seq)
    missing_codes = [c for c in range(256) if c not in got]

    print(f"conversions parsed: {len(codes)}/256")
    print(f"exact codes: {len(exact)}  (code == k at the code center)")
    if exact:
        lo, hi = min(exact), max(exact)
        print(f"first/last exact: {lo} / {hi}")
        # largest contiguous exact run
        run, best, s = [], (0, 0), None
        for k in range(256):
            if k in codes and errs[k] == 0:
                if s is None: s = k
            else:
                if s is not None and k - s > best[1] - best[0]:
                    best = (s, k - 1)
                s = None
        if s is not None and 256 - s > best[1] - best[0]:
            best = (s, 255)
        vlsb = 3.293 / 256
        print(f"largest contiguous exact window: codes {best[0]}..{best[1]} "
              f"(VIN {best[0]*vlsb:.3f}..{(best[1]+1)*vlsb:.3f} V)")
        inw = {k: e for k, e in errs.items() if best[0] <= k <= best[1]}
        print(f"max |error| inside window: {max(abs(e) for e in inw.values())} LSB")
        outw = {k: e for k, e in errs.items() if e != 0}
        if outw:
            print("nonzero errors (code_in: err_LSB):")
            items = sorted(outw.items())
            print("  " + ", ".join(f"{k}:{e:+d}" for k, e in items))
    print(f"non-monotonic steps (input k -> codes): {nonmono if nonmono else 'none'}")
    print(f"output codes never produced: {missing_codes if missing_codes else 'none'}")
    if len(sys.argv) > 3 and sys.argv[2] == "--csv":
        with open(sys.argv[3], "w") as f:
            f.write("k,vin,code,err\n")
            for k in ks:
                f.write(f"{k},{(k+0.5)*3.293/256:.6f},{codes[k]},{errs[k]}\n")
        print(f"csv written: {sys.argv[3]}")

if __name__ == "__main__":
    main()
