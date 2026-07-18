#!/usr/bin/env python3
"""Capacitor-mismatch Monte Carlo INL/DNL analysis for the 8-bit cap DAC.

Extends the analytical charge-redistribution transfer function verified
against dac/sim/tb_inl_dnl.sch's nominal 256-code sweep (see
designs/scripts/extract_dnl_inl.py and dac/WORKLOG.md, 2026-07-17 "Step 1"
entry: measured FS span 1.6465V vs this model's closed form ~1.6474V, and
the 0.499 = VREF/... gain-mismatch flag) with per-unit-cap random mismatch,
instead of re-running ngspice per Monte Carlo trial (which would take
N_runs x 64us transients -- far too slow for N>=1000).

Transfer function (top-plate sampling via TG, VIN sampled onto DAC_TOP with
bottom plates grounded; convert phase switches each bit's bottom plate to
VREF or GND; DAC-only sweep uses a fixed VIN=0 input, matching
tb_inl_dnl.sch exactly):

    V(code) = VREF * C_code(code) / (C_total + C_p)

  where C_code(code) = sum of C_i over bits set in `code`, C_total = sum of
  all 8 C_i, and C_p = 20fF fixed comparator-input placeholder load (same
  value as every DAC testbench in this series).

Mismatch model: each binary-weighted cap C_i is built from N_i = 2^i
parallel 50fF unit cells (i = 0..7, N_i = 1,2,4,8,...,128). Each unit cell's
capacitance is an independent Gaussian draw with relative sigma
`sigma_unit` (see SIGMA_UNIT_RELATIVE below + dac/WORKLOG.md for the PDK
source and its caveats). Summing N_i iid unit cells gives
C_i ~ Normal(N_i*Cu, N_i*(sigma_unit*Cu)^2), i.e.
sigma(C_i)/C_i(ideal) = sigma_unit / sqrt(N_i) -- the standard 1/sqrt(N)
averaging-down of parallel unit-cell arrays.

Usage: python3 dac_mismatch_mc.py [N_RUNS]
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- PDK-sourced mismatch figure -------------------------------------------
# Source: gf180mcuD ngspice deck, libs.tech/ngspice/sm141064.ngspice,
# ".LIB mimcap_statistical" (~line 47750):
#   mc_c_cox_2p0fF2 = agauss(0, 0.025, 3)
#   mc_c_cox_2p0fF  = mc_c_cox_2p0fF2 * sw_stat_global * cap_mc_skew
# This is the relative-sigma Monte Carlo term multiplying c_cox (and hence
# capacitance) for the cap_mim_2f0_* family -- the 2fF/um^2 MIM option that
# backs this design's cap_mim_2f0fF unit cell (50fF = 2fF/um^2 * 5um*5um).
# sigma = 0.025 (2.5%, 1-sigma; agauss's 3rd arg is a 3-sigma clip on the
# draw, it does not change sigma itself).
#
# CAVEAT (load-bearing, see dac/WORKLOG.md): this PDK parameter is wired
# only to `sw_stat_global` -- grepping every reference to `sw_stat_mismatch`
# in sm141064.ngspice shows it gating MOSFET (delvto/mulu0) and resistor
# (mis_r) mismatch terms, but it never appears in any cap_mim_* subckt.
# gf180mcuD's ngspice deck therefore ships a GLOBAL (die-to-die / lot-to-lot)
# process-corner-style MC parameter for MIM cap oxide capacitance, not a
# local (intra-die) mismatch model -- as literally written, one draw of
# mc_c_cox_2p0fF applies identically to every cap_mim instance in a single
# simulation run, so it cannot by itself produce cap-to-cap mismatch on one
# die. No local-mismatch (Pelgrom A_C) coefficient for cap_mim is present
# anywhere else in the PDK tree (checked docs/READMEs and both ngspice model
# files; none exist in this ciel-packaged PDK release).
#
# Since no local-mismatch number is available from the PDK, this analysis
# uses the 2.5% global-variation sigma as a deliberately conservative proxy
# for the per-unit-cap local sigma(C)/C required by the task. Real intra-die
# mismatch is normally several times smaller than global/lot corner spread,
# so treating 2.5% as the *local* unit-cap sigma should overstate (not
# understate) the DAC's mismatch-driven INL/DNL -- a worst-case bound, not a
# central estimate.
SIGMA_UNIT_RELATIVE = 0.025

# --- Design constants (must match dac/sim/tb_inl_dnl.sch) ------------------
N_BITS = 8
N_CODES = 1 << N_BITS
WEIGHTS = np.array([1 << i for i in range(N_BITS)])  # 1,2,4,...,128 unit cells
CU = 50e-15  # unit cap, 5um x 5um cap_mim_2f0fF
CP = 20e-15  # comparator-input placeholder load
VREF = 1.65

DNL_SPEC = 0.5
INL_SPEC = 0.5

REPO_ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = REPO_ROOT / "dac" / "docs" / "figures"

# code -> bit-set matrix (N_CODES x N_BITS), used to sum C_i for each code
_CODES = np.arange(N_CODES)
BIT_SET = ((_CODES[:, None] >> np.arange(N_BITS)[None, :]) & 1).astype(np.float64)


def run_mc(n_runs, seed=0):
    rng = np.random.default_rng(seed)

    # sigma(C_i)/C_i(ideal) = SIGMA_UNIT_RELATIVE / sqrt(N_i)
    ideal_ci = WEIGHTS * CU  # (N_BITS,)
    sigma_ci = SIGMA_UNIT_RELATIVE / np.sqrt(WEIGHTS) * ideal_ci  # (N_BITS,)

    # (n_runs, N_BITS) mismatched cap values
    ci = ideal_ci[None, :] + rng.standard_normal((n_runs, N_BITS)) * sigma_ci[None, :]

    c_total = ci.sum(axis=1)  # (n_runs,)
    c_code = ci @ BIT_SET.T  # (n_runs, N_CODES)
    v_code = VREF * c_code / (c_total + CP)[:, None]  # (n_runs, N_CODES)

    return analyze(v_code)


def analyze(v_code):
    """v_code: (n_runs, N_CODES) -> per-run DNL/INL summary."""
    n_runs = v_code.shape[0]
    v_lsb = (v_code[:, -1] - v_code[:, 0]) / (N_CODES - 1)  # (n_runs,)

    steps = np.diff(v_code, axis=1)  # (n_runs, N_CODES-1)
    dnl = steps / v_lsb[:, None] - 1.0  # (n_runs, N_CODES-1), dnl[:,k] is code k+1
    max_dnl_idx = np.argmax(np.abs(dnl), axis=1)  # index into 0..N_CODES-2
    max_dnl = np.take_along_axis(dnl, max_dnl_idx[:, None], axis=1)[:, 0]
    max_dnl_code = max_dnl_idx + 1

    codes = np.arange(N_CODES)
    v_line = v_code[:, 0:1] + codes[None, :] * (v_code[:, -1:] - v_code[:, 0:1]) / (N_CODES - 1)
    inl = (v_code - v_line) / v_lsb[:, None]  # (n_runs, N_CODES)
    max_inl_idx = np.argmax(np.abs(inl), axis=1)
    max_inl = np.take_along_axis(inl, max_inl_idx[:, None], axis=1)[:, 0]

    return {
        "v_code": v_code,
        "dnl": dnl,
        "inl": inl,
        "max_dnl": max_dnl,
        "max_dnl_code": max_dnl_code,
        "max_inl": max_inl,
        "max_inl_code": max_inl_idx,
    }


def summarize(result):
    max_dnl_abs = np.abs(result["max_dnl"])
    max_inl_abs = np.abs(result["max_inl"])
    pass_mask = (max_dnl_abs < DNL_SPEC) & (max_inl_abs < INL_SPEC)
    yield_frac = float(np.mean(pass_mask))

    codes, counts = np.unique(result["max_inl_code"], return_counts=True)
    worst_code_inl = int(codes[np.argmax(counts)])
    codes_d, counts_d = np.unique(result["max_dnl_code"], return_counts=True)
    worst_code_dnl = int(codes_d[np.argmax(counts_d)])

    return {
        "n_runs": len(max_dnl_abs),
        "dnl_mean": float(np.mean(max_dnl_abs)),
        "dnl_sigma": float(np.std(max_dnl_abs)),
        "dnl_worst": float(np.max(max_dnl_abs)),
        "inl_mean": float(np.mean(max_inl_abs)),
        "inl_sigma": float(np.std(max_inl_abs)),
        "inl_worst": float(np.max(max_inl_abs)),
        "worst_code_dnl": worst_code_dnl,
        "worst_code_dnl_frac": float(counts_d.max() / len(max_dnl_abs)),
        "worst_code_inl": worst_code_inl,
        "worst_code_inl_frac": float(counts.max() / len(max_inl_abs)),
        "yield": yield_frac,
    }


def plot_results(result, summary):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    codes = np.arange(N_CODES)
    n_plot = min(300, result["dnl"].shape[0])  # cap traces drawn for readability

    # --- INL/DNL spread plot (overlay of sampled runs + 5-95% envelope) ---
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    ax = axes[0]
    for k in range(n_plot):
        ax.plot(codes[1:], result["dnl"][k], color="C0", alpha=0.05, lw=0.6)
    dnl_lo = np.percentile(result["dnl"], 2.5, axis=0)
    dnl_hi = np.percentile(result["dnl"], 97.5, axis=0)
    ax.fill_between(codes[1:], dnl_lo, dnl_hi, color="C0", alpha=0.3, label="95% envelope")
    ax.axhline(DNL_SPEC, color="r", ls="--", lw=0.9, label="+/-0.5 LSB spec")
    ax.axhline(-DNL_SPEC, color="r", ls="--", lw=0.9)
    ax.set_ylabel("DNL [LSB]")
    ax.set_title(f"Cap-mismatch Monte Carlo DNL/INL spread (N={summary['n_runs']} runs, "
                 f"sigma_unit={SIGMA_UNIT_RELATIVE*100:.1f}%)")
    ax.legend(loc="upper right")

    ax = axes[1]
    for k in range(n_plot):
        ax.plot(codes, result["inl"][k], color="C1", alpha=0.05, lw=0.6)
    inl_lo = np.percentile(result["inl"], 2.5, axis=0)
    inl_hi = np.percentile(result["inl"], 97.5, axis=0)
    ax.fill_between(codes, inl_lo, inl_hi, color="C1", alpha=0.3, label="95% envelope")
    ax.axhline(INL_SPEC, color="r", ls="--", lw=0.9, label="+/-0.5 LSB spec")
    ax.axhline(-INL_SPEC, color="r", ls="--", lw=0.9)
    ax.set_xlabel("code")
    ax.set_ylabel("INL [LSB]")
    ax.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "mc_dnl_inl_spread.png", dpi=150)
    plt.close(fig)

    # --- histogram of max|INL| across runs ---
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(np.abs(result["max_inl"]), bins=60, color="C1", alpha=0.85)
    ax.axvline(INL_SPEC, color="r", ls="--", lw=1.2, label="0.5 LSB spec")
    ax.axvline(summary["inl_mean"], color="k", ls="-", lw=1.0, label=f"mean={summary['inl_mean']:.3f}")
    ax.set_xlabel("max |INL| per run [LSB]")
    ax.set_ylabel("count")
    ax.set_title(f"Distribution of worst-case |INL| across {summary['n_runs']} MC runs "
                 f"(yield={summary['yield']*100:.1f}%)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "mc_max_inl_histogram.png", dpi=150)
    plt.close(fig)


def main():
    n_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    result = run_mc(n_runs)
    summary = summarize(result)

    print(f"sigma_unit (relative, per 50fF unit cap): {SIGMA_UNIT_RELATIVE*100:.2f}%")
    print(f"N_runs: {summary['n_runs']}")
    print()
    print(f"max|DNL|: mean={summary['dnl_mean']:.4f} LSB, sigma={summary['dnl_sigma']:.4f} LSB, "
          f"worst-case={summary['dnl_worst']:.4f} LSB")
    print(f"max|INL|: mean={summary['inl_mean']:.4f} LSB, sigma={summary['inl_sigma']:.4f} LSB, "
          f"worst-case={summary['inl_worst']:.4f} LSB")
    print()
    print(f"most common worst-DNL code: {summary['worst_code_dnl']} "
          f"(0x{summary['worst_code_dnl']:02X}), {summary['worst_code_dnl_frac']*100:.1f}% of runs")
    print(f"most common worst-INL code: {summary['worst_code_inl']} "
          f"(0x{summary['worst_code_inl']:02X}), {summary['worst_code_inl_frac']*100:.1f}% of runs")
    print()
    print(f"YIELD (max|DNL|<{DNL_SPEC} AND max|INL|<{INL_SPEC}): {summary['yield']*100:.2f}%")

    plot_results(result, summary)
    print(f"\nfigures written to {FIG_DIR}/mc_dnl_inl_spread.png, {FIG_DIR}/mc_max_inl_histogram.png")


if __name__ == "__main__":
    main()
