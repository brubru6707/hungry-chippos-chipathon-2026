v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {comparator_alt/schematic/ckl_gen.sym} 150 -30 0 0 {name=x1}
C {lab_pin.sym} 0 -50 0 0 {name=p1 sig_type=std_logic lab=CK}
C {lab_pin.sym} 300 -50 2 0 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 300 -30 2 0 {name=p4 sig_type=std_logic lab=CKL}
C {code_shown.sym} 910 -400 0 0 {name=MODELS only_toplevel=false value="
.param sw_stat_global   = 0
.param sw_stat_mismatch = 0
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
"}
C {code_shown.sym} 80 -310 0 0 {name=s1 only_toplevel=false value="
Vvdd VDD 0 3.3
Vck  CK  0 PULSE(0 3.3 2n 100p 100p 8n 20n)

.control
save v(ck) v(ckl)
tran 0.01n 25n
meas tran trise trig v(ck) val=1.65 rise=1 targ v(ckl) val=1.65 rise=1
meas tran tfall trig v(ck) val=1.65 fall=1 targ v(ckl) val=1.65 fall=1
echo RESULT tt trise=$&trise tfall=$&tfall
.endc
"}
C {gnd.sym} 300 -10 0 0 {name=l1 lab=0}
