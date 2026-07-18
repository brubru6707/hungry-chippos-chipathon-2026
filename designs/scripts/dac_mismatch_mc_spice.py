#!/usr/bin/env python3
"""Transistor-level Monte-Carlo cross-check of the cap-mismatch DNL analysis.

Companion to dac_mismatch_mc.py (the fast, primary, idealized-transfer-
function Monte Carlo over all 256 codes). That script assumes instantaneous
charge conservation with no switch resistance, no TG charge injection, no
digital gate delay -- this script re-runs the same per-bit random cap draws
through real ngspice transient simulation on dac/sim/tb_major_carry.sch's
structure (TG top-plate switch, real gate logic, 20fF comparator load) to
confirm those second-order effects don't change the mismatch-driven DNL
conclusion. Per task instructions, only the three dominant major-carry
transitions are exercised (0x7F->0x80, 0x3F->0x40, 0xBF->0xC0) at N~50-100
runs each -- a full 256-code x 100-run ngspice sweep would be far too slow
(64us x 256 codes per run, see tb_inl_dnl.sch's 8.2s single-run wall time).

Must run inside the iic-osic-tools container (needs ngspice + the gf180mcuD
PDK), from /foss/designs, using the pre-generated flat netlist at
designs/simulations/tb_major_carry.spice (regenerate first if missing:
`xschem -q -x -n --rcfile designs/.config/.xschem/xschemrc dac/sim/tb_major_carry.sch`).

Usage (inside container, cwd=/foss/designs):
    python3 designs/scripts/dac_mismatch_mc_spice.py [N_RUNS_PER_TRANSITION]
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/foss/designs")
BASE_NETLIST = REPO_ROOT / "designs" / "simulations" / "tb_major_carry.spice"

SIGMA_UNIT_RELATIVE = 0.025  # same PDK-sourced figure as dac_mismatch_mc.py
CU = 50e-15
WEIGHTS = [1 << i for i in range(8)]  # bit i -> N_i unit cells
V_LSB_IDEAL = 6.457e-3  # from the Step-1 nominal 256-code sweep (WORKLOG, endpoint-derived)
T0 = 700e-9  # major-carry transition time, matches tb_major_carry.sch

TRANSITIONS = [
    ("0x7F->0x80 (MSB carry)", 0x7F, 0x80),
    ("0x3F->0x40", 0x3F, 0x40),
    ("0xBF->0xC0", 0xBF, 0xC0),
]

CAP_LINE_RE = re.compile(
    r"^(XC(\d)) net(\d+) DAC_TOP cap_mim_2f0fF c_width=5e-6 c_length=5e-6(?:\s+m=(\d+))?\s*$",
    re.MULTILINE,
)


def gen_b_source(bit_idx, pre_bit, post_bit):
    name = f"V_B{bit_idx}"
    net = f"B{bit_idx}"
    if pre_bit == post_bit:
        return f"{name} {net} 0 {3.3 * pre_bit}"
    if pre_bit == 0 and post_bit == 1:
        # rising at t0 (matches B7's pattern in tb_major_carry.spice)
        return f"{name} {net} 0 pulse(0 3.3 {T0*1e9:.6g}n 50p 50p 40u 80u)"
    # falling at t0 (matches B0-B6's pattern): high from 100n+50p to t0
    pulse_width_ns = (T0 - 100e-9 - 0.05e-9) * 1e9
    return f"{name} {net} 0 pulse(0 3.3 100n 50p 50p {pulse_width_ns:.6g}n 80u)"


def build_deck(base_text, pre_code, post_code, cap_scale, out_path, v_final_offset_ns):
    text = base_text

    for i in range(8):
        pre_bit = (pre_code >> i) & 1
        post_bit = (post_code >> i) & 1
        old_line_re = re.compile(rf"^V_B{i} B{i} 0 .*$", re.MULTILINE)
        text, n = old_line_re.subn(gen_b_source(i, pre_bit, post_bit), text)
        assert n == 1, f"expected 1 substitution for V_B{i}, got {n}"

    def repl(m):
        inst, bit_s, net, m_s = m.groups()
        bit = int(bit_s)
        scale = cap_scale[bit]
        # scale width & length together -> area scales ~scale^2 (dominant term)
        w = 5e-6 * scale
        l = 5e-6 * scale
        mpart = f" m={m_s}" if m_s else ""
        return f"{inst} net{net} DAC_TOP cap_mim_2f0fF c_width={w:.8e} c_length={l:.8e}{mpart}"

    text, n = CAP_LINE_RE.subn(repl, text)
    assert n == 8, f"expected 8 cap substitutions, got {n}"

    # Trim the control block to just what this cross-check needs (speed + robustness
    # vs the fragile CROSS=LAST measures already flagged elsewhere in this repo).
    # NOTE (load-bearing): the full 1.05us duration used by tb_major_carry.sch's
    # own .control block is numerically unstable in this ngspice build once run
    # past ~750-780ns -- confirmed by a duration sweep (500n-750n: clean exit 0;
    # 780n-870n: hangs/timeout; 1.05u: "memory required X more than available Y"
    # fatal error, ~7.6M accepted timepoints instead of the expected ~52,500).
    # This reproduces even on the pristine, unmodified netlist with "save
    # v(dac_top)" already applied -- not something introduced by this script's
    # substitutions. Since Gate-2's own spec point is settling by t0+40ns (and
    # the worst-case PVT corner from Brief #10 settles by ~80ns), there is no
    # need to run anywhere near the unstable region: this script only needs
    # v_pre (well before t0) and v_final at t0+40ns. Truncating to 745ns
    # reproduces WORKLOG's documented v_at40=2.02645V exactly on the nominal
    # (unperturbed) netlist, confirming the truncation is not losing signal.
    v_final_ns = T0 * 1e9 + v_final_offset_ns
    total_ns = v_final_ns + 5.0  # small margin past the sample point, stay inside the safe window
    text = re.sub(
        r"\.control.*\.endc",
        (
            ".control\n"
            "save v(dac_top)\n"
            f"tran 0.02n {total_ns:.6g}n\n"
            f"meas tran v_pre FIND v(DAC_TOP) AT={(T0-10e-9)*1e9:.6g}n\n"
            f"meas tran v_final FIND v(DAC_TOP) AT={v_final_ns:.6g}n\n"
            "echo RESULT v_pre= $&v_pre v_final= $&v_final\n"
            ".endc\n"
        ),
        text,
        flags=re.DOTALL,
    )

    out_path.write_text(text)


# Real TT/27C settling for this design is ~2-4ns after t0 (WORKLOG, Brief #10);
# 40ns is Gate-2's own spec point. The *numerical* instability onset (see
# build_deck's note) can occasionally shift earlier than 745ns total duration
# for some random cap draws -- shrink the post-t0 window on retry rather than
# fail the run, since 10ns is still >2x the real settling time and comfortably
# outside the ngspice error region observed at every duration tried.
V_FINAL_OFFSET_CANDIDATES_NS = [40.0, 25.0, 15.0, 10.0]


def run_ngspice_once(deck_path, timeout=60):
    p = subprocess.run(
        ["ngspice", "-b", str(deck_path)],
        capture_output=True, text=True, timeout=timeout,
    )
    for line in p.stdout.splitlines():
        if line.strip().startswith("RESULT"):
            m = re.search(r"v_pre=\s*([\-0-9.eE]+)\s+v_final=\s*([\-0-9.eE]+)", line)
            if m:
                return float(m.group(1)), float(m.group(2))
    return None


def run_ngspice_with_retry(base_text, pre_code, post_code, cap_scale, deck_path):
    last_err = None
    for offset_ns in V_FINAL_OFFSET_CANDIDATES_NS:
        build_deck(base_text, pre_code, post_code, cap_scale, deck_path, offset_ns)
        try:
            result = run_ngspice_once(deck_path)
        except subprocess.TimeoutExpired as e:
            last_err = e
            continue
        if result is not None:
            return result
        last_err = RuntimeError(f"no RESULT line at offset {offset_ns}ns")
    raise RuntimeError(f"all retries failed for {deck_path}: {last_err}")


def main():
    n_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    if not BASE_NETLIST.exists():
        print(f"ERROR: {BASE_NETLIST} not found -- netlist tb_major_carry.sch first "
              f"(see module docstring).", file=sys.stderr)
        sys.exit(1)
    base_text = BASE_NETLIST.read_text()

    rng = np.random.default_rng(1)
    tmpdir = Path(tempfile.mkdtemp(prefix="dac_mc_spice_"))
    print(f"scratch decks in {tmpdir}\n")

    all_results = {}
    for label, pre_code, post_code in TRANSITIONS:
        dnls = []
        for run in range(n_runs):
            sigma_i = SIGMA_UNIT_RELATIVE / np.sqrt(WEIGHTS)
            delta = rng.standard_normal(8) * sigma_i
            cap_scale = np.sqrt(1.0 + delta)  # area-scale factor per bit

            deck_path = tmpdir / f"run_{pre_code:02x}_{post_code:02x}_{run}.spice"
            v_pre, v_final = run_ngspice_with_retry(base_text, pre_code, post_code, cap_scale, deck_path)

            dnl = (v_final - v_pre) / V_LSB_IDEAL - 1.0
            dnls.append(dnl)

        dnls = np.array(dnls)
        all_results[label] = dnls
        print(f"{label}: N={n_runs}  mean|DNL|={np.mean(np.abs(dnls)):.4f} LSB  "
              f"sigma={np.std(np.abs(dnls)):.4f} LSB  worst={np.max(np.abs(dnls)):.4f} LSB")

    print(f"\n(scratch decks left in {tmpdir} for inspection; not committed)")
    return all_results


if __name__ == "__main__":
    main()
