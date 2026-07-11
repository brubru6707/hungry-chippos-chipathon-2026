v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 140 70 140 80 {lab=0}
N -270 80 140 80 {lab=0}
N -270 80 -270 90 {lab=0}
N -270 70 -270 80 {lab=0}
N -200 70 -200 80 {lab=0}
N -130 70 -130 80 {lab=0}
N 140 -20 140 10 {lab=Z}
N 60 -20 140 -20 {lab=Z}
N -10 20 -10 80 {lab=0}
N -10 -120 -10 -60 {lab=#net1}
N -270 -120 -10 -120 {lab=#net1}
N -270 -120 -270 10 {lab=#net1}
N -200 -40 -200 10 {lab=A}
N -200 -40 -40 -40 {lab=A}
N -130 0 -130 10 {lab=B}
N -130 -0 -40 -0 {lab=B}
C {nand2.sym} 40 -20 0 0 {name=x1}
C {vsource.sym} -130 40 0 0 {name=VB value="PULSE(0 3.3 0 1n 1n 1u 2u)" savecurrent=false}
C {vsource.sym} -200 40 0 0 {name=VA value="PULSE(0 3.3 0 1n 1n 2u 4u)" savecurrent=false}
C {vsource.sym} -270 40 0 0 {name=VVDD value=3.3 savecurrent=false}
C {gnd.sym} -270 90 0 0 {name=l1 lab=0}
C {capa.sym} 140 40 0 0 {name=C1
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {code_shown.sym} 90 -180 0 0 {name=MODELS only_toplevel=true  
format="tcleval( @value )" 
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/smbb000149.ngspice typical
"}
C {code_shown.sym} 210 10 0 0 {name=COMMANDS only_toplevel=false value="
.control
  tran 10n 4u
  run
  plot V(A) V(B) V(Z)
.endc
"}
C {lab_pin.sym} -100 -40 0 0 {name=p2 sig_type=std_logic lab=A}
C {lab_pin.sym} -80 0 0 0 {name=p3 sig_type=std_logic lab=B}
C {lab_pin.sym} 130 -20 0 0 {name=p4 sig_type=std_logic lab=Z}
