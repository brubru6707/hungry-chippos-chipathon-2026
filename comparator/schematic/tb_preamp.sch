v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {title.sym} 40 -40 0 0 {name=l1 author="Luc Bastien"}
C {gnd.sym} 340 -150 0 0 {name=l2 lab=0}
C {lab_pin.sym} 340 -170 2 0 {name=p1 sig_type=std_logic lab=DIP1}
C {lab_pin.sym} 340 -190 2 0 {name=p10 sig_type=std_logic lab=DIP2}
C {lab_pin.sym} 340 -210 2 0 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 40 -210 0 0 {name=p3 sig_type=std_logic lab=VIN2}
C {lab_pin.sym} 40 -190 0 0 {name=p4 sig_type=std_logic lab=VIN1}
C {lab_pin.sym} 40 -170 0 0 {name=p5 sig_type=std_logic lab=CK}
C {code_shown.sym} 20 -600 0 0 {name=NGSPICE only_toplevel=false value="
* stimulus
V1 VDD 0 3.3
V2 VIN1 0 1.6505
V3 VIN2 0 1.6495
V4 CK  0 PULSE(0 3.3 2n 100p 100p 10n 20n)
C1 DIP1 0 30f
C2 DIP2 0 30f
* <-- paste your GF180 model .lib line here -->
.tran 10p 20n
.control
run
plot v(dip1) v(dip2) v(ck)
let vd = v(dip2)-v(dip1)
plot vd
meas tran vpk MAX vd from=2.1n to=12n
let gain = vpk/1m
print gain
.endc
"}
C {code_shown.sym} 550 -590 0 0 {name=MODELS only_toplevel=false value="
.param sw_stat_global   = 0
.param sw_stat_mismatch = 0
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
"
}
C {comparator/schematic/preamp_dyn.sym} 190 -180 0 0 {name=x2}
