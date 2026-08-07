#!/usr/bin/env python3
"""DNL/INL extractor for the 8-bit cap-DAC 256-code transfer sweep.

Reads the ngspice wrdata transient CSV produced by dac/sim/tb_inl_dnl.sch
(one long stepped transient, 256 codes x 250ns/code: 100ns SAMPLE=1 sample
phase with a fixed VIN=0 input, 150ns SAMPLE=0 convert phase driving
B0-B7 to the code) and computes the standard static-linearity figures:
full-scale span, DNL, INL (endpoint-line and best-fit-line), monotonicity,
and missing-code checks.

Usage: python3 extract_dnl_inl.py [path/to/tb_inl_dnl_tran.csv]
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Must match dac/sim/tb_inl_dnl.sch's stimulus generator
# (scratchpad gen_tb_inl_dnl.py at the time this was written).
N_CODES = 256
PERIOD = 250e-9
SAMPLE_OFFSET = 245e-9  # sample point within each period: 5ns before it ends
INTENDED_FS_V = 3.3

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = REPO_ROOT / "dac" / "sim" / "tb_inl_dnl_tran.csv"
FIG_DIR = REPO_ROOT / "dac" / "docs" / "figures"


def load_transient(csv_path):
    data = np.loadtxt(csv_path)
    return data[:, 0], data[:, 1]


def sample_codes(t, v):
    codes = np.arange(N_CODES)
    sample_times = codes * PERIOD + SAMPLE_OFFSET
    v_code = np.interp(sample_times, t, v)
    return v_code


def analyze(v_code):
    codes = np.arange(N_CODES)

    fs_measured = v_code[-1] - v_code[0]
    v_lsb = fs_measured / (N_CODES - 1)

    steps = np.diff(v_code)
    dnl = steps / v_lsb - 1.0
    dnl_full = np.concatenate(([0.0], dnl))  # dnl[0] undefined, report as 0
    max_dnl_idx = 1 + int(np.argmax(np.abs(dnl)))
    max_dnl = dnl[max_dnl_idx - 1]

    monotonic = bool(np.all(steps > 0))
    no_missing_codes = bool(np.all(dnl > -1.0))

    # Endpoint line: through code 0 and code 255
    v_line_endpoint = v_code[0] + codes * (v_code[-1] - v_code[0]) / (N_CODES - 1)
    inl_endpoint = (v_code - v_line_endpoint) / v_lsb
    max_inl_ep_idx = int(np.argmax(np.abs(inl_endpoint)))
    max_inl_ep = inl_endpoint[max_inl_ep_idx]

    # Best-fit (least-squares) line
    slope, intercept = np.polyfit(codes, v_code, 1)
    v_line_fit = slope * codes + intercept
    inl_fit = (v_code - v_line_fit) / v_lsb
    max_inl_fit_idx = int(np.argmax(np.abs(inl_fit)))
    max_inl_fit = inl_fit[max_inl_fit_idx]

    return {
        "fs_measured": fs_measured,
        "v_lsb": v_lsb,
        "dnl": dnl_full,
        "max_dnl": max_dnl,
        "max_dnl_code": max_dnl_idx,
        "monotonic": monotonic,
        "no_missing_codes": no_missing_codes,
        "inl_endpoint": inl_endpoint,
        "max_inl_endpoint": max_inl_ep,
        "max_inl_endpoint_code": max_inl_ep_idx,
        "inl_fit": inl_fit,
        "max_inl_fit": max_inl_fit,
        "max_inl_fit_code": max_inl_fit_idx,
    }


def plot_results(v_code, result):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    codes = np.arange(N_CODES)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(codes, result["dnl"], lw=0.9)
    ax.axhline(0.5, color="r", ls="--", lw=0.8, label="+/-0.5 LSB spec")
    ax.axhline(-0.5, color="r", ls="--", lw=0.8)
    ax.set_xlabel("code")
    ax.set_ylabel("DNL [LSB]")
    ax.set_title("Nominal DNL vs code (256-code sweep)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "dnl_vs_code.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(codes, result["inl_endpoint"], lw=0.9, label="endpoint-line INL")
    ax.plot(codes, result["inl_fit"], lw=0.9, label="best-fit-line INL")
    ax.axhline(0.5, color="r", ls="--", lw=0.8, label="+/-0.5 LSB spec")
    ax.axhline(-0.5, color="r", ls="--", lw=0.8)
    ax.set_xlabel("code")
    ax.set_ylabel("INL [LSB]")
    ax.set_title("Nominal INL vs code (256-code sweep)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "inl_vs_code.png", dpi=150)
    plt.close(fig)


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    t, v = load_transient(csv_path)
    v_code = sample_codes(t, v)
    result = analyze(v_code)

    print(f"measured FS span (V[255]-V[0]): {result['fs_measured']*1e3:.4f} mV")
    print(f"intended FS: {INTENDED_FS_V} V -- "
          f"ratio measured/intended = {result['fs_measured']/INTENDED_FS_V:.5f}")
    if result["fs_measured"] < 0.5 * INTENDED_FS_V:
        print("FLAG: measured full-scale span is far below the 3.3V FS spec -- "
              "the bottom-plate reference is VREF=1.65V, not the 3.3V rail, so "
              "the DAC's native output span is ~VREF, not FS. Gain/reference "
              "mismatch, not a linearity defect.")
    print(f"V_LSB (endpoint-derived): {result['v_lsb']*1e3:.5f} mV")
    print(f"max |DNL| = {abs(result['max_dnl']):.5f} LSB at code {result['max_dnl_code']}")
    print(f"monotonic (all steps > 0): {result['monotonic']}")
    print(f"no missing codes (all DNL > -1): {result['no_missing_codes']}")
    print(f"max |INL| endpoint-line = {abs(result['max_inl_endpoint']):.5f} LSB "
          f"at code {result['max_inl_endpoint_code']}")
    print(f"max |INL| best-fit-line = {abs(result['max_inl_fit']):.5f} LSB "
          f"at code {result['max_inl_fit_code']}")
    print("Note: VIN is fixed (0V) during sampling in this testbench, so "
          "sample-switch charge injection shows up here as a constant offset "
          "removed by endpoint/best-fit referencing -- its input-dependent "
          "part only shows up in a full-ADC transfer test with a swept input, "
          "not in this DAC-only sweep.")

    plot_results(v_code, result)
    print(f"figures written to {FIG_DIR}/dnl_vs_code.png, {FIG_DIR}/inl_vs_code.png")


if __name__ == "__main__":
    main()
