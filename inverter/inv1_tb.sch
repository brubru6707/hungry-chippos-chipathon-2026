v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 400 -290 400 -240 {lab=0}
N 400 -420 400 -350 {lab=VDD}
N 570 -290 570 -250 {lab=0}
N 570 -370 750 -370 {lab=in}
N 570 -370 570 -350 {lab=in}
N 830 -290 830 -230 {lab=0}
N 910 -370 990 -370 {lab=out}
N 830 -490 830 -450 {lab=VDD}
C {title.sym} 170 -40 0 0 {name=l1 author="Bruno R.M."}
C {vsource.sym} 400 -320 0 0 {name=V1 value=3.3 savecurrent=false}
C {vsource.sym} 570 -320 0 0 {name=VIN value=3.3 savecurrent=false}
C {vdd.sym} 830 -490 0 0 {name=l2 lab=VDD}
C {vdd.sym} 400 -420 0 1 {name=l3 lab=VDD}
C {gnd.sym} 400 -240 0 0 {name=l4 lab=0}
C {gnd.sym} 570 -250 0 0 {name=l5 lab=0}
C {gnd.sym} 830 -230 0 0 {name=l6 lab=0}
C {noconn.sym} 990 -370 2 0 {name=l7}
C {lab_wire.sym} 660 -370 0 0 {name=p1 sig_type=std_logic lab=in}
C {lab_wire.sym} 970 -370 0 0 {name=p2 sig_type=std_logic lab=out}
C {devices/code_shown.sym} 20 -160 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {devices/code_shown.sym} 10 -820 0 0 {name=NGSPICE only_toplevel=true
value="
.control
save all

** Define input signal
let fsig = 1k
let tper = 1/fsig
let tfr = 0.01*tper
let ton = 0.5*tper-2*tfr

** Define transient params
let tstop = 2*tper
let tstep = 0.001*tper

** Set Sources
alter @VIN[DC] = 0.0
alter @VIN[PULSE] = [ 0 3.3 0 $&tfr $&tfr $&ton $&tper 0 ]

** Simulations
op
dc vin 0 3.3 0.01
tran $&tstep $&tstop

write inv1_tb.raw
.endc
"}
C {inverter/inv1.sym} 750 -270 0 0 {name=x2}
