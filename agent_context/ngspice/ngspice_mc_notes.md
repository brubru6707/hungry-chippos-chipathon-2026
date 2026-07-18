# ngspice Monte Carlo Scripting — Notes & Lessons Learned

Context: these notes document bugs found and fixed while writing the StrongARM comparator
offset Monte Carlo sim (`comparator/schematic/strongarm_mc_tb.sch`). They are written for
future AI models or engineers who need to debug or extend `.control` block MC loops.

---

## The working MC loop pattern

```spice
.control
let mc_runs = 50
let run = 0
let offset_results = vector(mc_runs)
set curplatenv = $curplot

dowhile run < mc_runs
  echo ---- run $&run ----

  * Inject per-run mismatch directly (more reliable than relying on reset+PDK re-seed)
  alter @m.x1.xm10.m0[delvto] = svt * sgauss(0)
  alter @m.x1.xm8.m0[delvto]  = svt * sgauss(0)

  tran 10p 2u

  * Pre-init so the vector always exists; meas overwrites if measurement succeeds
  let trip_time = -1
  meas tran trip_time when v(out1)=1.5 fall=LAST

  if trip_time > 0
    meas tran v_in_at_trip find v(vin1) at=trip_time
    let offset_results[run] = v_in_at_trip - 1.200
    echo   offset = $&offset_results[run]
  else
    let offset_results[run] = -999
    echo   Warning: no flip on run $&run
  end

  let run = run + 1
end

setplot $curplatenv
write comp_mc_offsets.raw offset_results
print offset_results
.endc
```

---

## Bug 1: `$?varname` does NOT detect `meas` results

### Symptom
`meas tran t1 when ...` prints `t1 = 2.02274e-08` (measurement succeeded), but
`if $?t1` immediately after evaluates to false, so the branch is never entered.
All runs stored the sentinel `-999`.

### Root cause
`$?varname` checks the **shell variable** namespace — things set with the `set` command.
`meas tran` stores its result as a **vector in the current tran plot** (the `let`/vector
namespace). These are two separate namespaces. `$?` never sees a `meas` result.

### Fix
Pre-initialize the vector to a sentinel value with `let`, then check the value directly:

```spice
* WRONG
meas tran t1 when v(out1)=1.5 fall=LAST
if $?t1          <- always false, $? checks shell vars not vectors
  ...
end

* CORRECT
let t1 = -1      <- vector now always exists
meas tran t1 when v(out1)=1.5 fall=LAST
if t1 > 0        <- checks the vector value directly
  ...
end
```

---

## Bug 2: `$&varname` inside `[...]` causes "no such variable" error

### Symptom
```
Error: &idx: no such variable.
Error getting index.
```

### Root cause
`$&varname` is the scalar-extraction prefix for use in `echo`, `set`, and `print`
contexts. Inside vector index brackets `[...]`, ngspice does NOT expand `$&` — it tries
to look up a variable literally named `&idx`, which doesn't exist.

### Fix
Use the bare vector name as the index, no `$&`:

```spice
* WRONG
let offset_results[$&idx] = value

* CORRECT
let offset_results[idx] = value
```

The same applies to any vector used as an index — just name it directly.

---

## Bug 3: `setplot $curplatenv` immediately before `tran` breaks measurements

### Symptom
After adding `setplot $curplatenv` right before `tran 10p 2u` to set up the `idx`
variable in the right plot, all results became `-999` even though measurements were
printing valid times.

### Root cause
Not fully pinned, but: switching to the env plot immediately before `tran` disrupts the
measurement context. Likely a side-effect of plot state at the time `tran` creates its new
plot and `meas` writes into it.

### Fix
Never put `setplot $curplatenv` before `tran`. Only switch to the env plot AFTER `tran`
and all measurements are done. Compute any index or scratch variables you need for the env
plot inside the `if/else` block, right after the `setplot`:

```spice
tran 10p 2u
* ... all meas commands here, still in tran plot ...

if trip_time > 0
  meas tran v_in_at_trip find v(vin1) at=trip_time
  let current_offset = v_in_at_trip - 1.200

  setplot $curplatenv        <- switch HERE, after all measurements
  let idx = run - 1          <- compute idx now, run is in curplatenv
  let offset_results[idx] = {$current_tran}.current_offset
end
```

---

## Bug 4: PWL ramp must span the full transient duration

### Symptom
Every MC run returned the same `trip_time` and the same offset. The distribution was
completely degenerate.

### Root cause
The stimulus was `PWL(0 1.1 60n 1.3)` — a 200 mV ramp in 60 ns. With a 20 ns clock
period and a 2 µs transient, the ramp finished in the first 3 clock cycles and VIN1 sat
flat at 1.3 V for the remaining 97 cycles. `meas ... fall=LAST` then returned the same
last-cycle artifact on every run because the 100 mV static overdrive swamped any MC
mismatch (typically a few mV).

### Fix
Make the ramp span the full transient so each clock cycle is a distinct decision point:

```spice
* WRONG — ramp done in 60 ns, 97 cycles are static
VVIN1 value="PWL(0 1.1 60n 1.3)"

* CORRECT — ramp spans full 2 us, ~2 mV/cycle resolution, VIN1 crosses VIN2 at ~1 us
VVIN1 value="PWL(0 1.1 2u 1.3)"
```

Rule of thumb: ramp duration = transient duration.

---

## Plot context rules (summary)

| Event | Effect on current plot |
|---|---|
| `.control` block starts | current plot = `const` (constants plot) |
| `let x = ...` | creates vector `x` in **current plot** |
| `set name = ...` | creates shell variable (separate namespace) |
| `tran ...` | creates new tran plot, **current plot switches to it** |
| `meas tran name ...` | creates vector `name` in **current tran plot**; also prints result |
| `setplot plotname` | switches current plot |
| `{plotname}.vecname` | cross-plot read; works in `let` assignments |
| `$&vecname` | scalar extraction; for `echo`/`set`/`print` only, NOT for `[...]` indexing |
| `$?varname` | checks shell variable namespace only; never true for `let`/`meas` vectors |

---

## `echo` gotchas

ngspice passes `echo` arguments through something that interprets shell metacharacters.
Avoid `<`, `>`, `(`, `)`, `|` inside echo strings — they will be treated as redirects or
subexpressions and produce "No such file or directory" errors.

```spice
* WRONG — < is interpreted as shell redirect
echo   trip on out1 (t1 < t2)

* CORRECT
echo   trip_on = out1
```

---

## Mismatch injection: `alter` vs `reset` + PDK re-seed

The `reset` command re-loads the netlist but **may not re-randomize** PDK statistical
parameters depending on the model library and ngspice version. Using `reset` alone in a
loop can produce identical device parameters across runs, making MC useless.

The reliable approach for GF180 (and similar PDKs with `agauss()`-based mismatch):
explicitly `alter` the device parameters each iteration using `sgauss(0)`:

```spice
let svt = 3.0e-3     * 1-sigma Vth mismatch in volts; = AVT/sqrt(WL)
alter @m.x1.xm10.m0[delvto] = svt * sgauss(0)
alter @m.x1.xm8.m0[delvto]  = svt * sgauss(0)
```

Also add `.options seed=random` in the MODELS block so each top-level simulation gets a
different base seed.

To verify mismatch is actually varying: print one altered parameter inside the loop and
confirm the value changes run-to-run:

```spice
echo   delvto10 = $&@m.x1.xm10.m0[delvto]
```

---

## Output polarity check for `fall=LAST` vs `fall=FIRST`

`meas tran trip_time when v(out1)=1.5 fall=LAST` works correctly only if **out1 falls
below 1.5 V on every clock cycle BEFORE the flip** (when VIN1 < VIN2 + offset) and stays
high after. In that case the last falling edge ≈ the decision point.

If out1 has the opposite polarity (high before the flip, low after), `fall=LAST` returns
the final clock cycle artifact on every run. Switch to:

```spice
meas tran trip_time when v(out1)=1.5 fall=FIRST
```

Always verify polarity with a single waveform plot before running MC.

---

## Useful reference

`ngspice_code_sampe.txt` in the repo root is a forum post demonstrating vector/variable
syntax with runnable examples and expected output. Key things it shows:
- Vector indexing syntax: `let arr[indexvec] = value` (bare name, no `$&`)
- `$&vecname` for scalar extraction in string contexts
- `set sltwopi="$&ltwopi"` to copy a vector value into a shell variable
- `compose` for building vectors without `let`
