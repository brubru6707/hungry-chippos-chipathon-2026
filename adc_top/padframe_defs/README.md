# A13 padframe DEFs (rev received 2026-08-28)

Authoritative block spec from the Chipathon padframe generator, extracted from
`A13.def (2).tgz`. Two variants were generated for us; `A13_selected_variants.json`
lists both `BV` and `BH`, so we choose one.

`A13_selected_variants.json` also records what the generator read out of our GDS:
top cell `adc_top`, layer 0/0 rectangle `[30000, 500, 544250, 550200]` dbu =
**514.25 × 549.7 µm**, and our 14 top-level texts. That size matches no defined
block, which is why the audit sheet marks A13 `Size Check = FALSE`.

DEF units are **200 per micron**.

| | BV | BH |
| :--- | :--- | :--- |
| DIEAREA | `(0 0) (110000 222000)` = **550 × 1110 µm** | `(0 0) (222000 110000)` = **1110 × 550 µm** |
| Origin on die | 350, 1475 | 350, 2035 |
| West pins | VSS W12, VDD W13, CLK W14, RST_N W15, EOC W16, BIT_0 W17, BIT_1 W18, BIT_2 W19, BIT_3 W20, BIT_4 W21, BIT_5 W22 | VSS W18, VDD W19, CLK W20, RST_N W21, EOC W22 |
| North pins | BIT_6 N01, BIT_7 N02, VIN N03 | BIT_0–BIT_7 N01–N08, VIN N09 |

Pin geometry belongs on **Metal2**, 1 µm deep from the edge: west pins occupy
x 0–1 µm, north pins occupy the top 1 µm (y 1109–1110 for BV, y 549–550 for BH).
Routing blockage layers are Metal1–Metal5; usable area 610,500 µm².

## What our layout has to change

1. **Boundary.** The single layer 0/0 box must become exactly the chosen DIEAREA.
   Ours is 514.25 × 549.7 and sits at (30, 0.5)–(544.25, 550.2).
2. **Pin locations.** All 14 of our pin texts are currently on the SOUTH edge at
   y = 12 µm, x = 110–454. Neither variant has south pins — they must move to the
   west and north edges at the coordinates in the `translated_user` fields of
   `*_interface.yaml`.
3. **Pad control signals.** `*_padring.v` exposes every pad control as a port, so
   the block drives them; they are not tied off in the padring. Each `bi_t`
   bidirectional pad (EOC and the eight BIT pads) needs CS, SL, IE, OE, PU, PD,
   PDRV0, PDRV1 and A driven, with Y read back if we use the input direction. Our
   current top level has only the single `*_OUT` signal per pad.

## Choosing a variant

BH is the closer fit: our block is 549.7 µm tall against BH's 550 µm, so the height
is already right and the spare area is a 596 µm strip to the east. BV instead leaves
a 560 µm strip to the north and squeezes our 514.25 µm width into 550 µm.

Counting against BH: its 0.3 µm of vertical slack is very tight, and our geometry
currently reaches y = 550.2, which overhangs a 0–550 box by 0.2 µm, so everything
shifts down slightly. BH also needs nine north-edge pins spread to x = 890, well past
our current 544 µm right edge. BV needs eleven west-edge pins reaching y = 1076, well
above our 550 µm top. Either way the pin routing is new work.

The audit sheet currently lists us as slot type **BV**.
