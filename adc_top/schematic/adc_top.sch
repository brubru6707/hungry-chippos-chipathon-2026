v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {ADC top-level (INT-3) -- 8-bit SAR ADC, gf180mcuD.
Scheme per docs/pin_contracts.md (INT-2): DAC runs as a VDAC generator
(DAC VIN pin tied to VSS; SAMPLE=~RST_N resets DAC_TOP to 0 V each
conversion). ADC input VIN drives comparator VIN1 directly; DAC_TOP
drives VIN2. CMP_OUT=1 means VIN>VDAC = keep trial bit. Comparator
strobes on CK=~CLK (mid-trial, CLK-low half).
Decision latch: VOUT1/VOUT2 are each buffered by an IDENTICAL inverter
(x_ib1/x_ib2) before a cross-coupled NOR SR latch. Do NOT tie the
comparator outputs straight into a NAND SR latch: the NAND whose second
input is enabled by the held state presents a larger (Miller) input
capacitance, biasing near-rail decisions toward repeating the previous
decision (found in INT-5 sim: sticky keeps ratcheted VIN=3.25 V to code
255). The inverter buffers make both comparator outputs see identical,
state-independent loads.
BIT_i -> DAC B_i straight; EOC rises on the 8th CLK edge after RST_N
release (release during CLK-HIGH phase, see pin_contracts section 5).
13 pins: VDD VSS VIN CLK RST_N BIT_7..0 EOC.} -700 -700 0 0 0.3 0.3 {}
N -600 -600 -540 -600 {lab=VDD}
N -600 -560 -540 -560 {lab=VSS}
N -600 -520 -540 -520 {lab=VIN}
N -600 -480 -540 -480 {lab=CLK}
N -600 -440 -540 -440 {lab=RST_N}
N -600 -400 -540 -400 {lab=BIT_7}
N -600 -360 -540 -360 {lab=BIT_6}
N -600 -320 -540 -320 {lab=BIT_5}
N -600 -280 -540 -280 {lab=BIT_4}
N -600 -240 -540 -240 {lab=BIT_3}
N -600 -200 -540 -200 {lab=BIT_2}
N -600 -160 -540 -160 {lab=BIT_1}
N -600 -120 -540 -120 {lab=BIT_0}
N -600 -80 -540 -80 {lab=EOC}
C {dac/schematic/cap_array.sym} 0 0 0 0 {name=x_dac}
C {lab_wire.sym} -85 -130 0 0 {name=ld0 sig_type=std_logic lab=VSS}
C {lab_wire.sym} -85 -90 0 0 {name=ld1 sig_type=std_logic lab=VDD}
C {lab_wire.sym} -85 -70 0 0 {name=ld2 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} -85 -50 0 0 {name=ld3 sig_type=std_logic lab=BIT_0}
C {lab_wire.sym} -85 -30 0 0 {name=ld4 sig_type=std_logic lab=BIT_1}
C {lab_wire.sym} -85 -10 0 0 {name=ld5 sig_type=std_logic lab=BIT_2}
C {lab_wire.sym} -85 10 0 0 {name=ld6 sig_type=std_logic lab=BIT_3}
C {lab_wire.sym} -85 30 0 0 {name=ld7 sig_type=std_logic lab=BIT_4}
C {lab_wire.sym} -85 50 0 0 {name=ld8 sig_type=std_logic lab=BIT_5}
C {lab_wire.sym} -85 70 0 0 {name=ld9 sig_type=std_logic lab=BIT_6}
C {lab_wire.sym} -85 90 0 0 {name=ld10 sig_type=std_logic lab=BIT_7}
C {lab_wire.sym} 85 0 0 0 {name=ld11 sig_type=std_logic lab=DAC_TOP}
C {comparator/schematic/strongarm.sym} 600 100 0 0 {name=x_cmp}
C {lab_wire.sym} 750 20 0 0 {name=lc0 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 610 20 0 0 {name=lc1 sig_type=std_logic lab=CK}
C {lab_wire.sym} 750 40 0 0 {name=lc2 sig_type=std_logic lab=VOUT2}
C {lab_wire.sym} 750 60 0 0 {name=lc3 sig_type=std_logic lab=VOUT1}
C {lab_wire.sym} 610 40 0 0 {name=lc4 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 610 60 0 0 {name=lc5 sig_type=std_logic lab=DAC_TOP}
C {lab_wire.sym} 750 80 0 0 {name=lc6 sig_type=std_logic lab=VSS}
C {sar_logic/sar_designs/sar_logic.sym} 1400 0 0 0 {name=x_sar}
C {lab_wire.sym} 1400 -170 0 0 {name=ls0 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 1400 170 0 0 {name=ls1 sig_type=std_logic lab=VSS}
C {lab_wire.sym} 1540 -120 0 0 {name=ls2 sig_type=std_logic lab=BIT_7}
C {lab_wire.sym} 1540 -90 0 0 {name=ls3 sig_type=std_logic lab=BIT_6}
C {lab_wire.sym} 1540 -60 0 0 {name=ls4 sig_type=std_logic lab=BIT_5}
C {lab_wire.sym} 1540 -30 0 0 {name=ls5 sig_type=std_logic lab=BIT_4}
C {lab_wire.sym} 1540 0 0 0 {name=ls6 sig_type=std_logic lab=BIT_3}
C {lab_wire.sym} 1540 30 0 0 {name=ls7 sig_type=std_logic lab=BIT_2}
C {lab_wire.sym} 1540 60 0 0 {name=ls8 sig_type=std_logic lab=BIT_1}
C {lab_wire.sym} 1540 90 0 0 {name=ls9 sig_type=std_logic lab=BIT_0}
C {lab_wire.sym} 1540 120 0 0 {name=ls10 sig_type=std_logic lab=EOC}
C {lab_wire.sym} 1260 -60 0 0 {name=ls11 sig_type=std_logic lab=RST_N}
C {lab_wire.sym} 1260 0 0 0 {name=ls12 sig_type=std_logic lab=CMP_OUT}
C {lab_wire.sym} 1260 60 0 0 {name=ls13 sig_type=std_logic lab=CLK}
C {sar_logic/sar_designs/inv.sym} 700 400 0 0 {name=x_inv_ck}
C {lab_wire.sym} 630 330 0 0 {name=lik0 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 600 400 0 0 {name=lik1 sig_type=std_logic lab=CLK}
C {lab_wire.sym} 730 400 0 0 {name=lik2 sig_type=std_logic lab=CK}
C {lab_wire.sym} 630 460 0 0 {name=lik3 sig_type=std_logic lab=VSS}
C {sar_logic/sar_designs/inv.sym} 700 600 0 0 {name=x_inv_smp}
C {lab_wire.sym} 630 530 0 0 {name=lis0 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 600 600 0 0 {name=lis1 sig_type=std_logic lab=RST_N}
C {lab_wire.sym} 730 600 0 0 {name=lis2 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 630 660 0 0 {name=lis3 sig_type=std_logic lab=VSS}
C {sar_logic/sar_designs/inv.sym} 700 800 0 0 {name=x_ib1}
C {lab_wire.sym} 630 730 0 0 {name=lib1_0 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 600 800 0 0 {name=lib1_1 sig_type=std_logic lab=VOUT1}
C {lab_wire.sym} 730 800 0 0 {name=lib1_2 sig_type=std_logic lab=V1B}
C {lab_wire.sym} 630 860 0 0 {name=lib1_3 sig_type=std_logic lab=VSS}
C {sar_logic/sar_designs/inv.sym} 700 1000 0 0 {name=x_ib2}
C {lab_wire.sym} 630 930 0 0 {name=lib2_0 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 600 1000 0 0 {name=lib2_1 sig_type=std_logic lab=VOUT2}
C {lab_wire.sym} 730 1000 0 0 {name=lib2_2 sig_type=std_logic lab=V2B}
C {lab_wire.sym} 630 1060 0 0 {name=lib2_3 sig_type=std_logic lab=VSS}
C {sar_logic/sar_designs/nor2.sym} 1000 800 0 0 {name=x_nq}
C {lab_wire.sym} 990 760 0 0 {name=lnq0 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 970 770 0 0 {name=lnq1 sig_type=std_logic lab=V2B}
C {lab_wire.sym} 970 830 0 0 {name=lnq2 sig_type=std_logic lab=QB}
C {lab_wire.sym} 1040 800 0 0 {name=lnq3 sig_type=std_logic lab=CMP_OUT}
C {lab_wire.sym} 990 840 0 0 {name=lnq4 sig_type=std_logic lab=VSS}
C {sar_logic/sar_designs/nor2.sym} 1000 1000 0 0 {name=x_nqb}
C {lab_wire.sym} 990 960 0 0 {name=lnb0 sig_type=std_logic lab=VDD}
C {lab_wire.sym} 970 970 0 0 {name=lnb1 sig_type=std_logic lab=V1B}
C {lab_wire.sym} 970 1030 0 0 {name=lnb2 sig_type=std_logic lab=CMP_OUT}
C {lab_wire.sym} 1040 1000 0 0 {name=lnb3 sig_type=std_logic lab=QB}
C {lab_wire.sym} 990 1040 0 0 {name=lnb4 sig_type=std_logic lab=VSS}
C {iopin.sym} -600 -600 0 0 {name=pp0 lab=VDD}
C {lab_wire.sym} -540 -600 0 0 {name=lp0 sig_type=std_logic lab=VDD}
C {iopin.sym} -600 -560 0 0 {name=pp1 lab=VSS}
C {lab_wire.sym} -540 -560 0 0 {name=lp1 sig_type=std_logic lab=VSS}
C {ipin.sym} -600 -520 0 0 {name=pp2 lab=VIN}
C {lab_wire.sym} -540 -520 0 0 {name=lp2 sig_type=std_logic lab=VIN}
C {ipin.sym} -600 -480 0 0 {name=pp3 lab=CLK}
C {lab_wire.sym} -540 -480 0 0 {name=lp3 sig_type=std_logic lab=CLK}
C {ipin.sym} -600 -440 0 0 {name=pp4 lab=RST_N}
C {lab_wire.sym} -540 -440 0 0 {name=lp4 sig_type=std_logic lab=RST_N}
C {opin.sym} -600 -400 0 0 {name=pp5 lab=BIT_7}
C {lab_wire.sym} -540 -400 0 0 {name=lp5 sig_type=std_logic lab=BIT_7}
C {opin.sym} -600 -360 0 0 {name=pp6 lab=BIT_6}
C {lab_wire.sym} -540 -360 0 0 {name=lp6 sig_type=std_logic lab=BIT_6}
C {opin.sym} -600 -320 0 0 {name=pp7 lab=BIT_5}
C {lab_wire.sym} -540 -320 0 0 {name=lp7 sig_type=std_logic lab=BIT_5}
C {opin.sym} -600 -280 0 0 {name=pp8 lab=BIT_4}
C {lab_wire.sym} -540 -280 0 0 {name=lp8 sig_type=std_logic lab=BIT_4}
C {opin.sym} -600 -240 0 0 {name=pp9 lab=BIT_3}
C {lab_wire.sym} -540 -240 0 0 {name=lp9 sig_type=std_logic lab=BIT_3}
C {opin.sym} -600 -200 0 0 {name=pp10 lab=BIT_2}
C {lab_wire.sym} -540 -200 0 0 {name=lp10 sig_type=std_logic lab=BIT_2}
C {opin.sym} -600 -160 0 0 {name=pp11 lab=BIT_1}
C {lab_wire.sym} -540 -160 0 0 {name=lp11 sig_type=std_logic lab=BIT_1}
C {opin.sym} -600 -120 0 0 {name=pp12 lab=BIT_0}
C {lab_wire.sym} -540 -120 0 0 {name=lp12 sig_type=std_logic lab=BIT_0}
C {opin.sym} -600 -80 0 0 {name=pp13 lab=EOC}
C {lab_wire.sym} -540 -80 0 0 {name=lp13 sig_type=std_logic lab=EOC}
