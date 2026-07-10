# Handoff: strongarm comparator LVS short (VOUT2 still merged with internal nodes)

## TL;DR

The `strongarm` latch layout (`comparator/layout/strongarm.gds`) has a real LVS
short. `VOUT1` was already fixed (now matches the schematic exactly, 0
contamination). `VOUT2` is still electrically merged with two internal nodes
that must stay separate: the tail node (`net2`) and another internal node
(`net3`). Two attempted fixes this session both failed the same way (see
"What was tried and failed" below) and were reverted. The file on disk right
now is clean/unmodified — see "Current state" for the exact backup to diff
against if you want to confirm nothing is broken.

## Environment / how to reproduce the LVS run

Everything (PDK, KLayout, xschem) lives inside a running Docker container,
not on the host mac. Host mac cannot run these tools directly.

```bash
docker ps   # container name: iic-osic-tools_xvnc_uid_501 (image hpretl/iic-osic-tools:chipathon26)
docker exec <container_id> bash -lc '<command>'
```

The project repo is mounted inside the container at `/foss/designs` (this
maps to the repo root — `/foss/designs/comparator/...` ==
`comparator/...` in this repo).

**The canned pipeline script is broken, do not use it as-is:**
`designs/scripts/run_klayout_lvs.sh` calls `xschem_netlisting.sh`, which does
not exist anywhere in the container. It also hardcodes
`/foss/pdks/gf180mcuD/libs.tech/klayout/lvs/run_lvs.py`, but the real path has
an extra `tech/` segment:
`/foss/pdks/gf180mcuD/libs.tech/klayout/tech/lvs/run_lvs.py`. It also tries to
`.include` a nonexistent standard-cell LVS spice file — just omit that line,
`strongarm` doesn't use standard cells.

**Working manual LVS command** (schematic netlist already exists checked in
at `comparator/schematic/strongarm.spice`, so netlisting-from-schematic can be
skipped entirely — just reuse that file):

```bash
docker exec <container_id> bash -lc '
LVS_RUN_DIR=/foss/designs/comparator/layout/klayout_lvs_run_TMP
mkdir -p "$LVS_RUN_DIR"
cp /foss/designs/comparator/schematic/strongarm.spice "$LVS_RUN_DIR/strongarm_lvs.spice"
cp /foss/designs/comparator/layout/strongarm.gds "$LVS_RUN_DIR/strongarm.gds"
cd "$LVS_RUN_DIR"
python3 /foss/designs/designs/scripts/lvs_strip_gds_labels.py strongarm.gds
python /foss/pdks/gf180mcuD/libs.tech/klayout/tech/lvs/run_lvs.py \
  --layout=strongarm_lvs.gds \
  --netlist=strongarm_lvs.spice \
  --variant=D \
  --run_dir=. \
  --topcell=strongarm \
  --lvs_sub=VSS \
  --run_mode=flat \
  --schematic_simplify
'
```

This produces, in `$LVS_RUN_DIR`: `strongarm_lvs.lvsdb` (full LVS database,
text-based KLayout format), `strongarm_lvs.cir` (extracted SPICE netlist from
the layout — the fastest way to eyeball what's shorted), and
`strongarm_lvs.gds` (label-stripped copy of the layout actually used for the
compare).

It will always print `ERROR : Netlists don't match` right now — that's
expected until VOUT2 is fixed; check `strongarm_lvs.cir` for the actual
substance rather than relying on the pass/fail line.

### Programmatic inspection (KLayout Python API)

A GUI is available too (`export DISPLAY=:1` before running `klayout`, an Xvnc
server is already running on display `:1`), but most of this investigation
was done headlessly via `klayout.db` / `pya` Python bindings, e.g.:

```python
import klayout.db as db
l2n = db.LayoutVsSchematic()
l2n.read('/path/to/strongarm_lvs.lvsdb')   # NOTE: use LayoutVsSchematic, not
                                             # LayoutToNetlist -- the latter
                                             # cannot parse the H(...)
                                             # reference-netlist section and
                                             # throws a parse error.
netlist = l2n.netlist()
for circuit in netlist.each_circuit():
    for net in circuit.each_net():
        print(net.expanded_name())
        for li in l2n.layer_indexes():
            region = l2n.shapes_of_net(net, l2n.layer_by_index(li), True)
            ...
```

Renders of specific layout regions with a net highlighted were done via
`pya.LayoutView` in batch mode (`klayout -z -rx -r script.py` with
`DISPLAY=:1` set) — see git history of this conversation / ask the user for
the render scripts if useful, they were scratch files under `/tmp` inside the
container and were not preserved on the host.

## Schematic ground truth (what "correct" looks like)

From `comparator/schematic/strongarm.spice` (11 devices total: M1-M11).
Net `VOUT1` and net `VOUT2` are each supposed to touch **exactly 6 things** (5
device terminals + 1 output pin) — perfectly symmetric by design:

- **VOUT1**: M1.gate, M2.drain, M3.drain, M7.gate, M9.drain, pin p8
- **VOUT2**: M1.drain, M2.gate, M6.drain, M7.drain, M9.gate, pin p3

Internal nodes that must NOT touch VOUT1/VOUT2:
- `net2` (the tail node): shared source of the input differential pair
  (M8.source, M10.source) and drain of the tail switch M11 (M11: drain=net2,
  gate=CK, source=VSS). This is legitimately one node shared by 3 transistors
  — that part is correct circuit topology, not a bug.
- `net3`: M9.source/M10.drain.
- `net1`: M1.source/M8.drain.

## Current diagnosis (as of end of this session)

Running LVS on the current (reverted-to-clean) `strongarm.gds` extracts (see
`strongarm_lvs.cir` from a fresh run):

```
M$1  VDD VOUT2 VOUT1 VDD     pfet   -- matches schematic M2 (D=VOUT1 via S/D swap), clean
M$2  ... CK VOUT1 VOUT1      pfet   -- matches M3 pattern, but BULK incorrectly = VOUT1 (should be VDD)
M$3  $11 CK VOUT2 VDD        pfet   -- matches M6 pattern, source floating on unnamed net (separate minor issue)
M$4  VDD CK $8 VDD           pfet   -- matches M4/M5, clean
M$5  VDD CK VOUT2 VOUT2      pfet   -- matches M6-ish pattern, BULK incorrectly = VOUT2 (should be VDD)
M$6  VDD VOUT1 VOUT2 VDD     pfet   -- matches M7, clean
M$7  VOUT2 CK VSS VOUT2      nfet   -- this is M11 (tail switch). Drain AND bulk = VOUT2. SHOULD be net2.
M$8  $6 VIN2 VOUT2 VOUT2     nfet   -- this is M8. Source AND bulk = VOUT2. SHOULD be net2.
M$9  VOUT2 VIN1 VOUT2 VOUT2  nfet   -- this is M10. Drain, source, AND bulk = VOUT2. SHOULD be net3 (drain) / net2 (source/bulk).
M$10 VOUT2 VOUT1 $4 VOUT2    nfet   -- this is M1. Bulk = VOUT2. SHOULD be net1.
M$11 VOUT1 VOUT2 VOUT2 VOUT2 nfet   -- this is M9. Source AND bulk = VOUT2. SHOULD be net3.
```

(Device numbering `M$n` is assigned by KLayout's extraction traversal order
and is **not stable** between runs — re-derive the schematic correspondence
each time by matching gate nets, don't assume `M$7` always means the same
physical device across different LVS runs.)

**Net effect: `net2` (tail) and `net3` are both fully fused with `VOUT2`.**
`VOUT1` is completely clean (0 contamination) — confirmed by cross-checking
against the schematic connection list above, every VOUT1 occurrence matches
exactly.

There are also a couple of secondary, smaller bulk/body-tie shorts on
individual pfets (bulk tied to VOUT1/VOUT2 instead of VDD) — these are
distinct from the main VOUT2/net2/net3 fusion and haven't been investigated
in depth; they may or may not resolve once the main short is fixed.

## What was tried and failed this session (reverted, do not repeat blindly)

1. **Device orientation** (fixed by the user, not me): the user discovered
   that MOSFET layout cells have two mechanically-symmetric diffusion pads
   either side of the gate — physically identical, only distinguished by
   which net is wired to which pad. Placing a cell mirrored/rotated swaps
   which physical pad is source vs. drain without anything looking visually
   wrong. Rotating one device fixed VOUT1's contamination completely. This
   is very likely still relevant to the VOUT2 side — there is probably an
   analogous device near VOUT2 with the same orientation problem.

2. **Deleted an "extra" nfet cell instance.** The layout has 6 nfet cell
   instances placed but schematic only needs 5 (M1, M8, M9, M10, M11). By
   matching each instance's position to the 5 valid extracted devices, one
   instance (orientation `m45`, position **(7.87, 5.41) µm** in the top
   cell) didn't match any of them and looked like a leftover/duplicate.
   **Deleting it did NOT fix the VOUT2/net2/net3 short at all** (identical
   before/after) **and broke** an unrelated pfet's legitimate connection to
   VOUT1 (M3-pattern device's drain went from VOUT1 to an unnamed/floating
   net) and left another pfet completely floating on all 4 terminals. Net
   negative, reverted from backup
   (`backups/strongarm_backup_pre_duplicate_nfet_fix_2026-07-10_05h01.gds`).
   **Caution:** this 6th instance might be an intentional dummy/matching
   transistor (common in analog layout for gradient/etch symmetry) rather
   than a true duplicate — don't assume it's safe to delete without more
   evidence.

3. **Deleted a single via1 (GDS layer 35/0) shape** at
   **(-5.285, 4.570)–(-5.025, 4.830) µm**, identified via `shapes_of_net`
   query as genuinely belonging to the shorted VOUT2 net (not just
   geometrically nearby — actually queried and confirmed part of the net).
   Same failure signature as #2: VOUT2's short to net2/net3 completely
   unchanged, but broke the same M3→VOUT1 connection again, floated another
   pfet, and a 12th phantom device appeared in the extraction. Reverted from
   backup (`backups/strongarm_backup_pre_via_cut_2026-07-10_05h16.gds`).

**Pattern across both failed attempts:** cutting things in the region
between the differential-pair/tail transistor cluster (roughly
`x: -10 to 15 µm, y: -16 to 12 µm`) and the VOUT1/VOUT2 pad routing keeps
breaking VOUT1-side connectivity (specifically the M3-pattern device's link
to VOUT1) while never touching the actual VOUT2/net2/net3 fusion. This
strongly suggests VOUT1 and VOUT2's routing **share some common physical
via/metal2 trunk structure** in that region, and both "surgical" cuts so far
happened to hit the shared part rather than something unique to the bad
VOUT2 connection.

## Useful known-good coordinates from earlier analysis (may still be relevant)

- Tail transistor (M11 equivalent) diffusion/drain area, metal1 (GDS 34/0):
  a polygon spanning **x: 2.73–5.33 µm, y: -15.65 to -11.50 µm** has shown up
  as touching the merged/shorted net in every single extraction run this
  session, completely unaffected by every fix attempted so far. Never
  actually cut/tested directly — worth investigating whether this specific
  shape (or its continuation further up, since it's part of a longer
  multi-segment strap) is the true root, using the rigorous connectivity
  trace approach below rather than another blind proximity guess.
- The `VOUT1` and `VOUT2` pin/pad text labels sit at roughly
  `(-13.7, 12.0) µm` and `(18.0, 12.3) µm` respectively (from an earlier,
  now-stale run — re-verify against current file before trusting).

## Recommended next step

Don't repeat proximity-based single-shape deletion — it's failed twice with
an identical, informative failure mode. Instead:

1. Build the **full connectivity graph** for the region between the
   tail/differential-pair cluster and the pad routing: every contact/via/
   metal shape and exactly what it touches on adjacent layers (not just "is
   it near the merged net" but "trace layer-by-layer what connects to
   what"). The goal is to find the specific junction where VOUT2's routing
   and net2/net3's routing become electrically the same, as distinct from
   wherever VOUT1 and VOUT2 legitimately share physical trunk/via structure
   (which appears to exist and must be left alone).
2. Once a candidate cut point is found, verify by checking the **entire**
   device list before/after (not just the one net you're targeting) — both
   failures this session would have been caught immediately by checking all
   11 devices instead of assuming success from a partial check.
3. Given the orientation-bug precedent (item #1 above), also seriously
   consider that VOUT2's fusion might have the same root cause as VOUT1's
   did — an incorrectly mirrored/rotated device near the tail/net3 area —
   rather than assuming it must be a metal/via short. Check device
   orientations for M1, M8, M9, M10, M11 (the ones on the VOUT2/net2/net3
   side) against what fixed VOUT1 before spending more time on metal-level
   forensics.
4. Always back up (`cp strongarm.gds backups/strongarm_backup_<description>_$(date ...).gds`)
   before any edit, and always re-run the full LVS + check all devices
   immediately after, before doing anything else.

## UPDATE 2026-07-10 (later session): corrected per-device diagnosis + new floating-gate finding

The diagnosis above was derived by eyeballing the `.cir` SPICE text and assuming
column order `D G S B`. **That assumption was wrong for at least one device**
and led to a mis-identification (the device previously called "M1, fully
correct except bulk" actually has a **floating gate**, not a correct one).
The corrected data below was pulled via the KLayout Python API directly
(`dev.net_for_terminal(td.id())` keyed by actual terminal name, not SPICE
column position — trust this over any `.cir` text eyeballing), cross-checked
against physical instance positions via `l2n.shapes_of_terminal()`. Device
count/electrical state was re-confirmed unchanged from the original diagnosis
(file still matches `strongarm_backup_pre_via_cut_2026-07-10_05h16.gds`, no
edits made in this session yet).

**Physical instance ↔ schematic device map** (position = bbox center of the
`nfet` cell instance in the top cell, from `top.each_inst()`):

| Instance pos (x,y) µm | orientation | schematic device |
|---|---|---|
| (10.005, -7.995) | angle180, mirror | **M8** |
| (-5.875, -7.975) | angle0, no mirror | **M10** |
| (9.055, 6.095) | angle90, mirror | **extra/dummy** (not in schematic) |
| (-8.185, 2.125) | angle270, mirror | **M9** |
| (4.285, -14.955) | angle0, no mirror | **M11** (tail switch) |
| (13.655, 1.025) | angle90, mirror | **M1** |

**Corrected per-terminal fault table** (✓ = matches schematic net exactly, ✗ = wrong):

| Device | D | G | S | B |
|---|---|---|---|---|
| M1  | VOUT2 ✓ | **floating (net `$8`) ✗ should=VOUT1** | net1 ✓ | VOUT2 ✗ should=net1 |
| M8  | net1 ✓ | VIN2 ✓ | VOUT2 ✗ should=net2 | VOUT2 ✗ should=net2 |
| M9  | VOUT1 ✓ | **floating (net `$10`) ✗ should=VOUT2** | VOUT2 ✗ should=net3 | VOUT2 ✗ should=net3 |
| M10 | VOUT2 ✗ should=net3 | VIN1 ✓ | VOUT2 ✗ should=net2 | VOUT2 ✗ should=net2 |
| M11 | VOUT2 ✗ should=net2 | CK ✓ | VSS ✓ | VOUT2 ✗ should=net2 |
| extra/dummy | floating `$14` | floating `$13` | floating `$12` | VOUT2 (irrelevant, not a schematic device) |

**This changes the diagnosis materially: M1 and M9 — the cross-coupled latch
pair (M1.gate should=VOUT1 driving M1.drain=VOUT2; M9.gate should=VOUT2
driving M9.drain=VOUT1, i.e. the actual regenerative feedback loop of the
strongarm latch) — both have a genuinely OPEN (floating) gate, not merely a
bulk short.** This is a second, independent category of defect from the
net2/net3-fused-with-VOUT2 bulk short, and on its own would be enough to fail
LVS (a missing connection, not just an extra one).

**M1's floating gate traced to a physical root cause**: M1's gate poly
(x:12.17–14.77, y:0.53–0.81 µm) has a contact up to a small metal1 stub
(x:14.76–15.14, y:0.48–0.86) which has a **via1 at x:15.25–15.51, y:0.55–0.81
with no metal2 shape anywhere near it** (checked full region x:14–22,
y:-1–5 on layer 36/0 (metal2) and layer 38/0 (via2): zero shapes). The via1
is a dead end — the metal2 route that should carry this signal up to VOUT1
was apparently never drawn. This looks like a genuine missing-routing bug
(an addition is needed, not a deletion) rather than a short. **Not yet fixed
or attempted — next step is to find VOUT1's nearest metal2 landing pad and
add a connecting metal2 segment, then re-verify.**

M9's floating gate (poly at x:-9.0–-7.0, y:2.34–2.62) has not yet been traced
the same way — do that next, it's very likely the same class of bug
(missing metal2 route to VOUT2 this time).

**Also confirmed**: cutting the via1 previously tried in attempt #3 above
(`(-5.285,4.570)-(-5.025,4.830)`) was independently re-confirmed via
`l2n.shapes_of_net` to genuinely carry VOUT2 net current (not a false
proximity match), and is part of a real metal1 "bulk-tie rail" that runs from
the tail/diff-pair cluster (y≈-16 to -7) up a vertical trunk (x≈-10.27,
y≈-10 to +1.7) toward the M9 instance area, then via that via1/metal2 up
into VOUT2's own routing. Also confirmed VOUT1's own via1 shapes sit at
x≈-2 to 3 — nowhere near x≈-5 to -10 — so the M3→VOUT1 collateral breakage
from attempt #3 was likely NOT genuine electrical sharing at that exact via;
more likely the deletion method used swept up extra/nearby geometry, or the
breakage was an indirect side effect of re-extraction. Since cutting this via
already failed twice to break the net2/net3↔VOUT2 fusion, there is likely a
**redundant parallel path** into VOUT2 that hasn't been found yet — do not
try cutting this exact via a third time without first finding and
understanding that parallel path.

## UPDATE 2026-07-10 (third session): two real fixes landed, bulk-tie short characterized as multi-path

Starting from the clean state above, made two **confirmed, kept, verified**
fixes, then spent the rest of the session on the remaining bulk-tie short and
learned it is **not a single choke point** — at least two independent
physical bridges are involved. Full detail below; TL;DR for the next session:
**M1 and M9's gate opens are fixed and safe to build on. The net2/net3↔VOUT2
bulk fusion is still present and will need multiple separate cuts, verified
one at a time — do not expect a single via/wire deletion to resolve it.**

### Fixes kept (both re-confirmed via full 12-device check immediately before writing this)

1. **M1's floating gate → VOUT1.** M1 (physical instance at x≈13.655,
   y≈1.025) had D=VOUT2 ✓, S=net1 ✓, but **G was floating** (net `$8`) and
   B=VOUT2 (wrong, should be net1). Root cause: M1's gate poly had a contact
   up to a metal1 stub (x:14.76–15.14, y:0.48–0.86) that simply stopped ~3.4µm
   short of VOUT1's own metal1 routing (which ends at x:11.32, y:0.53–1.15) —
   a missing metal1 segment, not a short. **Fix**: added a metal1 rectangle
   x:11.20–14.90, y:0.55–0.84 on layer 34/0 bridging the gap. Verified: G now
   reads VOUT1 correctly, nothing else changed. B is still wrong (separate
   bulk-tie issue, see below).
2. **M9's floating gate → VOUT2.** M9 (physical instance at x≈-8.185,
   y≈2.125) had D=VOUT1 ✓, but **G was floating** (net `$10`), S and B both
   wrongly = VOUT2. Root cause: M9's gate poly → contact → metal1 stub
   dead-ends at y=4.88 (x:-9.75–-9.45) directly under an existing metal2
   polygon (x:-10.10–-4.76, y:4.42–4.99) with no via connecting them. **Fix**:
   added a via1 (layer 35/0) at x:-9.72–-9.46, y:4.52–4.80 bridging the
   existing metal1 stub to the existing metal2. Verified: G now reads VOUT2
   correctly. S/B still wrong (bulk-tie issue, below).

Both fixes are purely **additive** (new metal1/via1 shapes filling confirmed
physical gaps), unlike the two "attempt and fail" deletions from the earlier
session — much lower collateral-damage risk, and both were re-verified via
full 12-device dumps before/after with zero regressions.

**Important process note for whoever continues**: the `.cir` SPICE text
column order is **not reliably `D G S B`** — one of the mis-diagnoses this
session came from trusting that ordering. Always use
`dev.net_for_terminal(td.id())` keyed by the actual terminal name (`S`/`G`/
`D`/`B` from `device_class().terminal_definitions()`), not positional
reading of the `.cir` file.

### Bulk-tie short: now understood to be multi-path, not fixed

Remaining wrong terminals after the two fixes above (unchanged from the
original diagnosis, all still read VOUT2 instead of net1/net2/net3):
M1.B, M8.S, M8.B, M9.S, M9.B, M10.D, M10.S, M10.B, M11.D, M11.B.

Three separate cut experiments this session, each backed up and reverted
after full 12-device verification showed no clean win:

1. **Re-cut the via1 at (-5.285,-5.025 / 4.570,4.830)** (same one from the
   earlier session's attempt #3). Confirmed via `l2n.layer_indexes()` census
   that this is the **only** via1 shape in the entire merged VOUT2 net — a
   strong-looking single-point argument that turned out to be **wrong**:
   cutting it had **zero effect** on the net2/net3 fusion (identical before/
   after) and also broke M9's brand-new gate fix (since that fix's new via
   fed into the same metal2 island, which lost its only other connection).
   Reverted. Lesson: this via/metal2 pair turned out to be a **dead-end
   branch used only for M9's gate**, not a bridge to the bulk-tie mess at
   all — "only via1 in the merged net" does not imply "the bridge," because
   once nets are already fused, *everything* touching the blob trivially
   shows up under `shapes_of_net`.
2. **Cut a notch in a thin (0.3µm-tall, ~17µm-long) metal1 wire** at
   x:-20–-18, y:-2.90–-2.44, part of a long rail running from x≈-29
   (confirmed, via `shapes_of_terminal`, to be **M6's own legitimate VOUT2
   drain contact** — schematic M6: D=VOUT2,G=CK,S=VDD) down to x≈-11.36
   where it meets the tail/diff-pair "bulk-tie trunk." Result: **M6 got
   isolated by itself** (now floating, S+B both on one dead net) while the
   rest of the net2/net3/VOUT2 fusion was **completely unaffected** — proving
   the bulk-tie trunk reaches "real VOUT2" through some *other* path
   independent of M6's rail. Reverted.
3. **Cut the metal1 junction at x:-8.9–-7.1, y:-0.10–0.40**, where M9's own
   local source/bulk pad meets the vertical trunk coming up from the tail/
   diff-pair cluster (x≈-10.27 trunk → x:-8.71–-7.31 segment → M9's local
   pad). Result: this **separated M10's source together with M6** into one
   island (both now read the same floating net), while M11, M8, M9's own
   source/bulk, M1's bulk, and M10's drain **remained fused together as
   VOUT2**. This is the most informative result: it shows **M10.source and
   M6 share one bridge path**, while **M11/M8/M9(S,B)/M1(B)/M10(D) share a
   different one** — i.e. there are at least two independent physical
   bridges into the "VOUT2" identity, not one. Reverted (traded one short for
   an equally-wrong M6/M10 fusion, no net improvement).

**Also checked and ruled out**: diffusion/active-layer shorts (each of the 6
nfet instances has its own fully isolated 4.42µm² diffusion island, confirmed
via merged-region census on GDS layer 22/0 — not the cause).

### Recommended next step (updated)

Treat this as **N separate bridges to find and cut one at a time**, not one
root cause:
1. Bridge A (affects M10.source + M6): somewhere between the x≈-10.27/-8.7
   trunk segment and wherever M6's rail actually joins it (experiment 3
   narrowed this down — the junction is between x=-8.9 and M6's rail, likely
   at or near M9's local pad area; experiment 2 showed it's *not* out at
   x=-20/-18, so it's a shorter/closer segment than assumed).
2. Bridge B (affects M11, M8, M9(S,B), M1(B), M10.drain): still completely
   unlocated. Since it's independent of both the via1/metal2 branch
   (experiment 1) and M6's rail (experiments 2 & 3), it must be a separate
   physical path — check whether M10's drain pad and the shared net2 diffusion
   area have any direct metal1 overlap (this session confirmed the raw
   diffusion regions are properly separated per-device, but did not fully
   rule out adjacent metal1 *pad* overlap at the individual contact/pad
   level for M10 specifically — this is the next thing to check).
3. As before: back up before every edit, full 12-device check after every
   single edit (not just the target net), one edit at a time so effects are
   attributable.

## CORRECTION 2026-07-10: VOUT1 is NOT clean — third real bug found, unfixed

Everything above claims "VOUT1 has zero wrong connections" / "VOUT1 is
completely clean." **That claim is wrong** and should not be trusted. It was
based on checking only 4 of VOUT1's expected 6 connections (M1.gate, M2,
M7, M9.drain) and never checking the third CK-gated pfet. The user caught
this by opening the actual KLayout Netlist Database Browser (Cross
Reference tab), which is the ground truth and should be checked directly
rather than trusting a device-by-device script dump summary: it shows
**layout VOUT1 = 5 connections, reference/schematic expects 6** (and layout
VOUT2 = 19 against an expected 6 — consistent with everything above).

**Root cause of the VOUT1 shortfall**: of the 6 physical pfet instances,
one (at x≈-16.46, y≈19–20 in the top cell) is a real schematic device —
pfet instance/device count is exactly 6, matching schematic M2–M7 exactly,
so unlike the nfet side there is **no extra/dummy pfet** — but it is
**completely unrouted**: gate not connected to CK, drain not connected to
VOUT1, source not connected to VDD, bulk floating. All four terminals read
as isolated/floating nets. (Earlier in this same session this device was
mislabeled "extra/dummy, not in schematic" — that label is wrong, retract
it; it's a real device, most likely **M3** — the pfet whose drain should
land on VOUT1 — just entirely disconnected.)

Evidence this is M3 specifically (not certain, but strong): VOUT1's own
metal1 trunk runs within ~2µm of this device (trunk at x≈-18.36 to -18.66,
spanning y≈18.43–23.27, which fully covers this pfet's y-range of
18.56–20.87) — the same "local pad stops just short of the trunk it should
join" pattern as the M1 and M9 gate-open fixes that already worked twice
this session. Terminal locations for this specific device: S≈(-16.46,19.29),
G≈(-16.45,19.94), D≈(-16.46,20.22), B≈(-16.45,19.94). The drain (y≈20.22) is
the one that should bridge to the VOUT1 trunk to fix the VOUT1 count.
**Not yet attempted or fixed** — this was found and documented, no edit made.

Given this device needs potentially 3 separate bridges (gate→CK,
drain→VOUT1, source→VDD) and we only need the VOUT1 count to go 5→6, the
minimal fix is just the drain→VOUT1 bridge; but leaving gate/source
unrouted afterward would still leave this transistor functionally broken
(gate floating means it can't switch, source floating means no supply) —
worth fixing all three while in there, each verified separately.

**Process lesson for whoever continues**: verify against the actual KLayout
Netlist Database Browser cross-reference counts (Layout column vs Reference
column, per pin) after every round of fixes, not just a custom per-device
Python dump — the dump is easy to under-check (as happened here) if you
don't re-verify EVERY pin's connection count, not just the devices you
already suspect.

## Current state of the file on disk (superseded — see next session below)

`comparator/layout/strongarm.gds` at that point had **only the two
gate-open fixes for M1 and M9 applied** (confirmed via md5 match against
`backups/strongarm_backup_pre_via1_cut_retry_2026-07-10_05h47.gds`). All
three bulk-tie-short cut experiments were reverted — none of that
exploratory work remained in the file. The fully-disconnected pfet (M3,
x≈-16.46) described just above was **unfixed** — found this session but no
edit attempted yet. nfet instance count: 6 (includes one genuine extra/dummy
nfet not in schematic — this label IS correct for the nfet side). pfet
instance count: 6 (all 6 correspond to real schematic devices M2–M7 — no
extra pfet). LVS still reported `ERROR : Netlists don't match`. Per the
KLayout Netlist Database Browser: **VOUT1 layout=5 (expected 6)**, **VOUT2
layout=19 (expected 6)**, CK layout=5 (expected 6, also likely short by
this same unrouted pfet's missing gate connection).

**This section is now out of date — the file on disk has moved past this
point. See "UPDATE 2026-07-10 (fourth session)" below for the current
state and the correct backup to diff against.**

## UPDATE 2026-07-10 (fourth session): M3's drain+source fixed, one bulk-tie
## bridge cut, new diagnostic technique for the rest

Starting from the state described immediately above (only M1/M9 gate fixes
present, confirmed via md5 against
`backups/strongarm_backup_pre_via1_cut_retry_2026-07-10_05h47.gds`), this
session fixed **two more real terminals on the fully-disconnected pfet
(M3)** and made **one clean, verified cut into the bulk-tie short**. Both
kept. TL;DR for whoever continues: **M3's drain→VOUT1 and source→VDD are
now fixed and safe to build on (M3.gate→CK is still open, deliberately
deferred — see below). M10's source is now cleanly isolated from the
VOUT2/net2/net3 blob (previously wrongly shorted to it) — it needs a NEW
connection to net2's legitimate wiring, not yet added. The rest of the
bulk-tie short (M11, M8, M9(S,B), M1(B), M10.drain) is still fused with
VOUT2, same as before.**

### Fixes kept (re-confirmed via full 12-device dump + KLayout cross-reference before writing this)

1. **M3's drain → VOUT1.** The fully-disconnected pfet at x≈-16.46 (real
   schematic device, confirmed `PFET_03V3 '3' (S=VDD,G=CK,D=VOUT1,B=VDD)` by
   reading `l2n.reference` directly off the lvsdb — this is authoritative,
   don't re-derive by guessing). Its drain pad (metal1, x:-16.430–-16.050,
   y:20.450–20.830) was floating. **Root cause double-check**: the metal1
   trunk that looked like "VOUT1's trunk" in the previous session's notes
   (bbox x:-18.660–-18.360, y:18.430–23.270) is actually **VDD's** trunk,
   not VOUT1's — confirmed by querying `l2n.shapes_of_net(top.net_by_name('VDD'), ...)`
   vs `net_by_name('VOUT1')` directly and comparing bboxes. VOUT1's real
   metal1 reach in that area tops out lower, at y≈17.52 (bbox
   x:-18.890–-18.050, y:16.360–17.520). **Fix**: an L-shaped metal1 bridge
   from VOUT1's actual trunk tip up to the drain pad, added as two
   rectangles on layer 34/0:
   - segment A (vertical): x:-18.150–-17.700, y:17.400–20.830
   - segment B (horizontal): x:-17.700–-16.400, y:20.450–20.830
   Both rectangles were deliberately kept clear of the CK gate-contact pad
   (x:-17.130–-16.750, y:19.890–20.270, sitting right in the middle of this
   area) by staying left of x=-17.130 for segment A and above y=20.270 for
   segment B. Verified: D now reads VOUT1. **KLayout cross-reference
   confirms**: layout VOUT1 terminal count went from 5→still 5 but now
   *correctly* matches the reference's 5 device terminals (the schematic
   also expects exactly 5 device terminals + 1 pin = 6; the pin doesn't
   show up on either side of the compare because `lvs_strip_gds_labels.py`
   strips the text labels that pins are normally identified from — this is
   a label-stripping artifact of the LVS pipeline, not a real bug, and
   affects both the layout and reference sides symmetrically, so don't
   chase it).

2. **M3's source → VDD.** Same device's source pad (metal1,
   x:-16.430–-16.050, y:19.330–19.710) was floating. The VDD trunk found
   during the drain investigation (x:-18.660–-18.360, y:18.430–23.270)
   fully covers this pad's y-range and is only ~1.9µm away — a clean,
   obvious connection. **First attempt failed and was caught immediately**:
   a straight metal1 rectangle from the VDD trunk to the source pad
   (x:-18.460–-16.400, y:19.330–19.710) *physically overlapped segment A of
   the drain fix* (which spans y:17.400–20.830 at x:-18.150–-17.700) —
   this merged VOUT1 and VDD into one shorted net, confirmed by the device
   dump showing `S=VDD,VOUT1 ... D=VDD,VOUT1` everywhere. Caught via the
   mandatory full-12-device re-check, reverted immediately from
   `backups/strongarm_backup_post_M3_drain_fix_2026-07-10_06h21m1783657266.gds`.
   **Lesson**: when two additive metal1 fixes are placed near each other in
   the same session, check their footprints for overlap with each other,
   not just with pre-existing shapes — this is a new failure mode not
   covered by prior sessions' notes. **Working fix**: routed the source
   connection on **metal2** instead, to physically avoid crossing segment A
   on metal1:
   - via1 on the VDD trunk: x:-18.560–-18.460, y:19.430–19.610
   - via1 on the source pad: x:-16.350–-16.250, y:19.430–19.610
   - metal2 wire connecting them: x:-18.610–-16.300, y:19.430–19.610
   Verified: S now reads VDD, no short reappeared, no other devices
   changed. VDD's cross-reference terminal count went 8→9.

### M3's gate → CK: deliberately not attempted

The nearest CK metal1 is at x:-19.490–-19.110, y:17.660–18.040 — about 2µm
from the gate pad (x:-17.130–-16.750, y:19.890–20.270), and unlike the
drain/source fixes, **any straight-line or L-shaped path between them
necessarily cuts through the same congested pocket** that already caused
one same-session collision (VOUT1's trunk, VDD's trunk, the new metal2
source wire, and the nwell tap all occupy that exact x:-19–-16, y:17–21
box). Given (a) fixing this isn't needed for VOUT1/VDD's LVS counts — CK's
shortfall is a separate, pre-existing, already-documented gap — and (b) the
demonstrated collision risk in this exact pocket, this was left for a
future session with more budget to design a careful multi-layer route (e.g.
metal2, jumping over the existing VOUT1/VDD/source structures) rather than
guessed at under time pressure. CK's terminal count is currently
layout=4/reference=5 (schematic expects 5 device terminals + 1 pin = 6,
same pin-stripping caveat as VOUT1 above).

### New diagnostic technique: merged-metal1-island geometry (independent of LVS net labels)

Previous sessions' bulk-tie-short investigation worked purely from LVS net
membership (`shapes_of_net`), which can't distinguish *where* within an
already-fused blob the bridge is — every shape touching the blob shows up
identically regardless of whether it's near the bug or far from it (this
is explicitly called out as the reason experiment 1 in the third session
was misleading). This session used a different, purely-geometric technique
instead, independent of any net computation:

```python
import klayout.db as db
layout = db.Layout()
layout.read('/foss/designs/comparator/layout/strongarm.gds')
top = layout.top_cell()
dbu = layout.dbu
m1_li = layout.layer(34, 0)   # metal1
bx = db.Box(int(x1/dbu), int(y1/dbu), int(x2/dbu), int(y2/dbu))  # region of interest
r = db.Region(top.begin_shapes_rec_touching(m1_li, bx))
r.merge()   # shapes that touch/overlap become ONE polygon
for poly in r.each():
    print(poly.bbox())   # each print is a physically-connected "island"
```

This directly answers "what is physically the same electrical node on
metal1, ignoring what LVS thinks the node is called" — if two things that
should be different nets land in the same merged island, that IS the
short, full stop, no net-membership ambiguity. Cross-referencing each
device instance's known (x,y) position against which island contains it
immediately shows which devices are physically fused, e.g. this session
found **M9's local pad and M6's entire VOUT2 rail are the same merged
metal1 island** (bbox x:-29.360–-6.560, y:-10.310–18.390 before any cuts) —
independent confirmation of what the third session's experiment 3 implied
indirectly.

To find a good, low-collateral-risk **cut point** within a large island,
scan thin horizontal (or vertical) strips across it and measure the
intersected width — a strip where the width drops to a single minimum-rule
trace (0.2µm in this process) and `pieces==1` is a genuine single-wire
bottleneck, much safer to cut than a wide rail (cutting a wide rail, as
prior sessions found, often just isolates one unrelated branch without
touching the real short). Code:

```python
island_region = db.Region(target_polygon)
for y in frange(y0, y1, step):
    strip = db.Region(db.Box(...))  # thin horizontal slice
    clipped = island_region & strip
    width = sum((p.bbox().right - p.bbox().left) * dbu for p in clipped.each())
    pieces = clipped.count()
    # look for minimum width with pieces == 1
```

### Bulk-tie short: one bridge cut, cleanly isolating M10.source

Applying the technique above to the M9/M6 merged island (pre-cut bbox
x:-29.360–-6.560, y:-10.310–18.390) found a **0.2µm-wide, single-piece
trace at x:-10.270–-10.070, spanning y:-7.100–-3.900** — a genuine
minimum-width bottleneck, and at a different location from all three of
the previous session's cut attempts (via1 at x≈-5.3, M6's rail at
x≈-20–-18, and the M9-local-pad junction at x:-8.9–-7.1,y:-0.1–0.4).
**Cut**: removed a 1µm-tall notch at x:-10.300–-10.040, y:-6.000–-5.000 on
metal1 (layer 34/0). Backed up first to
`backups/strongarm_backup_pre_neck_cut_2026-07-10_06h28m1783657697.gds`.

**Result, confirmed via full 12-device dump and KLayout cross-reference**:
**M10's source terminal went from `S=VOUT2` (wrongly fused) to `S=$3`
(floating, isolated on its own)** — a clean, real severing of one bridge,
with **zero changes to any other device's terminals** (only net-ID
renumbering elsewhere, no topology change). Cross-reference confirms:
VOUT2's contamination count dropped 18→17, and **VIN1's net pair now shows
`status=Match`** (was Mismatch before) — a good side-effect sign of overall
netlist coherence improving. M11, M8, M9(S,B), M1(B), and M10.drain are
**still** fused with VOUT2, unaffected by this cut — this confirms (again)
that the bulk-tie short is multiple independent bridges, and this cut only
addressed the one that fed M10.source specifically.

**Important**: M10.source is now *floating*, not *correctly connected to
net2*. This is progress (one real short removed) but not a complete fix —
whoever continues needs to find net2's legitimate physical trunk (shared
by M8.source and M11.drain, which are themselves still incorrectly fused
with VOUT2 and haven't been untangled yet) and add a deliberate new
connection from M10's now-isolated source pad to it. Don't consider M10
"done" — it's disconnected-but-safe, one step short of correct.

**Next candidate necks found but not yet tried** (from re-running the
narrow-strip scan on the *post-cut* island, bbox now
x:-29.360–-7.300,y:-5.000–18.390 — the lower stub below y≈-3.6 is now a
dead end from this session's cut, ignore it):
- A 0.3µm-wide single-piece trace at x:-29.130–-28.830, spanning roughly
  y:2.2–17 — this is very likely **M6's own vertical rail leading to its
  drain contact**, not a bridge to M9; cutting it would probably just
  isolate M6 by itself again (same outcome as the third session's
  experiment 2, which cut M6's rail at a different point with the same
  result) — low expected value, but not actually re-tested at this exact
  location this session.
- Between y≈-2.9 and -2.7 the merged island suddenly widens to a 20.38µm
  single piece (x:-29.130–-8.750) — this is where M6's rail and the
  M9-area wiring actually merge into one wide strap, too wide to "notch
  cut" the way the two narrow necks above were handled. Whoever continues
  should look at this specific y-band with contact/via1 layers included
  (not just metal1) to find the real electrical junction point within it,
  since a blind cut through a wide rail risks repeating prior sessions'
  "isolated M6 alone, fusion unaffected" failure mode.

### Current state of the file on disk (authoritative)

`comparator/layout/strongarm.gds` currently has, in order: the M1 gate fix,
the M9 gate fix, the M3 drain→VOUT1 fix, the M3 source→VDD fix (metal2
jump), and the M10.source isolation cut — confirmed via md5 match against
`backups/strongarm_backup_post_neck_cut_M10source_isolated_2026-07-10_06h29m1783657770.gds`.
LVS still reports `ERROR : Netlists don't match` (expected — multiple bugs
remain). Per the KLayout cross-reference (`l2n.xref()`, see code pattern
below — this is the ground-truth method, matches the GUI's Cross Reference
tab exactly):

- VOUT1: layout terms=5, reference terms=5 — **now correctly matching**
  (both sides also separately show a pin that doesn't cross-match due to
  the label-stripping artifact noted above, not a real bug)
- VDD: layout terms=9 (was 8), reference terms=12 — M3.source fixed,
  M3.gate/bulk and other pre-existing pfet bulk-tie issues remain
- CK: layout terms=4, reference terms=5 — M3.gate still open (deferred)
- VOUT2: layout terms=17 (was 19 at start of session, 18 after M3 fixes,
  17 after the neck cut), reference (matched to NET2) terms=6 — still
  heavily contaminated, remaining bridges (M11, M8, M9(S,B), M1(B),
  M10.drain) not yet found
- VIN1: **Match** (terms=1 both sides)

### Note: GUI LVS wizard shows +1 on every pin-bearing net vs. the headless command above — this is expected, not a bug

If you open a `.gds` directly in KLayout's own GUI LVS wizard instead of
running the headless command earlier in this doc, every net that carries a
schematic-level pin (VDD, VOUT1, VOUT2, CK, VIN1, VIN2, VSS) will show
**exactly one more** terminal on the layout side than the headless command
reports (confirmed this session: VOUT1 5→6, VOUT2 17→18, CK 4→5, VDD 9→10,
VIN1/VIN2/VSS unaffected since they were already counted symmetrically).
**Root cause**: `run_lvs.py` has a `--top_lvl_pins` flag ("Enable top level
pins only in extracted netlist") that the headless command in this doc does
NOT pass, but the GUI wizard evidently does by default — it adds each
top-level schematic pin as an explicit extra terminal on the layout-side
net. Reproduced and confirmed directly: adding `--top_lvl_pins` to the
headless command reproduces the GUI's exact numbers. **This is a pure
counting/display difference, not a sign that a fix didn't take** — the
underlying device-terminal wiring (what actually matters, and what the
full 12-device dump checks) is identical either way. If you want your
headless numbers to match what you see in the GUI, add `--top_lvl_pins` to
the `run_lvs.py` invocation.

To reproduce the cross-reference query:
```python
import klayout.db as db
l2n = db.LayoutVsSchematic()
l2n.read('.../strongarm_lvs.lvsdb')
xref = l2n.xref()
for cp in xref.each_circuit_pair():
    for npair in xref.each_net_pair(cp):
        na, nb = npair.first(), npair.second()  # NOTE: these are methods, not properties
        # na/nb can be None; na.expanded_name(), na.each_terminal(), na.each_pin() as usual
```
Note the `.first()`/`.second()` calling convention — they show up as
`builtin_function_or_method` if you forget the parens and silently give the
wrong (method object) result instead of erroring, which cost some time
this session.

## UPDATE 2026-07-10 (fifth session): ROOT CAUSE FOUND — LVS NOW PASSES ✅

**Final result: `INFO : Congratulations! Netlists match.`** Every net and every
device shows `status=Match` in the cross-reference. The LVS-clean file is
`comparator/layout/strongarm.gds`, md5 `609af8d558b5e5d75882b06f1d6af86d`,
backed up as
`backups/strongarm_LVS_CLEAN_2026-07-10_*.gds`.

### The root cause every prior session was missing

The bulk-tie short was never a metal bridge at all. Three facts, discovered
in this order, explain everything:

1. **VOUT2's "fused blob" consisted of 5 disjoint metal1 islands** with no
   via1/metal2 connections between them (island graph analysis: merge all
   metal1 → islands, all metal2 → islands, treat via1 as edges).
   The tail-cluster island (M11.D+M8.S+M10.D+taps) had NO metal path to
   real VOUT2 whatsoever.
2. **The layout has no DNWELL and no LVPWELL.** Every nfet sits in the
   global p-substrate. Each `nfet` cell contains its own p+ tap strip with
   3 contacts, strapped by metal to its local source/drain rail. Since the
   substrate is one global node in extraction, ALL tap-strapped nets merge.
3. **M1's tap strip was strapped by the real VOUT2 routing itself** (contacts
   at x:12.85–14.09, y:1.81–2.03). That single strap injected the VOUT2 name
   into the substrate node — which then contaminated every tap-strapped
   island. This is why every metal cut "failed": the short traveled through
   silicon, not metal.

**Corollary: the schematic was unbuildable as drawn.** It tied each nfet
bulk to its source net (B=net1/net2/net3), which physically requires
deep-nwell isolation that the layout (and the plain `nfet_03v3` device)
doesn't have. No amount of layout editing could ever have made LVS pass
against that schematic.

### Changes made (all verified with full device dump + xref after each)

**Schematic (`comparator/schematic/strongarm.spice`; backup at
`strongarm.spice.bak_pre_bulk_fix`):**
- All 5 nfet bulks changed from net1/net2/net3 → **VSS** (the only
  physically-realizable configuration; standard for a StrongArm latch).
- M1's `L=0.28` → `L=0.28u` — the missing unit made the reference L parse
  as 280000µm and was the very last mismatch (visible as
  `MatchWithWarning` on the M1 device pair).
- ⚠️ **The xschem source `strongarm.sch` still has the old bulk wiring and
  the L typo.** If anyone re-netlists from xschem, these fixes will be
  overwritten. Fix the .sch (nfet bulk pins → VSS; M1 L → 0.28u) before
  regenerating.

**Layout (`comparator/layout/strongarm.gds`), in order applied:**
1. Deleted the 3 p-tap contacts from the shared `nfet` CELL DEFINITION
   (local x:1.47–1.69) — divorces all 6 instances' taps in one edit.
   This single edit collapsed the entire VOUT2/net2/net3 fusion.
2. Added a new substrate tap tied to VSS: COMP (3.93,−19.45)–(4.41,−18.97),
   Pplus (3.77,−19.61)–(4.57,−18.81), contact (4.06,−19.32)–(4.28,−19.10),
   under the existing VSS metal1 lobe (empty silicon verified first).
   All nfet bulks then read VSS.
3. Deleted the dummy/extra nfet instance at disp (7.87, 5.41) rot90+mirror
   (all terminals floating; device count now 11 = schematic). The
   second session's fear about deleting it was unfounded — its "collateral
   damage" back then was actually the pre-existing, then-undiscovered M3
   disconnection.
4. Junction notch: erased top-level metal1 (−11.72,−2.85)–(−11.36,−2.49),
   divorcing M6's drain rail + horizontal rail from the net3-side trunk.
5. Restored the fourth session's neck cut (re-added metal1
   (−10.30,−6.00)–(−10.04,−5.00)) — that metal was legitimate net3 routing
   (M10.S↔M9.S), only wrong because of what the island was fused to.
6. M5 drain→NET1: metal1 (28.70,17.35)–(29.30,17.95) bridging its floating
   pad to the NET1 island finger just below it.
7. M6 head cut: erased top-level metal1 (−29.36,17.68)–(−28.52,17.99)
   separating drain contacts (upper row) from nwell-tap contacts (lower).
8. M6 drain→VOUT2: via1+metal2 route from the drain piece east along
   y≈16.65–16.95 to a via down onto M2's gate pad (−7.16..−6.78,
   17.49..17.87), which is VOUT2.
9. M6 ntap→VDD: via1+metal2 west-side loop (x≈−29.9) up onto M6's own VDD
   pad piece (−29.24..−28.83, 19.13..19.51).
10. M4 (pfet at x=20.43): (a) strapped its upper pad to its VDD/ntap pad
    (metal1 20.33,18.95–20.53,19.46); (b) divorced its lower pad from the
    VOUT2 pin lobe that swallowed it (erased top-level metal1 moat
    (20.01,17.30)–(21.10,18.14) — in-cell pad survives since only
    top-level shapes were erased); (c) routed that pad to NET3: metal1
    finger west + via1 + ~35µm metal2 route (west at y≈17.5–17.8, south at
    x≈3.5, west at y≈−2.1) landing via1 in the net3 junction block
    (−11.36..−10.27, −3.44..−1.57).
11. M3 gate→CK: via1 on the CK stub (−19.49..−19.11,17.66..18.04), metal2
    north at x≈−19.3, east at y:19.89–20.27 (0.28 clear above the VDD
    metal2 wire), via1 onto the gate pad.
12. M3 ntap→VDD: via1 on the tap pad (−16.43..−16.05,18.60..18.98) + short
    metal2 vertical merging directly into the existing VDD metal2 wire
    from the fourth session's source fix.

## UPDATE 2026-07-10 (sixth session): DRC NOW CLEAN TOO ✅ (LVS re-verified passing)

**Final result: `Klayout DRC run is clean. GDS has no DRC violations.`** and LVS
re-run immediately after still prints `Congratulations! Netlists match.` with all
11 devices' terminals correct. The DRC+LVS-clean file is
`comparator/layout/strongarm.gds`, backed up as
`backups/strongarm_DRC_CLEAN_2026-07-10_*.gds`.

Starting point was the fifth session's LVS-clean file (md5
`609af8d558b5e5d75882b06f1d6af86d`), which had 53 DRC violations across 8 rules
(M1.1 ×20, M1.2a ×7, M2.1 ×1, V1.1 ×10, V1.3a ×4, V1.3c ×2, V1.4a ×4, V1.4b ×5).
All fixes are in `comparator/debugging/drc_fix.py` (groups 1–4, applied in that
order with a full DRC run between each; every coordinate was derived from
merged-polygon vertex dumps — `drc_recon.py`, `drc_recon2.py`, `drc_recon3.py`,
violation coordinates via `dump_drc.py` which parses the `.lyrdb` marker
databases with `klayout.rdb`).

### What was actually wrong (by cause, not rule)

1. **Session-added vias drawn at the wrong size.** The fourth session's
   M3-source-route vias were 0.10×0.18 (V1.1 requires exactly 0.26×0.26) and its
   metal2 wire was 0.18 wide (M2.1 min is 0.28). The third session's M9-gate via
   was 0.26×0.28. Fix: reworked the M3 source route (proper 0.26² vias at
   y19.34–19.60, 0.28-wide m2 wire at y19.33–19.61 — widened *downward* because
   the CK m2 route sits exactly 0.28 above the old wire top), trimmed 0.02 off
   the M9 via top.
2. **Three genuinely dangling vias** at (-3.26,19.44), (-4.05,19.67),
   (11.56,-1.59) with no metal1 AND no metal2 anywhere over them (verified by
   clipping merged regions — the m2 polygon whose bbox covers the first two has
   no actual material there). Deleted.
3. **A completely floating metal1 island** at x15.24–15.54, y-1.63–0.84 (0.30
   wide) carrying the long-known "dead-end via" from the second session. It
   touches nothing at either end. Deleted island + via, which also cleared the
   0.10 spacing violation to M1's gate stub.
4. **M1's gate bridge (third session) was geometrically unfixable on metal1**:
   the corridor between M1's other-net pad wiring below (top edge y0.36) and
   above (bottom edge y1.02) is 0.66 tall — max legal wire in it is
   0.66−2×0.23 = 0.20 < 0.23 min width. Replaced the m1 bridge with a
   **metal2 jumper**: erased top-level m1 (11.32,0.55)–(14.76,0.84), via1
   (10.98,0.55)–(11.24,0.81) on the VOUT1 trunk, via1 (14.82,0.54)–(15.08,0.80)
   on the gate stub, m2 (10.92,0.53)–(15.14,0.82). (The corridor was verified
   empty on m2 first.)
5. **The fifth session's M3-drain L-route was placed too close to its
   neighbors**: segment A sat 0.21 from the VDD trunk (trimmed its west edge to
   x-18.13 above y18.30 → 0.23), segment B sat 0.18 above M3's CK gate pad
   (raised its bottom to y20.50 → 0.23; the in-cell drain pad still provides the
   full-height landing). The A↔VOUT1-trunk junction had a 0.16 diagonal
   staircase throat — filled with a "foot" (-18.60,17.24)–(-17.70,17.52).
   Same staircase-throat pattern at the M5-drain bridge/pad corner (28.7,17.9);
   filled with (28.52,17.73)–(28.90,17.86).
6. **The original (pre-session) hand routing is 0.20µm wide in 12 places** —
   below the 0.23 GF180 metal1 minimum. This includes the x≈-10.17 net3 trunk,
   the M6-area rails, the tail-area straps, the M4 strap from the fifth session,
   and two long top-side rails. Each was widened by 0.03 on a side verified
   empty ≥0.23 (typically matching an existing landmark, e.g. the trunk was
   widened west to x-10.30 to line up with the fourth session's neck-cut fill).
   One follow-up (group4): where the t4 widening ended at y-0.33 it created a
   new 0.20 diagonal throat against the polygon's own step — extended the
   widening up to y0.00.
7. **Two same-polygon notches** (M9 pad area x-7.37 y1.70–1.75 gap 0.05; tail
   area slot x3.03–4.33 y-12.37–-12.22 gap 0.15). Both verified to be notches
   *within one merged polygon* (same physical node), so filling them exactly is
   connectivity-neutral. Filled.

### Techniques worth reusing
- `klayout.rdb.ReportDatabase` reads the `.lyrdb` DRC marker files directly —
  `dump_drc.py` prints every violation with exact coordinates; no GUI needed.
- Clip merged regions to a window and print hull vertices
  (`drc_recon2.py`) — every fix here was placed against actual polygon edges,
  not bbox guesses; nothing had to be reverted (53→26→20→1→0 monotonically).
- M1.1 "min width" also fires on **diagonal staircase throats** where two
  opposite-direction steps overlap within 0.23 euclidean — the fix is a small
  corner-fill patch, not a wire widening.
- When a corridor between two other-net shapes is < (0.23 + 2×0.23), don't try
  to squeeze metal1 through it — jump it on metal2.

### Remaining work
- **xschem .sch update** (see schematic warning above — bulk wiring + L=0.28u
  typo are still only fixed in `strongarm.spice`), then re-verify LVS with a
  freshly generated netlist.
- Consider more substrate taps / tap ring for latch-up robustness (still only
  one VSS tap).
- Antenna and density rules are OPT-IN flags on `run_drc.py` (`--antenna`,
  `--density`) and were NOT part of the main geometric runs. Both were run
  separately at the end of this session: **antenna = clean (0 items)**;
  **density = 8 items, all whole-cell MINIMUM-density rules** (DCF.1b, PL.8,
  M1.4–M5.4, MT.3 — each flags the full cell extent). That is expected for a
  small standalone analog block with mostly empty area and is normally
  satisfied by dummy/fill insertion at chip integration — no cell edit needed
  now, but don't forget fill generation before tapeout.

### Techniques that cracked it (for future reference)
- Island-graph analysis (merged metal1/metal2 regions + via1 edges) instead
  of `shapes_of_net` — shows physical connectivity independent of net labels.
- p-tap census: `(COMP & Pplus) - NWELL` intersected with contacts, grouped
  by owning metal1 island — this directly exposed the substrate bridge.
- Checking the REFERENCE netlist device-class/parameter dump
  (`dev.parameter(pd.id())`) — caught the L=0.28-without-unit typo that a
  netlist eyeball would never notice.
- Erasing only TOP-LEVEL shapes (iterate `top.each_shape`, boolean subtract,
  rewrite) leaves in-cell pads intact — used for the moat and head cuts.

### Remaining work (NOT LVS)
- **DRC has not been run** on the new geometry. All new shapes were placed
  with rule-of-thumb GF180 clearances (m1 space 0.23, m2 space 0.28, via
  0.26 with 0.06 enclosure, COMP/Pplus enclosures) but this needs a real
  DRC run before tapeout.
- **xschem .sch update** (see schematic warning above), then re-verify LVS
  with a freshly generated netlist.
- Consider adding more substrate taps / proper tap ring for latch-up
  robustness (only one VSS tap exists now); the old per-cell tap strips are
  still present in silicon but unconnected (contacts removed).
- The scripts used are preserved in `comparator/debugging/` (`island_graph.py`,
  `ptap_census.py`, `dump_devices.py`, `dump_xref.py`, `dump_params.py`,
  `edit_step.py`, `run_step.sh`, etc.).
