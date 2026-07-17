v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Gate-truth-table testbench (Brief #5 SAMPLE-gating verification).
Drives B0 and B7 with the SAME pattern (B1-B6 tied low, don't-care)
through all 4 (SAMPLE,B) combinations in 10ns windows with 0.1ns edges
and 9.8ns flat settle plateaus:
  [0,10n)   SAMPLE=1 B=0
  [10n,20n) SAMPLE=1 B=1
  [20n,30n) SAMPLE=0 B=0
  [30n,40n) SAMPLE=0 B=1
Probes the actual bN/bN_bar nodes feeding unit_switch inside cap_array:
x1.B0G/x1.B0_B (bit0) and x1.B7G/x1.B7_B (bit7). Expect: SAMPLE=1 =>
both G and _B LOW regardless of B (M2/M3 off, zero contention);
SAMPLE=0 => G=B, _B=NOT B (normal DAC conversion).} 0 -300 0 0 0.25 0.25 {}
N -400 -100 -400 -80 {lab=VIN}
N -400 -20 -400 0 {lab=0}
N -300 -100 -300 -80 {lab=VREF}
N -300 -20 -300 0 {lab=0}
N -200 -100 -200 -80 {lab=VDD}
N -200 -20 -200 0 {lab=0}
N -100 -100 -100 -80 {lab=SAMPLE}
N -100 -20 -100 0 {lab=0}
N 0 -100 0 -80 {lab=B7}
N 0 -20 0 0 {lab=0}
N 100 -100 100 -80 {lab=B6}
N 100 -20 100 0 {lab=0}
N 200 -100 200 -80 {lab=B5}
N 200 -20 200 0 {lab=0}
N 300 -100 300 -80 {lab=B4}
N 300 -20 300 0 {lab=0}
N 400 -100 400 -80 {lab=B3}
N 400 -20 400 0 {lab=0}
N 500 -100 500 -80 {lab=B2}
N 500 -20 500 0 {lab=0}
N 600 -100 600 -80 {lab=B1}
N 600 -20 600 0 {lab=0}
N 700 -100 700 -80 {lab=B0}
N 700 -20 700 0 {lab=0}
N -85 70 -110 70 {lab=VIN}
N -85 90 -110 90 {lab=VREF}
N -85 110 -110 110 {lab=VDD}
N -85 130 -110 130 {lab=SAMPLE}
N -85 150 -110 150 {lab=B0}
N -85 170 -110 170 {lab=B1}
N -85 190 -110 190 {lab=B2}
N -85 210 -110 210 {lab=B3}
N -85 230 -110 230 {lab=B4}
N -85 250 -110 250 {lab=B5}
N -85 270 -110 270 {lab=B6}
N -85 290 -110 290 {lab=B7}
N 85 200 200 200 {lab=DAC_TOP}
N 200 200 200 230 {lab=DAC_TOP}
N 200 290 200 310 {lab=0}
C {vsource.sym} -400 -50 0 0 {name=V_VIN value=1.2 savecurrent=false}
C {vsource.sym} -300 -50 0 0 {name=V_VREF value=1.65 savecurrent=false}
C {vsource.sym} -200 -50 0 0 {name=V_VDD value=3.3 savecurrent=false}
C {vsource.sym} -100 -50 0 0 {name=V_SAMPLE value="pwl(0 3.3 19.9n 3.3 20n 0 39.9n 0)" savecurrent=false}
C {vsource.sym} 0 -50 0 0 {name=V_B7 value="pwl(0 0 9.9n 0 10n 3.3 19.9n 3.3 20n 0 29.9n 0 30n 3.3 39.9n 3.3)" savecurrent=false}
C {vsource.sym} 100 -50 0 0 {name=V_B6 value=0 savecurrent=false}
C {vsource.sym} 200 -50 0 0 {name=V_B5 value=0 savecurrent=false}
C {vsource.sym} 300 -50 0 0 {name=V_B4 value=0 savecurrent=false}
C {vsource.sym} 400 -50 0 0 {name=V_B3 value=0 savecurrent=false}
C {vsource.sym} 500 -50 0 0 {name=V_B2 value=0 savecurrent=false}
C {vsource.sym} 600 -50 0 0 {name=V_B1 value=0 savecurrent=false}
C {vsource.sym} 700 -50 0 0 {name=V_B0 value="pwl(0 0 9.9n 0 10n 3.3 19.9n 3.3 20n 0 29.9n 0 30n 3.3 39.9n 3.3)" savecurrent=false}
C {gnd.sym} -400 0 0 0 {name=l1 lab=0}
C {gnd.sym} -300 0 0 0 {name=l2 lab=0}
C {gnd.sym} -200 0 0 0 {name=l3 lab=0}
C {gnd.sym} -100 0 0 0 {name=l4 lab=0}
C {gnd.sym} 0 0 0 0 {name=l5 lab=0}
C {gnd.sym} 100 0 0 0 {name=l6 lab=0}
C {gnd.sym} 200 0 0 0 {name=l7 lab=0}
C {gnd.sym} 300 0 0 0 {name=l8 lab=0}
C {gnd.sym} 400 0 0 0 {name=l9 lab=0}
C {gnd.sym} 500 0 0 0 {name=l10 lab=0}
C {gnd.sym} 600 0 0 0 {name=l11 lab=0}
C {gnd.sym} 700 0 0 0 {name=l12 lab=0}
C {lab_wire.sym} -400 -80 0 0 {name=p1 sig_type=std_logic lab=VIN}
C {lab_wire.sym} -300 -80 0 0 {name=p2 sig_type=std_logic lab=VREF}
C {lab_wire.sym} -200 -80 0 0 {name=p3 sig_type=std_logic lab=VDD}
C {lab_wire.sym} -100 -80 0 0 {name=p4 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 0 -80 0 0 {name=p5 sig_type=std_logic lab=B7}
C {lab_wire.sym} 100 -80 0 0 {name=p6 sig_type=std_logic lab=B6}
C {lab_wire.sym} 200 -80 0 0 {name=p7 sig_type=std_logic lab=B5}
C {lab_wire.sym} 300 -80 0 0 {name=p8 sig_type=std_logic lab=B4}
C {lab_wire.sym} 400 -80 0 0 {name=p9 sig_type=std_logic lab=B3}
C {lab_wire.sym} 500 -80 0 0 {name=p10 sig_type=std_logic lab=B2}
C {lab_wire.sym} 600 -80 0 0 {name=p11 sig_type=std_logic lab=B1}
C {lab_wire.sym} 700 -80 0 0 {name=p12 sig_type=std_logic lab=B0}
C {lab_wire.sym} -110 70 0 0 {name=p13 sig_type=std_logic lab=VIN}
C {lab_wire.sym} -110 90 0 0 {name=p14 sig_type=std_logic lab=VREF}
C {lab_wire.sym} -110 110 0 0 {name=p15 sig_type=std_logic lab=VDD}
C {lab_wire.sym} -110 130 0 0 {name=p16 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} -110 150 0 0 {name=p17 sig_type=std_logic lab=B0}
C {lab_wire.sym} -110 170 0 0 {name=p18 sig_type=std_logic lab=B1}
C {lab_wire.sym} -110 190 0 0 {name=p19 sig_type=std_logic lab=B2}
C {lab_wire.sym} -110 210 0 0 {name=p20 sig_type=std_logic lab=B3}
C {lab_wire.sym} -110 230 0 0 {name=p21 sig_type=std_logic lab=B4}
C {lab_wire.sym} -110 250 0 0 {name=p22 sig_type=std_logic lab=B5}
C {lab_wire.sym} -110 270 0 0 {name=p23 sig_type=std_logic lab=B6}
C {lab_wire.sym} -110 290 0 0 {name=p24 sig_type=std_logic lab=B7}
C {lab_wire.sym} 150 200 0 0 {name=p25 sig_type=std_logic lab=DAC_TOP}
C {capa.sym} 200 260 0 0 {name=Cload m=1 value=20f}
C {gnd.sym} 200 310 0 0 {name=l13 lab=0}
C {dac/schematic/cap_array.sym} 0 200 0 0 {name=x1}
C {code.sym} 0 -450 0 0 {name=s1 only_toplevel=false value="
.param nfet_wid=0.42u nfet_len=0.28u
.param mim_corner_1p0fF=1 mim_corner_1p5fF=1 mim_corner_2p0fF=1
.param mc_c_cox_1p0fF=0 mc_c_cox_1p5fF=0 mc_c_cox_2p0fF=0
.param var_vth=0 var_k=0
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice cap_mim
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.options savecurrents
.control
save all
tran 0.01n 40n
* bit0 truth table
meas tran b0g_s1_b0 FIND v(x1.B0G) AT=5n
meas tran b0b_s1_b0 FIND v(x1.B0_B) AT=5n
meas tran b0g_s1_b1 FIND v(x1.B0G) AT=15n
meas tran b0b_s1_b1 FIND v(x1.B0_B) AT=15n
meas tran b0g_s0_b0 FIND v(x1.B0G) AT=25n
meas tran b0b_s0_b0 FIND v(x1.B0_B) AT=25n
meas tran b0g_s0_b1 FIND v(x1.B0G) AT=35n
meas tran b0b_s0_b1 FIND v(x1.B0_B) AT=35n
* bit7 truth table
meas tran b7g_s1_b0 FIND v(x1.B7G) AT=5n
meas tran b7b_s1_b0 FIND v(x1.B7_B) AT=5n
meas tran b7g_s1_b1 FIND v(x1.B7G) AT=15n
meas tran b7b_s1_b1 FIND v(x1.B7_B) AT=15n
meas tran b7g_s0_b0 FIND v(x1.B7G) AT=25n
meas tran b7b_s0_b0 FIND v(x1.B7_B) AT=25n
meas tran b7g_s0_b1 FIND v(x1.B7G) AT=35n
meas tran b7b_s0_b1 FIND v(x1.B7_B) AT=35n
echo bit0_truth_table_V:
print b0g_s1_b0 b0b_s1_b0 b0g_s1_b1 b0b_s1_b1 b0g_s0_b0 b0b_s0_b0 b0g_s0_b1 b0b_s0_b1
echo bit7_truth_table_V:
print b7g_s1_b0 b7b_s1_b0 b7g_s1_b1 b7b_s1_b1 b7g_s0_b0 b7b_s0_b0 b7g_s0_b1 b7b_s0_b1
.endc
"}
