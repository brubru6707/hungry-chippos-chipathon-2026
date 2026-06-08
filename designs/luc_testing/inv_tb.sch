v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Inverter Test Bench} 700 -540 0 0 0.4 0.4 {}
N 640 -250 640 -190 {lab=0}
N 720 -250 720 -190 {lab=0}
N 640 -390 640 -310 {lab=VDD}
N 720 -310 790 -310 {lab=in}
N 850 -250 850 -190 {lab=0}
N 850 -440 850 -380 {lab=VDD}
N 910 -310 990 -310 {lab=out}
C {title.sym} 160 -40 0 0 {name=l1 author="Luc Bastien"}
C {inv.sym} 790 -380 0 0 {name=xinv1}
C {vsource.sym} 640 -280 0 0 {name=V1 value=3.3 savecurrent=false}
C {vsource.sym} 720 -280 0 0 {name=VIN value=3.3 savecurrent=false}
C {vdd.sym} 640 -390 0 0 {name=l2 lab=VDD}
C {vdd.sym} 850 -440 0 0 {name=l3 lab=VDD}
C {gnd.sym} 640 -190 0 0 {name=l4 lab=0}
C {gnd.sym} 720 -190 0 0 {name=l5 lab=0}
C {gnd.sym} 850 -190 0 0 {name=l6 lab=0}
C {noconn.sym} 990 -310 0 1 {name=l7}
C {lab_wire.sym} 770 -310 0 0 {name=p1 sig_type=std_logic lab=in}
C {lab_wire.sym} 960 -310 0 0 {name=p2 sig_type=std_logic lab=out
}
C {devices/code_shown.sym} 20 -190 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {devices/code_shown.sym} 10 -920 0 0 {name=NGSPICE only_toplevel=true
value="

.control
save all

** Define input signal
let fsig = 1k
let tper = 1/fsig
let tfr = 0.01*tper
let ton = tper*0.5 - 2*tfr

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

** Plots
setplot dc1
let vout = v(out)
plot vout

setplot tran1
let vout = v(out)
let vin = v(in)
let ivdd = v1#branch
plot vout vin ivdd

setplot op1
write inv_tb.raw
.endc
"}
C {launcher.sym} 670 -120 0 0 {name=h1
descr="Annotate OP"
tclcommand="set show_hidden_texts 1; xschem annotate_op" }
