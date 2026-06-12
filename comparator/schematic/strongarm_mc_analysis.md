# StrongArm Comparator Monte Carlo Analysis
​
This document outlines the debugging sequence, resolution, and final statistical analysis of a 50-run Monte Carlo simulation for a StrongArm comparator implemented in the GF180MCU PDK.
​
## 1. Executive Summary
​
The initial objective was to characterize the input-referred offset of a StrongArm comparator across 50 Monte Carlo runs. The simulation script encountered a series of environment, stimulus, and statistical engine issues. By resolving `ngspice` plot context scoping, correcting the input stimulus ramp time, and shifting to direct instance-level mismatch injection, the simulation successfully yielded a genuine offset distribution.
​
The final extracted data shows a systematic offset ($\mu$) of approximately 16 mV and a random mismatch offset ($\sigma$) of roughly 5 mV, constrained by a 2 mV measurement resolution.
​
## 2. Debugging Sequence & Root Cause Analysis
​
The testbench required several distinct fixes to move from syntax failures to a fully randomized Monte Carlo execution.
​
### Issue 1: Plot Context and Vector Indexing
​
- **Symptom:** `Error: &idx: no such variable.`
- **Root Cause:** The `tran 10p 2u` command generates a new plot environment (e.g., `tran1`). Variables created afterward exist only in that local plot. Furthermore, using `$&idx` inside vector brackets is invalid syntax; `$&` is reserved for string/echo scalar extraction.
- **Resolution:** Moved plot state variables to `$curplatenv` and corrected the array assignment syntax to use the bare variable `offset_results[idx]`. Added a pre-initialization of `t1 = -1` and `t2 = -1` to safely handle non-triggering runs without causing namespace errors.
​
### Issue 2: Stimulus Timing Mismatch
​
- **Symptom:** Measurements returned `-999` for all runs, indicating the comparator never flipped.
- **Root Cause:** The input ramp was defined as `PWL(0 1.1 60n 1.3)`. Because the clock period is 20 ns, the entire ramp completed in the first 3 cycles, leaving the remaining 97 cycles statically latching the exact same decision.
- **Resolution:** Extended the ramp to cover the full simulation window with `PWL(0 1.1 2u 1.3)`. This allowed the decision point to dynamically sweep across the 100 clock cycles at ~2 mV resolution per cycle.
​
### Issue 3: The "Frozen Seed" Randomization Bug
​
- **Symptom:** The script successfully captured a 14 mV offset, but it repeated identically across all 50 runs.
- **Root Cause:** In `ngspice`, the `reset` command reloads the circuit but reuses the `.param` statistical draws (like `agauss`) computed at parse time. Adding `seed=random` did not resolve this because the netlist was not being re-parsed, resulting in the exact same mismatch being applied loop after loop.
- **Resolution:** Disabled the global PDK mismatch (`.param sw_stat_mismatch = 0`) and manually injected per-instance threshold voltage variance into the input differential pair (XM10 and XM8) before each transient analysis.
​
**Implemented Mismatch Injection:**
​
```spice
alter @m.x1.xm10.m0[delvto] = svt * sgauss(0)
alter @m.x1.xm8.m0[delvto]  = svt * sgauss(0)
```
​
> *Note: `sgauss(0)` guarantees a fresh Gaussian draw upon every execution, completely bypassing the `reset` limitation.*
​
## 3. Final Data & Statistical Output
​
With the injection applied, the arrays populated with a true distribution representing the differential pair's threshold mismatch.
​
### Figures of Merit
​
- **Systematic Offset ($\mu$):** ~16 mV
- **Random Offset ($\sigma$):** ~5 mV
​
### Offset Distribution Data (Sample)
​
| Run Index | Extracted Offset (mV) |
| --------- | --------------------- |
| 0         | 16.03                 |
| 1         | 14.03                 |
| 2         | 18.03                 |
| 3         | 10.03                 |
| ...       | ...                   |
| 48        | 10.03                 |
| 49        | 20.03                 |
​
## 4. Analysis of Quantization Artifacts & Next Steps
​
The extracted data points are currently clustering onto a 2 mV grid (e.g., 10, 12, 14, 16, 18 mV). This quantization is an artifact of the measurement setup rather than physical circuit behavior.
​
The current resolution limit is dictated by the voltage swept per clock cycle:
​
$$
res = \frac{V_{range} \times T_{clk}}{T_{sweep}} = \frac{0.2\text{ V} \times 20\text{ ns}}{2\text{ }\mu\text{s}} = 2\text{ mV}
$$
​
Because $\sigma \approx 5\text{ mV}$, the 2 mV grid is relatively coarse and introduces artificial broadening into the standard deviation calculation.
​
**Optimization Recommendation:**
​
To achieve higher resolution, narrow the voltage sweep window to strictly bracket the observed offsets and extend the sweep time.
​
- **Updated Stimulus:** `VVIN1 = PWL(0 1.19 6u 1.25)`
- **Updated Transient:** `tran 10p 6u`
​
This adjustment will shrink the resolution from 2 mV down to **0.2 mV**, allowing for a much cleaner separation of the true physical systematic offset from measurement artifacts.