v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -20 -110 -20 -40 {lab=#net1}
N -20 -190 -20 -170 {lab=#net1}
N -20 70 110 70 {lab=0}
N -20 70 -20 80 {lab=0}
N -20 15 -20 80 {lab=0}
N -170 60 -170 70 {lab=0}
N -170 70 -20 70 {lab=0}
N -290 70 -20 70 {lab=0}
N -290 60 -290 70 {lab=0}
N -230 60 -230 70 {lab=0}
N -170 60 -170 70 {lab=0}
N -170 -190 -20 -190 {lab=#net1}
N -290 -190 -290 0 {lab=#net1}
N -290 -190 -170 -190 {lab=#net1}
N -230 -160 -230 0 {lab=CTRL_B}
N -230 -160 -80 -160 {lab=CTRL_B}
N -80 -160 -80 -70 {lab=CTRL_B}
N -170 -10 -170 0 {lab=A}
N -170 -10 -80 -10 {lab=A}
N 40 -10 120 -10 {lab=B}
N 120 -10 120 0 {lab=B}
N 120 60 120 70 {lab=0}
N 110 70 120 70 {lab=0}
N -20 -170 -20 -110 {lab=#net1}
N -350 -30 -350 0 {lab=CTRL}
N -390 -30 -350 -30 {lab=CTRL}
N -390 -30 -390 120 {lab=CTRL}
N -390 120 40 120 {lab=CTRL}
N 40 40 40 120 {lab=CTRL}
N -350 60 -350 70 {lab=0}
N -350 70 -290 70 {lab=0}
C {tg.sym} 0 -10 0 0 {name=x1}
C {code_shown.sym} 90 -340 0 0 {name=MODELS only_toplevel=true  
format="tcleval( @value )" 
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/smbb000149.ngspice typical
"}
C {code_shown.sym} 210 -150 0 0 {name=COMMANDS only_toplevel=false value="
* Simulation Command
.control
  tran 1n 2u
  run
  plot V(A) V(B) V(CTRL)
.endc"}
C {vsource.sym} -350 30 0 0 {name=VCTRL value="PULSE(0 3.3 0 1n 1n 500n 1u)" savecurrent=false}
C {gnd.sym} -20 80 0 0 {name=l1 lab=0}
C {vsource.sym} -170 30 0 0 {name=VA value="PULSE(0 3.3 0 100n 100n 1u 2u)" savecurrent=false}
C {vsource.sym} -230 30 0 0 {name=VCTRL_B value="PULSE(3.3 0 0 1n 1n 500n 1u)" savecurrent=false}
C {vsource.sym} -290 30 0 0 {name=VVDD value=3.3 savecurrent=false}
C {capa.sym} 120 30 0 0 {name=CLOAD
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} -130 -10 0 0 {name=p1 sig_type=std_logic lab=A}
C {lab_pin.sym} 90 -10 0 0 {name=p2 sig_type=std_logic lab=B}
C {lab_pin.sym} -80 -90 0 0 {name=p3 sig_type=std_logic lab=CTRL_B}
C {lab_pin.sym} 40 50 0 0 {name=p4 sig_type=std_logic lab=CTRL}
