# Prompt for next Claude session — padring integration watch (post-sign-off)

Copy-paste everything below the line into a fresh Claude Code session started in the repo root.

---

Read PROGRESS.md and REPRODUCIBILITY.md first. As of 2026-07-31 the ADC is **done**: Gates 1–5 all
PASS, chip block `adc_top/layout/adc_chip_top.gds` (topcell `adc_top`, 514×550 µm, 13 labeled M5
south-edge pins) signed off — DRC 0/660, LVS "Netlists match" 862/862, density + antenna clean.
The SS × −40 °C cross-corner is also closed (`adc_top/sim/supply_temp_report.md`): the dead zone
ends ≈0.70 V there, so the **quoted input range is 0.70–3.25 V** (ENOB re-projected at that swing:
7.20 b / SNDR 45.10 dB; CI regression updated). Regression: `run_all_sims.sh` = ALL CHECKS PASS.

Remaining work, in priority order — none is load-bearing, verify before touching anything:

1. **Padring integration (the only real deliverable).** Watch `sscs-ose/sscs-chipathon-2026`
   (`resources/Integration` currently has only generic previous-year padring docs) and our issue
   #18 thread (@d-m-bailey) for the final 2026 padframe geometry / integration repo. When it
   drops: place `adc_top` into the actual Block B slot, wire our 13 pins to pads, confirm whether
   power/ground count against Block B's 16-pin quota. **Aug 6 dry run:** our GDS is ready as-is;
   produce whatever wrapper format is asked from `adc_chip_top.gds`. Re-run chip DRC/LVS after
   ANY geometry change (`run_all_sims.sh`). Issue #18's body already carries area + pin list
   (updated 2026-07-31). ⚠️ Repo docs (issue #18 body, slides) still quote the OLD 0.65–3.25 V
   range + 7.23 b ENOB — update the issue body when the team ratifies the revised numbers.
2. **COMP-9 full-RC PEX** (optional, confirmation-only, 5.4× delay margin). Magic ext2spice
   attempt lives in `comparator/layout/pex/` (committed) — magic doesn't bind the 34/10 labels as
   ports and merges nets into VSS. If resuming: try port commands / label datatype remapping in
   the magicrc cifinput section, or klayout-to-magic label conversion. Don't sink more than a
   session; the bounding argument in the PROGRESS COMP-9 row already covers it.
3. **Spec ratification** (team): ENOB 7.20 b @ 0.70–3.25 V swing + 833 kS/s @ 10 MHz are
   proposed, pending team sign-off.

Env/workflow (hard-won, don't rediscover): everything runs in docker `sar_sim`
(`hpretl/iic-osic-tools:chipathon26`; `docker start sar_sim` if stopped). Every `docker exec`
needs `-e HOME=/headless -e USER=headless -e PATH=/foss/tools/klayout:/foss/tools/ngspice/bin:/usr/local/bin:/usr/bin:/bin`
(klayout AND ngspice are off the default PATH — silent instant-fail xargs runs otherwise).
DRC/LVS: `run_dac_drc.sh`/`run_dac_lvs.sh`, variant=D always, lvs_sub=VSS, absolute paths only
(they cd first). LVS references must be native M/C elements (X-calls silently extract 0 devices =
false pass). StrongARM sims: `.tran` max step ≤0.05n + reltol=1e-4, per-code constant-VIN decks,
`.save` only measured signals. MetalTop@11K: MT.1 0.44 / MT.2a 0.46 / MT.4 0.5625 µm² — no M5
below those, ever. Chip layout changes go through `gen_adc_chip_top.py` (never hand-edit the GDS).

Conventions: update PROGRESS.md rows as you close items; commit style `int:`/`comp:`/`rep:` with
detailed bodies; branch from main + PR (don't push to main); verify every claim by running the
tool — never eyeball.
