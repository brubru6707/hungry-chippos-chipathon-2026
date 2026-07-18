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

--- LOCAL vs GLOBAL mismatch (corrected 2026-07-17, see dac/WORKLOG.md) ----

The first version of this script (commit 4f936f1) used gf180mcuD's
`mc_c_cox_2p0fF` statistical parameter (2.5% 1-sigma, from
`libs.tech/ngspice/sm141064.ngspice`'s `.LIB mimcap_statistical`) as an
independent per-unit-cap random draw. That parameter is gated only by
`sw_stat_global`, never `sw_stat_mismatch` -- i.e. it is a single draw
shared by *every* cap_mim instance in one simulation run (die-to-die /
lot-to-lot process spread), not intra-die local mismatch. Applying it
independently per unit cap fabricated an INL/DNL-driving error the model
has no PDK basis for, giving an over-pessimistic "fails at 50fF" result.

A true GLOBAL parameter is a common scale factor on every cap on the die.
In a ratiometric DAC (V(code) depends on capacitance *ratios*), a common
scale factor is almost entirely a full-scale GAIN error -- see
`run_global_gain()` below -- and does not produce DNL/INL. Only LOCAL
(intra-die, cap-to-cap) mismatch does that, because it breaks the ratios.

gf180mcuD ships no local-mismatch (Pelgrom) coefficient for cap_mim
anywhere in the PDK tree (checked all READMEs/docs and both ngspice model
files). This script now uses literature Pelgrom estimates for 180nm MiM
capacitors instead:

    sigma(C_unit)/C_unit = A_C / sqrt(Area)      (Area in um^2, A_C in %*um)

with a primary estimate A_C = 1.6 %*um and a conservative (2x worse)
sensitivity case A_C = 3.2 %*um. Because these are literature numbers, not
PDK-extracted ones, a margin factor is intentional -- see dac/WORKLOG.md.
Unit-cap area is derived from the same 2fF/um^2 density used throughout
this design (50fF unit cap = 5um x 5um = 25um^2), so sweeping the unit cap
value Cu automatically sweeps its area and therefore its sigma (larger Cu
-> larger area -> smaller relative sigma, on top of the N-unit-cell
averaging below).

Each binary-weighted cap C_i is built from N_i = 2^i parallel Cu unit
cells (i = 0..7, N_i = 1,2,4,...,128). Each unit cell's capacitance is an
independent Gaussian draw with relative sigma `sigma_unit(Cu, A_C)`.
Summing N_i iid unit cells gives
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

# --- Local (Pelgrom) mismatch model -----------------------------------------
# sigma(C_unit)/C_unit [%] = A_C [%*um] / sqrt(Area [um^2])
# A_C_PRIMARY: literature estimate for 180nm MiM local mismatch.
# A_C_CONSERVATIVE: 2x worse, sensitivity/margin case (gf180mcuD ships no
# local-mismatch number of its own -- see module docstring).
A_C_PRIMARY = 1.6       # %*um
A_C_CONSERVATIVE = 3.2  # %*um
AC_CASES = {"A_C=1.6%*um (primary)": A_C_PRIMARY,
            "A_C=3.2%*um (conservative, 2x)": A_C_CONSERVATIVE}

CAP_DENSITY = 2e-15  # F/um^2, cap_mim_2f0fF (2fF/um^2) -- matches 50fF = 5um x 5um

def unit_area_um2(cu):
    """Unit-cap area [um^2] implied by the 2fF/um^2 cap_mim_2f0fF density."""
    return cu / CAP_DENSITY


def sigma_unit_relative(cu, a_c):
    """Pelgrom local-mismatch sigma(C_unit)/C_unit [fraction] for unit cap `cu` [F]."""
    return (a_c / 100.0) / np.sqrt(unit_area_um2(cu))


# --- Global (die-to-die / lot) mismatch, for the separate gain-error check --
# Source: gf180mcuD ngspice deck, libs.tech/ngspice/sm141064.ngspice,
# ".LIB mimcap_statistical" (~line 47750):
#   mc_c_cox_2p0fF2 = agauss(0, 0.025, 3)
#   mc_c_cox_2p0fF  = mc_c_cox_2p0fF2 * sw_stat_global * cap_mc_skew
# Gated by sw_stat_global (die-to-die/lot spread), never sw_stat_mismatch
# (intra-die local mismatch, which every other device's mismatch term in
# this deck uses) -- confirmed by grep across the whole ngspice tree. As
# literally written, one draw applies identically to every cap_mim
# instance in a single run: a common scale factor, not per-cap mismatch.
SIGMA_GLOBAL_RELATIVE = 0.025

# --- Design constants (must match dac/sim/tb_inl_dnl.sch) ------------------
N_BITS = 8
N_CODES = 1 << N_BITS
WEIGHTS = np.array([1 << i for i in range(N_BITS)])  # 1,2,4,...,128 unit cells
CU_NOMINAL = 50e-15  # current schematic unit cap, 5um x 5um cap_mim_2f0fF
CU_SWEEP = [50e-15, 100e-15, 200e-15]  # fF unit cap sweep, areas 25/50/100 um^2
CP = 20e-15  # comparator-input placeholder load (fixed -- does not scale with Cu)
VREF = 1.65

DNL_SPEC = 0.5
INL_SPEC = 0.5
YIELD_SPEC = 0.99

REPO_ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = REPO_ROOT / "dac" / "docs" / "figures"

# code -> bit-set matrix (N_CODES x N_BITS), used to sum C_i for each code
_CODES = np.arange(N_CODES)
BIT_SET = ((_CODES[:, None] >> np.arange(N_BITS)[None, :]) & 1).astype(np.float64)


def analyze(v_code):
    """v_code: (n_runs, N_CODES) -> per-run DNL/INL summary."""
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


def run_mc_local(cu, a_c, n_runs, seed=0):
    """Local (Pelgrom) mismatch MC at unit cap `cu` [F], coefficient `a_c` [%*um]."""
    rng = np.random.default_rng(seed)

    sigma_unit = sigma_unit_relative(cu, a_c)
    ideal_ci = WEIGHTS * cu  # (N_BITS,)
    sigma_ci = sigma_unit / np.sqrt(WEIGHTS) * ideal_ci  # (N_BITS,)

    ci = ideal_ci[None, :] + rng.standard_normal((n_runs, N_BITS)) * sigma_ci[None, :]

    c_total = ci.sum(axis=1)  # (n_runs,)
    c_code = ci @ BIT_SET.T  # (n_runs, N_CODES)
    v_code = VREF * c_code / (c_total + CP)[:, None]  # (n_runs, N_CODES)

    return analyze(v_code)


def run_global_gain(cu, sigma_global, n_runs, seed=1):
    """Global (die-to-die) mismatch: one common scale factor per run, applied
    identically to every cap. Demonstrates gain-error-only behavior."""
    rng = np.random.default_rng(seed)

    ideal_ci = WEIGHTS * cu  # (N_BITS,)
    g = rng.standard_normal(n_runs) * sigma_global  # (n_runs,) common draw

    ci = ideal_ci[None, :] * (1.0 + g[:, None])  # every cap scaled identically

    c_total = ci.sum(axis=1)
    c_code = ci @ BIT_SET.T
    v_code = VREF * c_code / (c_total + CP)[:, None]

    result = analyze(v_code)

    # gain error = relative deviation of the measured FS span from nominal
    ideal_result = analyze(VREF * (ideal_ci[None, :] @ BIT_SET.T) / (ideal_ci.sum() + CP))
    nominal_fs = ideal_result["v_code"][0, -1] - ideal_result["v_code"][0, 0]
    fs_span = result["v_code"][:, -1] - result["v_code"][:, 0]
    gain_error = fs_span / nominal_fs - 1.0

    return result, gain_error


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


def plot_spread(result, summary, cu, a_c, suffix=""):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    codes = np.arange(N_CODES)
    n_plot = min(300, result["dnl"].shape[0])

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
    ax.set_title(f"Local (Pelgrom) cap-mismatch MC DNL/INL spread (N={summary['n_runs']}, "
                 f"Cu={cu*1e15:.0f}fF, A_C={a_c:.1f}%*um)")
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
    fig.savefig(FIG_DIR / f"mc_dnl_inl_spread{suffix}.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(np.abs(result["max_inl"]), bins=60, color="C1", alpha=0.85)
    ax.axvline(INL_SPEC, color="r", ls="--", lw=1.2, label="0.5 LSB spec")
    ax.axvline(summary["inl_mean"], color="k", ls="-", lw=1.0, label=f"mean={summary['inl_mean']:.3f}")
    ax.set_xlabel("max |INL| per run [LSB]")
    ax.set_ylabel("count")
    ax.set_title(f"Distribution of worst-case |INL|, Cu={cu*1e15:.0f}fF, A_C={a_c:.1f}%*um "
                 f"(yield={summary['yield']*100:.2f}%)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"mc_max_inl_histogram{suffix}.png", dpi=150)
    plt.close(fig)


def plot_yield_vs_cu(sweep_summaries):
    """sweep_summaries: {ac_label: [(cu, summary), ...]}"""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 5))
    colors = {list(AC_CASES.keys())[0]: "C0", list(AC_CASES.keys())[1]: "C3"}
    markers = {list(AC_CASES.keys())[0]: "o", list(AC_CASES.keys())[1]: "s"}

    for ac_label, points in sweep_summaries.items():
        cus = [p[0] * 1e15 for p in points]
        yields = [p[1]["yield"] * 100 for p in points]
        ax.plot(cus, yields, marker=markers[ac_label], color=colors[ac_label],
                 lw=2, ms=7, label=ac_label)

    ax.axhline(YIELD_SPEC * 100, color="r", ls="--", lw=1.2, label=f"{YIELD_SPEC*100:.0f}% yield target")
    ax.set_xlabel("unit cap Cu [fF]")
    ax.set_ylabel("yield (max|DNL|<0.5 LSB AND max|INL|<0.5 LSB) [%]")
    ax.set_title("Local (Pelgrom) cap-mismatch yield vs unit cap size")
    ax.set_xticks([50, 100, 200])

    # Yield saturates near 100% everywhere in this sweep (that IS the
    # finding -- Cu=50fF already clears spec by a wide margin). A [0,100]
    # linear axis would render every point as an indistinguishable flat
    # line at the top, so zoom to the band that actually contains the data.
    all_yields = [p[1]["yield"] * 100 for pts in sweep_summaries.values() for p in pts]
    y_lo = min(all_yields + [YIELD_SPEC * 100])
    span = max(100.0 - y_lo, 0.001)
    ax.set_ylim(y_lo - 0.1 * span, 100.0 + 0.1 * span)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "mc_yield_vs_cu.png", dpi=150)
    plt.close(fig)


def main():
    n_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

    print("=" * 78)
    print("LOCAL (Pelgrom) mismatch MC -- Cu x A_C sweep")
    print("=" * 78)
    print(f"{'Cu [fF]':>8} {'A_C':>28} {'sigma_unit':>11} "
          f"{'DNL mean':>9} {'DNL worst':>10} {'INL mean':>9} {'INL worst':>10} {'YIELD':>8}")

    sweep_summaries = {label: [] for label in AC_CASES}
    min_cu_for_ac = {}

    for ac_label, a_c in AC_CASES.items():
        for cu in CU_SWEEP:
            result = run_mc_local(cu, a_c, n_runs, seed=hash((cu, a_c)) & 0xFFFFFFFF)
            summary = summarize(result)
            sweep_summaries[ac_label].append((cu, summary))
            sigma_u = sigma_unit_relative(cu, a_c) * 100
            print(f"{cu*1e15:8.0f} {ac_label:>28} {sigma_u:10.3f}% "
                  f"{summary['dnl_mean']:9.4f} {summary['dnl_worst']:10.4f} "
                  f"{summary['inl_mean']:9.4f} {summary['inl_worst']:10.4f} "
                  f"{summary['yield']*100:7.2f}%")

            if summary["yield"] >= YIELD_SPEC and ac_label not in min_cu_for_ac:
                min_cu_for_ac[ac_label] = cu

            if cu == CU_NOMINAL:
                suffix = "" if a_c == A_C_PRIMARY else "_conservative"
                plot_spread(result, summary, cu, a_c, suffix=suffix)

    print()
    for ac_label in AC_CASES:
        if ac_label in min_cu_for_ac:
            print(f"Minimum Cu meeting >={YIELD_SPEC*100:.0f}% yield ({ac_label}): "
                  f"{min_cu_for_ac[ac_label]*1e15:.0f} fF")
        else:
            print(f"No Cu in sweep {[c*1e15 for c in CU_SWEEP]} meets "
                  f">={YIELD_SPEC*100:.0f}% yield for {ac_label}")

    plot_yield_vs_cu(sweep_summaries)

    print()
    print("=" * 78)
    print("GLOBAL (die-to-die) mismatch -- gain-error-only check")
    print("=" * 78)
    global_result, gain_error = run_global_gain(CU_NOMINAL, SIGMA_GLOBAL_RELATIVE, n_runs)
    global_summary = summarize(global_result)
    print(f"sigma_global = {SIGMA_GLOBAL_RELATIVE*100:.2f}% applied as one common scale factor/run "
          f"(Cu={CU_NOMINAL*1e15:.0f}fF, N={n_runs})")
    print(f"Full-scale GAIN error: mean={np.mean(gain_error)*100:+.4f}%, "
          f"sigma={np.std(gain_error)*100:.4f}%, worst-case={np.max(np.abs(gain_error))*100:.4f}%")
    print(f"max|DNL| under global-only variation: mean={global_summary['dnl_mean']:.6f} LSB, "
          f"worst={global_summary['dnl_worst']:.6f} LSB")
    print(f"max|INL| under global-only variation: mean={global_summary['inl_mean']:.6f} LSB, "
          f"worst={global_summary['inl_worst']:.6f} LSB")
    print("-> confirms global variation is a gain error and does not drive DNL/INL "
          "(residual above is numerical noise from Cp not scaling with the caps, "
          f"Cp={CP*1e15:.0f}fF vs C_total~{(WEIGHTS.sum()*CU_NOMINAL)*1e15:.0f}fF).")

    print(f"\nfigures written to {FIG_DIR}/")


if __name__ == "__main__":
    main()
