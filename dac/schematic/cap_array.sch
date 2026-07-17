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
N 1930 -1260 2110 -1260 {lab=B0G}
N 2110 -1260 2180 -1260 {lab=B0G}
N 1860 -1420 1860 -1400 {lab=DAC_TOP}
C {dac/schematic/unit_switch.sym} 1880 -1270 0 0 {name=x_sw0 nfet_wid=0.42u nfet_len=0.28u}
C {symbols/cap_mim_2f0fF.sym} 1860 -1370 2 0 {name=C0
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=1}
C {gnd.sym} 1900 -1170 0 0 {name=lg0 lab=0}
N 1830 -1590 1830 -1570 {lab=VIN}
N 1860 -1590 1860 -1570 {lab=VREF}
N 1900 -1590 1900 -1570 {lab=0}
N 1860 -1740 1860 -1720 {lab=BOT1}
N 1930 -1640 1960 -1640 {lab=B1_B}
N 1960 -1640 1960 -1610 {lab=B1_B}
N 1930 -1680 2090 -1680 {lab=SAMPLE}
N 1930 -1660 2110 -1660 {lab=B1G}
N 2110 -1660 2180 -1660 {lab=B1G}
N 1860 -1820 1860 -1800 {lab=DAC_TOP}
C {dac/schematic/unit_switch.sym} 1880 -1670 0 0 {name=x_sw1 nfet_wid=0.84u nfet_len=0.28u}
C {symbols/cap_mim_2f0fF.sym} 1860 -1770 2 0 {name=C1
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=2}
C {gnd.sym} 1900 -1570 0 0 {name=lg1 lab=0}
N 1830 -1990 1830 -1970 {lab=VIN}
N 1860 -1990 1860 -1970 {lab=VREF}
N 1900 -1990 1900 -1970 {lab=0}
N 1860 -2140 1860 -2120 {lab=BOT2}
N 1930 -2040 1960 -2040 {lab=B2_B}
N 1960 -2040 1960 -2010 {lab=B2_B}
N 1930 -2080 2090 -2080 {lab=SAMPLE}
N 1930 -2060 2110 -2060 {lab=B2G}
N 2110 -2060 2180 -2060 {lab=B2G}
N 1860 -2220 1860 -2200 {lab=DAC_TOP}
C {dac/schematic/unit_switch.sym} 1880 -2070 0 0 {name=x_sw2 nfet_wid=1.68u nfet_len=0.28u}
C {symbols/cap_mim_2f0fF.sym} 1860 -2170 2 0 {name=C2
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=4}
C {gnd.sym} 1900 -1970 0 0 {name=lg2 lab=0}
N 1830 -2390 1830 -2370 {lab=VIN}
N 1860 -2390 1860 -2370 {lab=VREF}
N 1900 -2390 1900 -2370 {lab=0}
N 1860 -2540 1860 -2520 {lab=BOT3}
N 1930 -2440 1960 -2440 {lab=B3_B}
N 1960 -2440 1960 -2410 {lab=B3_B}
N 1930 -2480 2090 -2480 {lab=SAMPLE}
N 1930 -2460 2110 -2460 {lab=B3G}
N 2110 -2460 2180 -2460 {lab=B3G}
N 1860 -2620 1860 -2600 {lab=DAC_TOP}
C {dac/schematic/unit_switch.sym} 1880 -2470 0 0 {name=x_sw3 nfet_wid=3.36u nfet_len=0.28u}
C {symbols/cap_mim_2f0fF.sym} 1860 -2570 2 0 {name=C3
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=8}
C {gnd.sym} 1900 -2370 0 0 {name=lg3 lab=0}
N 1830 -2790 1830 -2770 {lab=VIN}
N 1860 -2790 1860 -2770 {lab=VREF}
N 1900 -2790 1900 -2770 {lab=0}
N 1860 -2940 1860 -2920 {lab=BOT4}
N 1930 -2840 1960 -2840 {lab=B4_B}
N 1960 -2840 1960 -2810 {lab=B4_B}
N 1930 -2880 2090 -2880 {lab=SAMPLE}
N 1930 -2860 2110 -2860 {lab=B4G}
N 2110 -2860 2180 -2860 {lab=B4G}
N 1860 -3020 1860 -3000 {lab=DAC_TOP}
C {dac/schematic/unit_switch.sym} 1880 -2870 0 0 {name=x_sw4 nfet_wid=6.72u nfet_len=0.28u}
C {symbols/cap_mim_2f0fF.sym} 1860 -2970 2 0 {name=C4
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=16}
C {gnd.sym} 1900 -2770 0 0 {name=lg4 lab=0}
N 1830 -3190 1830 -3170 {lab=VIN}
N 1860 -3190 1860 -3170 {lab=VREF}
N 1900 -3190 1900 -3170 {lab=0}
N 1860 -3340 1860 -3320 {lab=BOT5}
N 1930 -3240 1960 -3240 {lab=B5_B}
N 1960 -3240 1960 -3210 {lab=B5_B}
N 1930 -3280 2090 -3280 {lab=SAMPLE}
N 1930 -3260 2110 -3260 {lab=B5G}
N 2110 -3260 2180 -3260 {lab=B5G}
N 1860 -3420 1860 -3400 {lab=DAC_TOP}
C {dac/schematic/unit_switch.sym} 1880 -3270 0 0 {name=x_sw5 nfet_wid=13.44u nfet_len=0.28u}
C {symbols/cap_mim_2f0fF.sym} 1860 -3370 2 0 {name=C5
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=32}
C {gnd.sym} 1900 -3170 0 0 {name=lg5 lab=0}
N 1830 -3590 1830 -3570 {lab=VIN}
N 1860 -3590 1860 -3570 {lab=VREF}
N 1900 -3590 1900 -3570 {lab=0}
N 1860 -3740 1860 -3720 {lab=BOT6}
N 1930 -3640 1960 -3640 {lab=B6_B}
N 1960 -3640 1960 -3610 {lab=B6_B}
N 1930 -3680 2090 -3680 {lab=SAMPLE}
N 1930 -3660 2110 -3660 {lab=B6G}
N 2110 -3660 2180 -3660 {lab=B6G}
N 1860 -3820 1860 -3800 {lab=DAC_TOP}
C {dac/schematic/unit_switch.sym} 1880 -3670 0 0 {name=x_sw6 nfet_wid=26.88u nfet_len=0.28u}
C {symbols/cap_mim_2f0fF.sym} 1860 -3770 2 0 {name=C6
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=64}
C {gnd.sym} 1900 -3570 0 0 {name=lg6 lab=0}
N 1830 -3990 1830 -3970 {lab=VIN}
N 1860 -3990 1860 -3970 {lab=VREF}
N 1900 -3990 1900 -3970 {lab=0}
N 1860 -4140 1860 -4120 {lab=BOT7}
N 1930 -4040 1960 -4040 {lab=B7_B}
N 1960 -4040 1960 -4010 {lab=B7_B}
N 1930 -4080 2090 -4080 {lab=SAMPLE}
N 1930 -4060 2110 -4060 {lab=B7G}
N 2110 -4060 2180 -4060 {lab=B7G}
N 1860 -4220 1860 -4200 {lab=DAC_TOP}
C {dac/schematic/unit_switch.sym} 1880 -4070 0 0 {name=x_sw7 nfet_wid=53.76u nfet_len=0.28u}
C {symbols/cap_mim_2f0fF.sym} 1860 -4170 2 0 {name=C7
W=5e-6
L=5e-6
model=cap_mim_2f0fF
spiceprefix=X
m=128}
C {gnd.sym} 1900 -3970 0 0 {name=lg7 lab=0}
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
C {lab_wire.sym} 1830 -1170 0 0 {name=lw0_0 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 1860 -1170 0 0 {name=lw0_1 sig_type=std_logic lab=VREF}
C {lab_wire.sym} 1860 -1420 0 0 {name=lw0_2 sig_type=std_logic lab=DAC_TOP}
C {lab_wire.sym} 2090 -1280 0 0 {name=lw0_3 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2180 -1260 0 0 {name=lw0_4 sig_type=std_logic lab=B0G}
C {lab_wire.sym} 1960 -1210 0 0 {name=lw0_6 sig_type=std_logic lab=B0_B}
C {lab_wire.sym} 1830 -1570 0 0 {name=lw1_0 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 1860 -1570 0 0 {name=lw1_1 sig_type=std_logic lab=VREF}
C {lab_wire.sym} 1860 -1820 0 0 {name=lw1_2 sig_type=std_logic lab=DAC_TOP}
C {lab_wire.sym} 2090 -1680 0 0 {name=lw1_3 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2180 -1660 0 0 {name=lw1_4 sig_type=std_logic lab=B1G}
C {lab_wire.sym} 1960 -1610 0 0 {name=lw1_6 sig_type=std_logic lab=B1_B}
C {lab_wire.sym} 1830 -1970 0 0 {name=lw2_0 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 1860 -1970 0 0 {name=lw2_1 sig_type=std_logic lab=VREF}
C {lab_wire.sym} 1860 -2220 0 0 {name=lw2_2 sig_type=std_logic lab=DAC_TOP}
C {lab_wire.sym} 2090 -2080 0 0 {name=lw2_3 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2180 -2060 0 0 {name=lw2_4 sig_type=std_logic lab=B2G}
C {lab_wire.sym} 1960 -2010 0 0 {name=lw2_6 sig_type=std_logic lab=B2_B}
C {lab_wire.sym} 1830 -2370 0 0 {name=lw3_0 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 1860 -2370 0 0 {name=lw3_1 sig_type=std_logic lab=VREF}
C {lab_wire.sym} 1860 -2620 0 0 {name=lw3_2 sig_type=std_logic lab=DAC_TOP}
C {lab_wire.sym} 2090 -2480 0 0 {name=lw3_3 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2180 -2460 0 0 {name=lw3_4 sig_type=std_logic lab=B3G}
C {lab_wire.sym} 1960 -2410 0 0 {name=lw3_6 sig_type=std_logic lab=B3_B}
C {lab_wire.sym} 1830 -2770 0 0 {name=lw4_0 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 1860 -2770 0 0 {name=lw4_1 sig_type=std_logic lab=VREF}
C {lab_wire.sym} 1860 -3020 0 0 {name=lw4_2 sig_type=std_logic lab=DAC_TOP}
C {lab_wire.sym} 2090 -2880 0 0 {name=lw4_3 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2180 -2860 0 0 {name=lw4_4 sig_type=std_logic lab=B4G}
C {lab_wire.sym} 1960 -2810 0 0 {name=lw4_6 sig_type=std_logic lab=B4_B}
C {lab_wire.sym} 1830 -3170 0 0 {name=lw5_0 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 1860 -3170 0 0 {name=lw5_1 sig_type=std_logic lab=VREF}
C {lab_wire.sym} 1860 -3420 0 0 {name=lw5_2 sig_type=std_logic lab=DAC_TOP}
C {lab_wire.sym} 2090 -3280 0 0 {name=lw5_3 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2180 -3260 0 0 {name=lw5_4 sig_type=std_logic lab=B5G}
C {lab_wire.sym} 1960 -3210 0 0 {name=lw5_6 sig_type=std_logic lab=B5_B}
C {lab_wire.sym} 1830 -3570 0 0 {name=lw6_0 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 1860 -3570 0 0 {name=lw6_1 sig_type=std_logic lab=VREF}
C {lab_wire.sym} 1860 -3820 0 0 {name=lw6_2 sig_type=std_logic lab=DAC_TOP}
C {lab_wire.sym} 2090 -3680 0 0 {name=lw6_3 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2180 -3660 0 0 {name=lw6_4 sig_type=std_logic lab=B6G}
C {lab_wire.sym} 1960 -3610 0 0 {name=lw6_6 sig_type=std_logic lab=B6_B}
C {lab_wire.sym} 1830 -3970 0 0 {name=lw7_0 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 1860 -3970 0 0 {name=lw7_1 sig_type=std_logic lab=VREF}
C {lab_wire.sym} 1860 -4220 0 0 {name=lw7_2 sig_type=std_logic lab=DAC_TOP}
C {lab_wire.sym} 2090 -4080 0 0 {name=lw7_3 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2180 -4060 0 0 {name=lw7_4 sig_type=std_logic lab=B7G}
C {lab_wire.sym} 1960 -4010 0 0 {name=lw7_6 sig_type=std_logic lab=B7_B}
N 1500 -1270 1560 -1270 {lab=VIN}
C {lab_wire.sym} 1560 -1270 0 0 {name=lwp0 sig_type=std_logic lab=VIN}
N 1500 -1170 1560 -1170 {lab=VREF}
C {lab_wire.sym} 1560 -1170 0 0 {name=lwp1 sig_type=std_logic lab=VREF}
N 1500 -1070 1560 -1070 {lab=VDD}
C {lab_wire.sym} 1560 -1070 0 0 {name=lwp2 sig_type=std_logic lab=VDD}
N 1500 -970 1560 -970 {lab=SAMPLE}
C {lab_wire.sym} 1560 -970 0 0 {name=lwp3 sig_type=std_logic lab=SAMPLE}
N 1500 -870 1560 -870 {lab=B0}
C {lab_wire.sym} 1560 -870 0 0 {name=lwp4 sig_type=std_logic lab=B0}
N 1500 -770 1560 -770 {lab=B1}
C {lab_wire.sym} 1560 -770 0 0 {name=lwp5 sig_type=std_logic lab=B1}
N 1500 -670 1560 -670 {lab=B2}
C {lab_wire.sym} 1560 -670 0 0 {name=lwp6 sig_type=std_logic lab=B2}
N 1500 -570 1560 -570 {lab=B3}
C {lab_wire.sym} 1560 -570 0 0 {name=lwp7 sig_type=std_logic lab=B3}
N 1500 -470 1560 -470 {lab=B4}
C {lab_wire.sym} 1560 -470 0 0 {name=lwp8 sig_type=std_logic lab=B4}
N 1500 -370 1560 -370 {lab=B5}
C {lab_wire.sym} 1560 -370 0 0 {name=lwp9 sig_type=std_logic lab=B5}
N 1500 -270 1560 -270 {lab=B6}
C {lab_wire.sym} 1560 -270 0 0 {name=lwp10 sig_type=std_logic lab=B6}
N 1500 -170 1560 -170 {lab=B7}
C {lab_wire.sym} 1560 -170 0 0 {name=lwp11 sig_type=std_logic lab=B7}
N 1500 -70 1560 -70 {lab=DAC_TOP}
C {lab_wire.sym} 1560 -70 0 0 {name=lwp12 sig_type=std_logic lab=DAC_TOP}
C {dac/schematic/nor2.sym} 2500 -1270 0 0 {name=x_nor0}
C {lab_wire.sym} 2400 -1270 0 0 {name=ln0_a sig_type=std_logic lab=B0}
C {lab_wire.sym} 2400 -1230 0 0 {name=ln0_b sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2540 -1250 0 0 {name=ln0_y sig_type=std_logic lab=B0_B}
C {lab_wire.sym} 2460 -1310 0 0 {name=ln0_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2460 -1190 0 0 {name=gnor0 lab=0}
C {dac/schematic/nand2.sym} 2700 -1270 0 0 {name=x_nand0}
C {lab_wire.sym} 2600 -1270 0 0 {name=lnd0_a sig_type=std_logic lab=B0}
C {lab_wire.sym} 2600 -1230 0 0 {name=lnd0_b sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 2740 -1250 0 0 {name=lnd0_y sig_type=std_logic lab=B0NAND}
C {lab_wire.sym} 2660 -1310 0 0 {name=lnd0_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2660 -1190 0 0 {name=gnand0 lab=0}
C {dac/schematic/inv1.sym} 2900 -1270 0 0 {name=x_andinv0}
C {lab_wire.sym} 2800 -1270 0 0 {name=lai0_vin sig_type=std_logic lab=B0NAND}
C {lab_wire.sym} 2930 -1270 0 0 {name=lai0_vout sig_type=std_logic lab=B0G}
C {lab_wire.sym} 2830 -1340 0 0 {name=lai0_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2830 -1210 0 0 {name=gandinv0 lab=0}
C {dac/schematic/nor2.sym} 2500 -1670 0 0 {name=x_nor1}
C {lab_wire.sym} 2400 -1670 0 0 {name=ln1_a sig_type=std_logic lab=B1}
C {lab_wire.sym} 2400 -1630 0 0 {name=ln1_b sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2540 -1650 0 0 {name=ln1_y sig_type=std_logic lab=B1_B}
C {lab_wire.sym} 2460 -1710 0 0 {name=ln1_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2460 -1590 0 0 {name=gnor1 lab=0}
C {dac/schematic/nand2.sym} 2700 -1670 0 0 {name=x_nand1}
C {lab_wire.sym} 2600 -1670 0 0 {name=lnd1_a sig_type=std_logic lab=B1}
C {lab_wire.sym} 2600 -1630 0 0 {name=lnd1_b sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 2740 -1650 0 0 {name=lnd1_y sig_type=std_logic lab=B1NAND}
C {lab_wire.sym} 2660 -1710 0 0 {name=lnd1_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2660 -1590 0 0 {name=gnand1 lab=0}
C {dac/schematic/inv1.sym} 2900 -1670 0 0 {name=x_andinv1}
C {lab_wire.sym} 2800 -1670 0 0 {name=lai1_vin sig_type=std_logic lab=B1NAND}
C {lab_wire.sym} 2930 -1670 0 0 {name=lai1_vout sig_type=std_logic lab=B1G}
C {lab_wire.sym} 2830 -1740 0 0 {name=lai1_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2830 -1610 0 0 {name=gandinv1 lab=0}
C {dac/schematic/nor2.sym} 2500 -2070 0 0 {name=x_nor2}
C {lab_wire.sym} 2400 -2070 0 0 {name=ln2_a sig_type=std_logic lab=B2}
C {lab_wire.sym} 2400 -2030 0 0 {name=ln2_b sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2540 -2050 0 0 {name=ln2_y sig_type=std_logic lab=B2_B}
C {lab_wire.sym} 2460 -2110 0 0 {name=ln2_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2460 -1990 0 0 {name=gnor2 lab=0}
C {dac/schematic/nand2.sym} 2700 -2070 0 0 {name=x_nand2}
C {lab_wire.sym} 2600 -2070 0 0 {name=lnd2_a sig_type=std_logic lab=B2}
C {lab_wire.sym} 2600 -2030 0 0 {name=lnd2_b sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 2740 -2050 0 0 {name=lnd2_y sig_type=std_logic lab=B2NAND}
C {lab_wire.sym} 2660 -2110 0 0 {name=lnd2_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2660 -1990 0 0 {name=gnand2 lab=0}
C {dac/schematic/inv1.sym} 2900 -2070 0 0 {name=x_andinv2}
C {lab_wire.sym} 2800 -2070 0 0 {name=lai2_vin sig_type=std_logic lab=B2NAND}
C {lab_wire.sym} 2930 -2070 0 0 {name=lai2_vout sig_type=std_logic lab=B2G}
C {lab_wire.sym} 2830 -2140 0 0 {name=lai2_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2830 -2010 0 0 {name=gandinv2 lab=0}
C {dac/schematic/nor2.sym} 2500 -2470 0 0 {name=x_nor3}
C {lab_wire.sym} 2400 -2470 0 0 {name=ln3_a sig_type=std_logic lab=B3}
C {lab_wire.sym} 2400 -2430 0 0 {name=ln3_b sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2540 -2450 0 0 {name=ln3_y sig_type=std_logic lab=B3_B}
C {lab_wire.sym} 2460 -2510 0 0 {name=ln3_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2460 -2390 0 0 {name=gnor3 lab=0}
C {dac/schematic/nand2.sym} 2700 -2470 0 0 {name=x_nand3}
C {lab_wire.sym} 2600 -2470 0 0 {name=lnd3_a sig_type=std_logic lab=B3}
C {lab_wire.sym} 2600 -2430 0 0 {name=lnd3_b sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 2740 -2450 0 0 {name=lnd3_y sig_type=std_logic lab=B3NAND}
C {lab_wire.sym} 2660 -2510 0 0 {name=lnd3_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2660 -2390 0 0 {name=gnand3 lab=0}
C {dac/schematic/inv1.sym} 2900 -2470 0 0 {name=x_andinv3}
C {lab_wire.sym} 2800 -2470 0 0 {name=lai3_vin sig_type=std_logic lab=B3NAND}
C {lab_wire.sym} 2930 -2470 0 0 {name=lai3_vout sig_type=std_logic lab=B3G}
C {lab_wire.sym} 2830 -2540 0 0 {name=lai3_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2830 -2410 0 0 {name=gandinv3 lab=0}
C {dac/schematic/nor2.sym} 2500 -2870 0 0 {name=x_nor4}
C {lab_wire.sym} 2400 -2870 0 0 {name=ln4_a sig_type=std_logic lab=B4}
C {lab_wire.sym} 2400 -2830 0 0 {name=ln4_b sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2540 -2850 0 0 {name=ln4_y sig_type=std_logic lab=B4_B}
C {lab_wire.sym} 2460 -2910 0 0 {name=ln4_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2460 -2790 0 0 {name=gnor4 lab=0}
C {dac/schematic/nand2.sym} 2700 -2870 0 0 {name=x_nand4}
C {lab_wire.sym} 2600 -2870 0 0 {name=lnd4_a sig_type=std_logic lab=B4}
C {lab_wire.sym} 2600 -2830 0 0 {name=lnd4_b sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 2740 -2850 0 0 {name=lnd4_y sig_type=std_logic lab=B4NAND}
C {lab_wire.sym} 2660 -2910 0 0 {name=lnd4_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2660 -2790 0 0 {name=gnand4 lab=0}
C {dac/schematic/inv1.sym} 2900 -2870 0 0 {name=x_andinv4}
C {lab_wire.sym} 2800 -2870 0 0 {name=lai4_vin sig_type=std_logic lab=B4NAND}
C {lab_wire.sym} 2930 -2870 0 0 {name=lai4_vout sig_type=std_logic lab=B4G}
C {lab_wire.sym} 2830 -2940 0 0 {name=lai4_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2830 -2810 0 0 {name=gandinv4 lab=0}
C {dac/schematic/nor2.sym} 2500 -3270 0 0 {name=x_nor5}
C {lab_wire.sym} 2400 -3270 0 0 {name=ln5_a sig_type=std_logic lab=B5}
C {lab_wire.sym} 2400 -3230 0 0 {name=ln5_b sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2540 -3250 0 0 {name=ln5_y sig_type=std_logic lab=B5_B}
C {lab_wire.sym} 2460 -3310 0 0 {name=ln5_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2460 -3190 0 0 {name=gnor5 lab=0}
C {dac/schematic/nand2.sym} 2700 -3270 0 0 {name=x_nand5}
C {lab_wire.sym} 2600 -3270 0 0 {name=lnd5_a sig_type=std_logic lab=B5}
C {lab_wire.sym} 2600 -3230 0 0 {name=lnd5_b sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 2740 -3250 0 0 {name=lnd5_y sig_type=std_logic lab=B5NAND}
C {lab_wire.sym} 2660 -3310 0 0 {name=lnd5_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2660 -3190 0 0 {name=gnand5 lab=0}
C {dac/schematic/inv1.sym} 2900 -3270 0 0 {name=x_andinv5}
C {lab_wire.sym} 2800 -3270 0 0 {name=lai5_vin sig_type=std_logic lab=B5NAND}
C {lab_wire.sym} 2930 -3270 0 0 {name=lai5_vout sig_type=std_logic lab=B5G}
C {lab_wire.sym} 2830 -3340 0 0 {name=lai5_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2830 -3210 0 0 {name=gandinv5 lab=0}
C {dac/schematic/nor2.sym} 2500 -3670 0 0 {name=x_nor6}
C {lab_wire.sym} 2400 -3670 0 0 {name=ln6_a sig_type=std_logic lab=B6}
C {lab_wire.sym} 2400 -3630 0 0 {name=ln6_b sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2540 -3650 0 0 {name=ln6_y sig_type=std_logic lab=B6_B}
C {lab_wire.sym} 2460 -3710 0 0 {name=ln6_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2460 -3590 0 0 {name=gnor6 lab=0}
C {dac/schematic/nand2.sym} 2700 -3670 0 0 {name=x_nand6}
C {lab_wire.sym} 2600 -3670 0 0 {name=lnd6_a sig_type=std_logic lab=B6}
C {lab_wire.sym} 2600 -3630 0 0 {name=lnd6_b sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 2740 -3650 0 0 {name=lnd6_y sig_type=std_logic lab=B6NAND}
C {lab_wire.sym} 2660 -3710 0 0 {name=lnd6_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2660 -3590 0 0 {name=gnand6 lab=0}
C {dac/schematic/inv1.sym} 2900 -3670 0 0 {name=x_andinv6}
C {lab_wire.sym} 2800 -3670 0 0 {name=lai6_vin sig_type=std_logic lab=B6NAND}
C {lab_wire.sym} 2930 -3670 0 0 {name=lai6_vout sig_type=std_logic lab=B6G}
C {lab_wire.sym} 2830 -3740 0 0 {name=lai6_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2830 -3610 0 0 {name=gandinv6 lab=0}
C {dac/schematic/nor2.sym} 2500 -4070 0 0 {name=x_nor7}
C {lab_wire.sym} 2400 -4070 0 0 {name=ln7_a sig_type=std_logic lab=B7}
C {lab_wire.sym} 2400 -4030 0 0 {name=ln7_b sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 2540 -4050 0 0 {name=ln7_y sig_type=std_logic lab=B7_B}
C {lab_wire.sym} 2460 -4110 0 0 {name=ln7_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2460 -3990 0 0 {name=gnor7 lab=0}
C {dac/schematic/nand2.sym} 2700 -4070 0 0 {name=x_nand7}
C {lab_wire.sym} 2600 -4070 0 0 {name=lnd7_a sig_type=std_logic lab=B7}
C {lab_wire.sym} 2600 -4030 0 0 {name=lnd7_b sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 2740 -4050 0 0 {name=lnd7_y sig_type=std_logic lab=B7NAND}
C {lab_wire.sym} 2660 -4110 0 0 {name=lnd7_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2660 -3990 0 0 {name=gnand7 lab=0}
C {dac/schematic/inv1.sym} 2900 -4070 0 0 {name=x_andinv7}
C {lab_wire.sym} 2800 -4070 0 0 {name=lai7_vin sig_type=std_logic lab=B7NAND}
C {lab_wire.sym} 2930 -4070 0 0 {name=lai7_vout sig_type=std_logic lab=B7G}
C {lab_wire.sym} 2830 -4140 0 0 {name=lai7_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 2830 -4010 0 0 {name=gandinv7 lab=0}
C {dac/schematic/inv1.sym} 1700 -40 0 0 {name=x_sampinv}
C {lab_wire.sym} 1600 -40 0 0 {name=lsampinv_vin sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 1730 -40 0 0 {name=lsampinv_vout sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 1630 -110 0 0 {name=lsampinv_vdd sig_type=std_logic lab=VDD}
C {gnd.sym} 1630 20 0 0 {name=gsampinv lab=0}
