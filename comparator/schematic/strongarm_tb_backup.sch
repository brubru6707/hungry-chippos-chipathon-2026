v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 700 -310 700 -240 {lab=VIN1}
N 700 -310 870 -310 {lab=VIN1}
N 770 -290 770 -240 {lab=VIN2}
N 770 -290 870 -290 {lab=VIN2}
N 630 -330 630 -240 {lab=CK}
N 630 -330 870 -330 {lab=CK}
N 1010 -310 1140 -310 {lab=OUT1}
N 1010 -290 1100 -290 {lab=OUT2}
C {comparator/schematic/strongarm.sym} 860 -250 0 0 {name=STRONGARM}
C {vsource.sym} 770 -210 0 0 {name=V1 value=3 savecurrent=false}
C {vsource.sym} 700 -210 0 0 {name=V2 value=3 savecurrent=false}
C {vsource.sym} 560 -210 0 0 {name=V3 value=3 savecurrent=false}
C {vsource.sym} 630 -210 0 0 {name=V4 value=3 savecurrent=false}
C {title.sym} 170 -50 0 0 {name=l1 author="Bruno R.M."}
C {gnd.sym} 630 -180 0 0 {name=l2 lab=0}
C {gnd.sym} 560 -180 0 0 {name=l3 lab=0}
C {gnd.sym} 700 -180 0 0 {name=l4 lab=0}
C {gnd.sym} 770 -180 0 0 {name=l5 lab=0}
C {lab_pin.sym} 630 -240 0 0 {name=p1 sig_type=std_logic lab=CK}
C {lab_pin.sym} 700 -240 0 0 {name=p3 sig_type=std_logic lab=VIN1}
C {lab_pin.sym} 770 -240 0 0 {name=p4 sig_type=std_logic lab=VIN2}
C {vdd.sym} 1010 -330 1 0 {name=l6 lab=VDD}
C {vdd.sym} 560 -240 0 0 {name=l7 lab=VDD}
C {gnd.sym} 1010 -270 3 0 {name=l8 lab=0}
C {noconn.sym} 1100 -290 0 1 {name=l9}
C {noconn.sym} 1140 -310 0 1 {name=l10}
C {lab_wire.sym} 1120 -310 0 0 {name=p2 sig_type=std_logic lab=OUT1}
C {lab_wire.sym} 1050 -290 2 0 {name=p5 sig_type=std_logic lab=OUT2}
C {devices/code_shown.sym} 30 -220 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {devices/code_shown.sym} 20 -780 0 0 {name=NGSPICE only_toplevel=true
value="
.control
save all

** defin input signal & clock freq
let fclk = 50Meg
let tper = 1/fclk
let tfr = 0.01*tper
let ton 0.5*tper*-2*tfr

** define transient params
let tstop = 3*tper
let tstep = 0.001*tper

** set sources
* define static DC voltages for the differential pair inputs
alter @VVIN2[DC] = 1.201
alter @VVIN2[DC] = 1.200

* configure the clock source as a dynamic pulse stream
alter @vck[PULSE] = [ 0 3.3 0 $$&tfr $$&tfr $$&ton $$&tper 0 ]

** simulations
op
tran $$&tstep $$&tstop 
dc vd 0 3.3 0.01 vg 0 3.3 0.3
write strongarm_latch_tb.raw
.endc
"}
