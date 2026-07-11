v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 200 100 200 110 {lab=0}
N -210 110 200 110 {lab=0}
N -210 110 -210 120 {lab=0}
N -210 100 -210 110 {lab=0}
N -140 100 -140 110 {lab=0}
N -70 100 -70 110 {lab=0}
N 200 10 200 40 {lab=Z}
N 50 50 50 110 {lab=0}
N -210 -90 50 -90 {lab=#net1}
N -210 -90 -210 40 {lab=#net1}
N 50 -90 50 -30 {lab=#net1}
N -140 -20 30 -20 {lab=A}
N -140 -20 -140 40 {lab=A}
N -70 40 30 40 {lab=B}
N 100 10 200 10 {lab=Z}
C {vsource.sym} -70 70 0 0 {name=VB value="PULSE(0 3.3 0 1n 1n 1u 2u)" savecurrent=false}
C {vsource.sym} -140 70 0 0 {name=VA value="PULSE(0 3.3 0 1n 1n 2u 4u)" savecurrent=false}
C {vsource.sym} -210 70 0 0 {name=VVDD value=3.3 savecurrent=false}
C {gnd.sym} -210 120 0 0 {name=l1 lab=0}
C {capa.sym} 200 70 0 0 {name=C1
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} -40 -20 0 0 {name=p2 sig_type=std_logic lab=A}
C {lab_pin.sym} -20 40 0 0 {name=p3 sig_type=std_logic lab=B}
C {lab_pin.sym} 190 10 0 0 {name=p4 sig_type=std_logic lab=Z}
C {nor2.sym} 60 10 0 0 {name=x1}
C {code_shown.sym} 150 -130 0 0 {name=MODELS only_toplevel=true  
format="tcleval( @value )" 
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/smbb000149.ngspice typical
"}
C {code_shown.sym} 270 60 0 0 {name=COMMANDS only_toplevel=false value="
.control
  tran 10n 4u
  run
  plot V(A) V(B) V(Z)
.endc
"}
