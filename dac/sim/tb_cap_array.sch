v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {First-pass DAC-3 / Gate 2 settling testbench.
Phase 1 (0-100n): SAMPLE=1, bottom plates all tied to VIN (1.2V).
Phase 2 (100n+): SAMPLE=0, B7 (MSB) steps 0->1 as the bit trial;
B0-B6 held low. Probe DAC_TOP settling after the B7 edge.
This only tests one transition (MSB step), not the full major-carry
(0111_1111 -> 1000_0000) or all 256 codes - extend before trusting
this as the real Gate 2 result. Not yet simulated in Xschem - open,
netlist, and run before trusting.} 0 -300 0 0 0.25 0.25 {}
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
N 85 200 110 200 {lab=DAC_TOP}
C {vsource.sym} -400 -50 0 0 {name=V_VIN value=1.2 savecurrent=false}
C {vsource.sym} -300 -50 0 0 {name=V_VREF value=1.65 savecurrent=false}
C {vsource.sym} -200 -50 0 0 {name=V_VDD value=3.3 savecurrent=false}
C {vsource.sym} -100 -50 0 0 {name=V_SAMPLE value="pulse(3.3 0 100n 1n 1n 900n 2u)" savecurrent=false}
C {vsource.sym} 0 -50 0 0 {name=V_B7 value="pulse(0 3.3 100n 1n 1n 900n 2u)" savecurrent=false}
C {vsource.sym} 100 -50 0 0 {name=V_B6 value="dc 0" savecurrent=false}
C {vsource.sym} 200 -50 0 0 {name=V_B5 value="dc 0" savecurrent=false}
C {vsource.sym} 300 -50 0 0 {name=V_B4 value="dc 0" savecurrent=false}
C {vsource.sym} 400 -50 0 0 {name=V_B3 value="dc 0" savecurrent=false}
C {vsource.sym} 500 -50 0 0 {name=V_B2 value="dc 0" savecurrent=false}
C {vsource.sym} 600 -50 0 0 {name=V_B1 value="dc 0" savecurrent=false}
C {vsource.sym} 700 -50 0 0 {name=V_B0 value="dc 0" savecurrent=false}
C {gnd.sym} -400 20 0 0 {name=l1 lab=0}
C {gnd.sym} -300 20 0 0 {name=l2 lab=0}
C {gnd.sym} -200 20 0 0 {name=l3 lab=0}
C {gnd.sym} -100 20 0 0 {name=l4 lab=0}
C {gnd.sym} 0 20 0 0 {name=l5 lab=0}
C {gnd.sym} 100 20 0 0 {name=l6 lab=0}
C {gnd.sym} 200 20 0 0 {name=l7 lab=0}
C {gnd.sym} 300 20 0 0 {name=l8 lab=0}
C {gnd.sym} 400 20 0 0 {name=l9 lab=0}
C {gnd.sym} 500 20 0 0 {name=l10 lab=0}
C {gnd.sym} 600 20 0 0 {name=l11 lab=0}
C {gnd.sym} 700 20 0 0 {name=l12 lab=0}
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
tran 0.1n 2u
plot v(SAMPLE) v(B7) v(DAC_TOP)
* Gate 2 check (first pass, MSB step only): measure 10%-90% settling
* time of DAC_TOP after the B7 edge at t=100n, compare against 40ns spec.
meas tran t_settle_lo when v(DAC_TOP)=(0.1*(v(DAC_TOP)@2u - v(DAC_TOP)@100n)) rise=1
meas tran t_settle_hi when v(DAC_TOP)=(0.9*(v(DAC_TOP)@2u - v(DAC_TOP)@100n)) rise=1
.endc
"}
