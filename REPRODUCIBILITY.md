# Reproducibility — Hungry Chippos 8-bit SAR ADC (GF180MCU)

Every verification claim in `PROGRESS.md` can be re-run with the
commands below. **All tools run inside the container** — nothing is
installed on the host.

## 1 · Environment

```bash
docker run -d --user 501:20 -v "$(pwd)":/foss/designs \
  --name sar_sim hpretl/iic-osic-tools:chipathon26 tail -f /dev/null
# or, if the container already exists:
docker start sar_sim
```

Every `docker exec` needs two workarounds (both documented in
`designs/scripts/gen_dac_switch_layout.py`):

```bash
docker exec -e HOME=/headless -e USER=headless \
  -e PATH=/foss/tools/klayout:/usr/local/bin:/usr/bin:/bin sar_sim <cmd>
```

- `HOME`/`USER`: `docker exec` doesn't set them and the uid has no
  passwd entry → gdsfactory's `getpass.getuser()` crashes.
- `PATH`: `klayout` lives at `/foss/tools/klayout/`, not on the default
  non-login PATH.

PDK: **gf180mcuD, variant=D always** (metal_top=11K, mim_option=B,
metal_level=5LM — the real signed-off stack; variant=A was a mismatch,
see `dac/WORKLOG.md` 2026-07-18).

## 2 · Non-negotiable simulation settings

These were each earned by a debugging session; violating them produces
*silently wrong* results:

| Rule | Why |
|---|---|
| `.tran` max step ≤ **0.05n** AND `.option reltol=1e-4` for anything containing the StrongARM comparator | coarser settings corrupt sub-ns regeneration: fake ±2–4 LSB sawtooth, fake non-monotonicity, fake near-rail decision inversions (INT-6 retraction) |
| per-code **constant-VIN** decks, never PWL staircases | staircase corners abort ngspice at reltol=1e-4 (`trouble with node vvin#branch`) |
| `.save` only the measured signals | otherwise ngspice allocates GBs and dies |
| MIM caps need BOTH `.lib sm141064.ngspice mimcap_typical` AND `... cap_mim` | caps silently open-circuit otherwise |
| RST_N must be released during a CLK-**high** phase | comparator strobes on CLK falls; releasing during CLK-low latches a stale MSB comparison (pin_contracts §5) |
| xschem netlisting: run from `sar_logic/sar_designs`; never create same-name cells in two libs | subckts are emitted by basename — a name collision silently binds the wrong subckt (the DAC gate cells are `dac_nand2` etc. for this reason) |

## 3 · Physical verification (any block, and the chip)

```bash
# DRC (variant=D, terminal flow — the KLayout GUI LVS menu is broken, see handoff/README.md)
bash designs/scripts/run_dac_drc.sh <gds> <topcell> <run_dir> D
# LVS vs a native-element reference (X-calls to undefined subckts
# silently extract 0 devices = FALSE PASS — references must use M/C cards)
bash designs/scripts/run_dac_lvs.sh <gds> <topcell> <ref.spice> <run_dir> D VSS
```

Signed-off artifacts and their references:

| Block | GDS (topcell) | LVS reference | Devices |
|---|---|---|---|
| DAC | `dac/layout/dac_top_floorplan.gds` | `dac/layout/dac_top_ref.spice` | 377 |
| Comparator | `comparator/layout/strongarm.gds` | `comparator/schematic/strongarm.spice` | 11 |
| SAR (flat strip) | `sar_logic/layout/sar_cells.gds` (`sar_logic`) | `sar_logic/layout/refs/sar_logic_ref.spice` | 458 |
| SAR (3-row fold, used on chip) | `sar_logic/layout/sar_folded.gds` (`sar_logic`) | same | 458 |
| Glue | `adc_top/layout/adc_glue.gds` (`adc_glue`) | `adc_top/layout/refs/adc_glue_ref.spice` | 16 |
| **Chip** | `adc_top/layout/adc_chip_top.gds` (`adc_top`) | `adc_top/layout/refs/adc_top_ref.spice` (generated) | **862** |

Regenerate any generated layout / reference:

```bash
python3 designs/scripts/gen_sar_layout.py            # flat sar_cells.gds
python3 designs/scripts/gen_sar_layout.py --fold 3   # sar_folded.gds
python3 designs/scripts/gen_adc_glue_layout.py       # adc_glue.gds
python3 designs/scripts/gen_adc_chip_top.py          # adc_chip_top.gds (+ taps + dummy fill + self-checks)
python3 designs/scripts/gen_adc_chip_ref.py          # adc_top_ref.spice
```

Chip-only extra checks (both must be clean):

```bash
cd <run_dir> && python /foss/pdks/gf180mcuD/libs.tech/klayout/tech/drc/run_drc.py \
  --path=.../adc_chip_top.gds --variant=D --run_dir=. --topcell=adc_top \
  --run_mode=flat --density_only     # whole-die coverage minima (dt-4 fill)
# same with --antenna_only
```

## 4 · Gate-by-gate electrical verification

| Gate | Command(s) | Expected |
|---|---|---|
| Gate 1 (comparator) | `comparator/` MC + delay decks, see `comparator/WORKLOG.md` | σ=36.9 mV (calibratable), delay 362 ps worst corner |
| Gate 2 (DAC settling) | `dac/sim/tb_major_carry.sch` flow, `VERIFICATION_PLAN.md` | worst corner SS/125 °C/2.97 V settles 3.86 ns |
| Gate 3 (TT transfer) | `python3 designs/scripts/gen_adc_sweep_tt.py adc_top/sim/sweep_tt_fine2` then `cd` there, `ls code_*.spice \| xargs -P 8 -I{} sh -c 'ngspice -b {} > {}.log 2>&1'`, then `python3 designs/scripts/check_adc_sweep.py adc_top/sim/sweep_tt_fine2` | monotonic, no missing codes, codes 39–102 exact, 103–255 = −1, 1–38 dead |
| Gate 4 (MOS corners) | same with corner arg `ff/ss/fs/sf`, dirs `adc_top/sim/sweep_{ff,ss,fs,sf}` | identical structure; dead zone FF 0.40 V … SS 0.62 V (`adc_top/sim/corners_report.md`) |
| Supply/temp follow-up | `python3 designs/scripts/gen_adc_sweep_vt.py <dir> --vdd 3.0\|3.6 --temp -40\|125` + run + `--check` | monotonic, offset band only |
| ENOB (REP-2) | `python3 designs/scripts/calc_enob.py --transfer adc_top/sim/sweep_tt_fine2/sweep_codes.csv --vlo 0.65 --vhi 3.25` | SNDR 45.3 dB → **ENOB 7.23 bits** (static-projected) |

## 5 · One-shot regression

```bash
bash designs/scripts/run_all_sims.sh          # layouts + all DRC/LVS + summary
bash designs/scripts/run_all_sims.sh --full   # + the 256-code TT sweep (hours)
```

## 6 · Datasheet lines (as verified)

- 8-bit SAR, FS = 3.3 V (VDD-referenced), 1 LSB = 12.9 mV
  (measured FS 3.293 V)
- Input range **0.65–3.25 V** quoted (guaranteed 0.62–3.29 V across MOS
  corners; low bound tracks the NMOS corner)
- Offset ≈ −0.5 LSB, calibratable; monotonic, no missing codes
- **ENOB 7.2 bits / SNDR 45.3 dB** (static-transfer-projected at 79 % FS
  swing); no input S/H → full-swing sine BW ≈ 1.5 kHz, DC/stepped
  inputs unaffected
- **833 kS/s @ 10 MHz CLK** (12 CLK per conversion: reset ≥ 1 period +
  8 trials + EOC margin); timing closes with >10× slack — CLK is not
  the limit below ~100 MHz (re-verification needed to claim it)
