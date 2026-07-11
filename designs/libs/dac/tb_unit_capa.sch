v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 1830 -1190 1830 -1170 {lab=VIN}
N 1860 -1190 1860 -1170 {lab=VREF}
N 1900 -1190 1900 -1170 {lab=GND}
N 1860 -1340 1860 -1320 {lab=TOP_PLATE}
N 1930 -1240 1960 -1240 {lab=bN_bar}
N 1960 -1240 1960 -1210 {lab=bN_bar}
N 1930 -1280 2090 -1280 {lab=SAMPLE}
N 1930 -1260 2110 -1260 {lab=bN}
N 2180 -1260 2180 -1200 {lab=bN}
N 1860 -1420 1860 -1400 {lab=GND}
N 1830 -1110 1830 -1090 {lab=GND}
N 1860 -1110 1860 -1090 {lab=GND}
N 2180 -1140 2180 -1130 {lab=GND}
N 2110 -1260 2180 -1260 {lab=bN}
C {designs/libs/dac/unit_switch.sym} 1880 -1270 0 0 {name=x1}
C {vsource.sym} 2120 -1280 3 0 {name=V_SAMPLE value="PULSE(0 3.3 0 1n 1n 44n 100n)" savecurrent=false
text_size_1=0.1}
C {vsource.sym} 2180 -1170 0 0 {name=V_bN value="PULSE(0 3.3 50n 1n 1n 44n 200n)" savecurrent=false
text_size_1=0.2}
C {vsource.sym} 1960 -1180 0 0 {name=V_bN_bar value="PULSE(0 3.3 150n 1n 1n 44n 200n)" savecurrent=false
w=20u l=20u text_size_1=0.2}
C {vsource.sym} 1830 -1140 0 1 {name=V_VIN value=1.65 savecurrent=false}
C {vsource.sym} 1860 -1140 0 0 {name=V_VREF value=3.3 savecurrent=false}
C {code_shown.sym} 830 -1740 0 0 {name=MODELS only_toplevel=false
value="
* MIM PARAMETERS
.param mim_corner_1p0fF=1 mim_corner_1p5fF=1 mim_corner_2p0fF=1
.param mc_c_cox_1p0fF=0 mc_c_cox_1p5fF=0 mc_c_cox_2p0fF=0
.param var_vth=0 var_k=0

* CKT PARAMETERS
.param nfet_wid=0.42u nfet_len=0.28u
.param m_capa=1 w_capa=5e-6 l_capa=5e-6

*.lib \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/sm141064.ngspice\\" nfet_03v3_t
*.lib \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/sm141064.ngspice\\" fets_mm
.lib \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/sm141064.ngspice\\" typical
.lib \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/sm141064.ngspice\\" cap_mim
.include \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/design.ngspice\\"
.options savecurrents
.control
save all
tran 1n 200n
plot v(TOP_PLATE) v(VIN) v(SAMPLE) v(bN) v(bN_bar)
.endc
"
}
C {symbols/cap_mim_2f0fF.sym} 1860 -1370 2 0 {name=C_load
W=w_capa
L=l_capa
model=cap_mim_2f0fF
spiceprefix=X
m=m_capa}
C {lab_pin.sym} 1860 -1330 0 0 {name=p7 sig_type=std_logic lab=TOP_PLATE}
C {lab_pin.sym} 1980 -1280 1 0 {name=p8 sig_type=std_logic lab=SAMPLE}
C {lab_pin.sym} 2180 -1230 2 0 {name=p9 sig_type=std_logic lab=bN}
C {lab_pin.sym} 1960 -1220 2 0 {name=p10 sig_type=std_logic lab=bN_bar}
C {lab_pin.sym} 1830 -1180 0 0 {name=p11 sig_type=std_logic lab=VIN}
C {lab_pin.sym} 1860 -1180 2 0 {name=p12 sig_type=std_logic lab=VREF}
C {gnd.sym} 2150 -1280 3 0 {name=l2 lab=GND}
C {gnd.sym} 2180 -1130 0 0 {name=l3 lab=GND}
C {gnd.sym} 1960 -1150 0 0 {name=l4 lab=GND}
C {gnd.sym} 1860 -1090 0 0 {name=l6 lab=GND}
C {gnd.sym} 1900 -1170 0 0 {name=l7 lab=GND}
C {gnd.sym} 1830 -1090 0 0 {name=l8 lab=GND}
C {gnd.sym} 1860 -1420 2 1 {name=l5 lab=GND}
