v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 330 70 330 90 {lab=#net1}
N 360 70 360 90 {lab=#net2}
N 400 70 400 90 {lab=0}
N 360 -80 360 -60 {lab=#net3}
N 430 20 460 20 {lab=#net4}
N 460 20 460 50 {lab=#net4}
N 430 -20 590 -20 {lab=#net5}
N 430 0 610 0 {lab=#net6}
N 610 0 610 60 {lab=#net6}
C {libs/dac/unit_switch.sym} 380 -10 0 0 {name=x1}
C {vsource.sym} 620 -20 3 0 {name=V_SAMPLE value="PULSE(0 3.3 0 1n 1n 50n 100n)" savecurrent=false
text_size_1=0.1}
C {vsource.sym} 610 90 0 0 {name=V_bN value="PULSE(0 3.3 60 1n 1n 40n 100n)" savecurrent=false
text_size_1=0.1}
C {vsource.sym} 460 80 0 0 {name=V_bN_bar value="PULSE(3.3 0 60 1n 1n 40n 100n)" savecurrent=false
w=20u l=20u text_size_1=0.1}
C {vsource.sym} 330 120 0 1 {name=V_VIN value=1.65 savecurrent=false}
C {vsource.sym} 360 120 0 0 {name=V_VREF value=3.3 savecurrent=false}
C {gnd.sym} 400 90 0 0 {name=V_GND lab=0}
C {lab_pin.sym} 650 -20 0 1 {name=p1 sig_type=std_logic lab=GND}
C {lab_pin.sym} 610 120 0 1 {name=p2 sig_type=std_logic lab=GND}
C {lab_pin.sym} 460 110 1 1 {name=p3 sig_type=std_logic lab=GND}
C {lab_pin.sym} 330 150 0 0 {name=p4 sig_type=std_logic lab=GND}
C {lab_pin.sym} 360 150 0 1 {name=p5 sig_type=std_logic lab=GND}
C {lab_pin.sym} 360 -140 0 0 {name=p6 sig_type=std_logic lab=GND}
C {code_shown.sym} 650 -340 0 0 {name=NGSPICE only_toplevel=false
value="
**PARAMETERS
.param wn=0.42u ln=0.28u
.param m_capa=1 w_capa=5e-6 l_capa=5e-6
.tran 1n 200n
"}
C {code_shown.sym} -20 -250 0 0 {name=MODELS only_toplevel=false
value="
.include \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/design.ngspice\\"
.lib \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/sm141064.ngspice\\" typical
"}
C {symbols/cap_mim_2f0fF.sym} 360 -110 2 1 {name=C_load
W=w_capa
L=l_capa
model=cap_mim_2f0fF
spiceprefix=X
m=m_capa}
