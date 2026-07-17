v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Binary-weighted 8-bit charge-redistribution cap array (DAC-1/DAC-2).
Bottom-plate switching: each bit's unit_switch (Max, ported from origin/max)
ties its bottom plate (BOTn) to VIN during SAMPLE, and to VREF or GND during
the conversion trial based on Bn. All 8 top plates share one node, DAC_TOP,
which is the common summing node read by the comparator.
Weights: bit0=1x .. bit7=128x Cu, Cu=50fF (5um x 5um at cap_mim_2f0fF density).
Switch is left at unit size for all bits (first-pass simplification -
MSB switch is relatively undersized vs its cap; revisit if Gate 2 settling fails).
Ported/authored outside Xschem - open, visually check, and netlist/simulate
before trusting this for Gate 2.} 1450 -2200 0 0 0.25 0.25 {}
N 1830 -1190 1830 -1170 {lab=VIN}
N 1860 -1190 1860 -1170 {lab=VREF}
N 1900 -1190 1900 -1170 {lab=0}
N 1860 -1340 1860 -1320 {lab=BOT0}
N 1930 -1240 1960 -1240 {lab=B0_B}
N 1960 -1240 1960 -1210 {lab=B0_B}
N 1930 -1280 2090 -1280 {lab=SAMPLE}
N 1930 -1260 2110 -1260 {lab=B0}
N 2110 -1260 2180 -1260 {lab=B0}
N 1860 -1420 1860 -1400 {lab=DAC_TOP}
N 2200 -1270 2170 -1270 {lab=B0}
N 2330 -1270 2360 -1270 {lab=B0_B}
N 2230 -1340 2230 -1360 {lab=VDD}
N 2230 -1210 2230 -1190 {lab=0}
C {dac/schematic/unit_switch.sym} 1880 -1270 0 0 {name=x_sw0}
C {symbols/cap_mim_2f0fF.sym} 1860 -1370 2 0 {name=C0
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=1}
C {gnd.sym} 1900 -1170 0 0 {name=lg0 lab=0}
C {dac/schematic/inv1.sym} 2300 -1270 0 0 {name=x_inv0}
N 1830 -1590 1830 -1570 {lab=VIN}
N 1860 -1590 1860 -1570 {lab=VREF}
N 1900 -1590 1900 -1570 {lab=0}
N 1860 -1740 1860 -1720 {lab=BOT1}
N 1930 -1640 1960 -1640 {lab=B1_B}
N 1960 -1640 1960 -1610 {lab=B1_B}
N 1930 -1680 2090 -1680 {lab=SAMPLE}
N 1930 -1660 2110 -1660 {lab=B1}
N 2110 -1660 2180 -1660 {lab=B1}
N 1860 -1820 1860 -1800 {lab=DAC_TOP}
N 2200 -1670 2170 -1670 {lab=B1}
N 2330 -1670 2360 -1670 {lab=B1_B}
N 2230 -1740 2230 -1760 {lab=VDD}
N 2230 -1610 2230 -1590 {lab=0}
C {dac/schematic/unit_switch.sym} 1880 -1670 0 0 {name=x_sw1}
C {symbols/cap_mim_2f0fF.sym} 1860 -1770 2 0 {name=C1
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=2}
C {gnd.sym} 1900 -1570 0 0 {name=lg1 lab=0}
C {dac/schematic/inv1.sym} 2300 -1670 0 0 {name=x_inv1}
N 1830 -1990 1830 -1970 {lab=VIN}
N 1860 -1990 1860 -1970 {lab=VREF}
N 1900 -1990 1900 -1970 {lab=0}
N 1860 -2140 1860 -2120 {lab=BOT2}
N 1930 -2040 1960 -2040 {lab=B2_B}
N 1960 -2040 1960 -2010 {lab=B2_B}
N 1930 -2080 2090 -2080 {lab=SAMPLE}
N 1930 -2060 2110 -2060 {lab=B2}
N 2110 -2060 2180 -2060 {lab=B2}
N 1860 -2220 1860 -2200 {lab=DAC_TOP}
N 2200 -2070 2170 -2070 {lab=B2}
N 2330 -2070 2360 -2070 {lab=B2_B}
N 2230 -2140 2230 -2160 {lab=VDD}
N 2230 -2010 2230 -1990 {lab=0}
C {dac/schematic/unit_switch.sym} 1880 -2070 0 0 {name=x_sw2}
C {symbols/cap_mim_2f0fF.sym} 1860 -2170 2 0 {name=C2
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=4}
C {gnd.sym} 1900 -1970 0 0 {name=lg2 lab=0}
C {dac/schematic/inv1.sym} 2300 -2070 0 0 {name=x_inv2}
N 1830 -2390 1830 -2370 {lab=VIN}
N 1860 -2390 1860 -2370 {lab=VREF}
N 1900 -2390 1900 -2370 {lab=0}
N 1860 -2540 1860 -2520 {lab=BOT3}
N 1930 -2440 1960 -2440 {lab=B3_B}
N 1960 -2440 1960 -2410 {lab=B3_B}
N 1930 -2480 2090 -2480 {lab=SAMPLE}
N 1930 -2460 2110 -2460 {lab=B3}
N 2110 -2460 2180 -2460 {lab=B3}
N 1860 -2620 1860 -2600 {lab=DAC_TOP}
N 2200 -2470 2170 -2470 {lab=B3}
N 2330 -2470 2360 -2470 {lab=B3_B}
N 2230 -2540 2230 -2560 {lab=VDD}
N 2230 -2410 2230 -2390 {lab=0}
C {dac/schematic/unit_switch.sym} 1880 -2470 0 0 {name=x_sw3}
C {symbols/cap_mim_2f0fF.sym} 1860 -2570 2 0 {name=C3
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=8}
C {gnd.sym} 1900 -2370 0 0 {name=lg3 lab=0}
C {dac/schematic/inv1.sym} 2300 -2470 0 0 {name=x_inv3}
N 1830 -2790 1830 -2770 {lab=VIN}
N 1860 -2790 1860 -2770 {lab=VREF}
N 1900 -2790 1900 -2770 {lab=0}
N 1860 -2940 1860 -2920 {lab=BOT4}
N 1930 -2840 1960 -2840 {lab=B4_B}
N 1960 -2840 1960 -2810 {lab=B4_B}
N 1930 -2880 2090 -2880 {lab=SAMPLE}
N 1930 -2860 2110 -2860 {lab=B4}
N 2110 -2860 2180 -2860 {lab=B4}
N 1860 -3020 1860 -3000 {lab=DAC_TOP}
N 2200 -2870 2170 -2870 {lab=B4}
N 2330 -2870 2360 -2870 {lab=B4_B}
N 2230 -2940 2230 -2960 {lab=VDD}
N 2230 -2810 2230 -2790 {lab=0}
C {dac/schematic/unit_switch.sym} 1880 -2870 0 0 {name=x_sw4}
C {symbols/cap_mim_2f0fF.sym} 1860 -2970 2 0 {name=C4
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=16}
C {gnd.sym} 1900 -2770 0 0 {name=lg4 lab=0}
C {dac/schematic/inv1.sym} 2300 -2870 0 0 {name=x_inv4}
N 1830 -3190 1830 -3170 {lab=VIN}
N 1860 -3190 1860 -3170 {lab=VREF}
N 1900 -3190 1900 -3170 {lab=0}
N 1860 -3340 1860 -3320 {lab=BOT5}
N 1930 -3240 1960 -3240 {lab=B5_B}
N 1960 -3240 1960 -3210 {lab=B5_B}
N 1930 -3280 2090 -3280 {lab=SAMPLE}
N 1930 -3260 2110 -3260 {lab=B5}
N 2110 -3260 2180 -3260 {lab=B5}
N 1860 -3420 1860 -3400 {lab=DAC_TOP}
N 2200 -3270 2170 -3270 {lab=B5}
N 2330 -3270 2360 -3270 {lab=B5_B}
N 2230 -3340 2230 -3360 {lab=VDD}
N 2230 -3210 2230 -3190 {lab=0}
C {dac/schematic/unit_switch.sym} 1880 -3270 0 0 {name=x_sw5}
C {symbols/cap_mim_2f0fF.sym} 1860 -3370 2 0 {name=C5
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=32}
C {gnd.sym} 1900 -3170 0 0 {name=lg5 lab=0}
C {dac/schematic/inv1.sym} 2300 -3270 0 0 {name=x_inv5}
N 1830 -3590 1830 -3570 {lab=VIN}
N 1860 -3590 1860 -3570 {lab=VREF}
N 1900 -3590 1900 -3570 {lab=0}
N 1860 -3740 1860 -3720 {lab=BOT6}
N 1930 -3640 1960 -3640 {lab=B6_B}
N 1960 -3640 1960 -3610 {lab=B6_B}
N 1930 -3680 2090 -3680 {lab=SAMPLE}
N 1930 -3660 2110 -3660 {lab=B6}
N 2110 -3660 2180 -3660 {lab=B6}
N 1860 -3820 1860 -3800 {lab=DAC_TOP}
N 2200 -3670 2170 -3670 {lab=B6}
N 2330 -3670 2360 -3670 {lab=B6_B}
N 2230 -3740 2230 -3760 {lab=VDD}
N 2230 -3610 2230 -3590 {lab=0}
C {dac/schematic/unit_switch.sym} 1880 -3670 0 0 {name=x_sw6}
C {symbols/cap_mim_2f0fF.sym} 1860 -3770 2 0 {name=C6
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=64}
C {gnd.sym} 1900 -3570 0 0 {name=lg6 lab=0}
C {dac/schematic/inv1.sym} 2300 -3670 0 0 {name=x_inv6}
N 1830 -3990 1830 -3970 {lab=VIN}
N 1860 -3990 1860 -3970 {lab=VREF}
N 1900 -3990 1900 -3970 {lab=0}
N 1860 -4140 1860 -4120 {lab=BOT7}
N 1930 -4040 1960 -4040 {lab=B7_B}
N 1960 -4040 1960 -4010 {lab=B7_B}
N 1930 -4080 2090 -4080 {lab=SAMPLE}
N 1930 -4060 2110 -4060 {lab=B7}
N 2110 -4060 2180 -4060 {lab=B7}
N 1860 -4220 1860 -4200 {lab=DAC_TOP}
N 2200 -4070 2170 -4070 {lab=B7}
N 2330 -4070 2360 -4070 {lab=B7_B}
N 2230 -4140 2230 -4160 {lab=VDD}
N 2230 -4010 2230 -3990 {lab=0}
C {dac/schematic/unit_switch.sym} 1880 -4070 0 0 {name=x_sw7}
C {symbols/cap_mim_2f0fF.sym} 1860 -4170 2 0 {name=C7
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=128}
C {gnd.sym} 1900 -3970 0 0 {name=lg7 lab=0}
C {dac/schematic/inv1.sym} 2300 -4070 0 0 {name=x_inv7}
C {ipin.sym} 1500 -1270 0 0 {name=pVIN lab=VIN}
C {ipin.sym} 1500 -1170 0 0 {name=pVREF lab=VREF}
C {ipin.sym} 1500 -1070 0 0 {name=pVDD lab=VDD}
C {ipin.sym} 1500 -970 0 0 {name=pSAMPLE lab=SAMPLE}
C {ipin.sym} 1500 -870 0 0 {name=pB0 lab=B0}
C {ipin.sym} 1500 -770 0 0 {name=pB1 lab=B1}
C {ipin.sym} 1500 -670 0 0 {name=pB2 lab=B2}
C {ipin.sym} 1500 -570 0 0 {name=pB3 lab=B3}
C {ipin.sym} 1500 -470 0 0 {name=pB4 lab=B4}
C {ipin.sym} 1500 -370 0 0 {name=pB5 lab=B5}
C {ipin.sym} 1500 -270 0 0 {name=pB6 lab=B6}
C {ipin.sym} 1500 -170 0 0 {name=pB7 lab=B7}
C {opin.sym} 1500 -70 0 0 {name=pDACTOP lab=DAC_TOP}
