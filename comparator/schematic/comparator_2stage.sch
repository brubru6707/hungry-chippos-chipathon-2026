v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 330 -230 430 -230 {lab=DIP1}
N 330 -210 430 -210 {lab=DIP2}
N 430 -230 490 -210 {lab=DIP1}
N 430 -210 490 -230 {lab=DIP2}
C {ipin.sym} 30 -210 0 0 {name=p1 lab=CK}
C {iopin.sym} 330 -250 0 0 {name=p3 lab=VDD}
C {lab_pin.sym} 790 -250 2 0 {name=p4 sig_type=std_logic lab=VDD}
C {iopin.sym} 330 -190 0 0 {name=p5 lab=VSS}
C {lab_pin.sym} 790 -190 2 0 {name=p6 sig_type=std_logic lab=VSS}
C {ipin.sym} 30 -230 0 0 {name=p7 lab=VIN1}
C {ipin.sym} 30 -250 0 0 {name=p8 lab=VIN2}
C {opin.sym} 790 -230 0 0 {name=p9 lab=VOUT2}
C {opin.sym} 790 -210 0 0 {name=p10 lab=VOUT1}
C {ipin.sym} 490 -250 0 0 {name=p2 lab=CKL}
C {lab_wire.sym} 420 -230 0 0 {name=p11 sig_type=std_logic lab=DIP1}
C {lab_wire.sym} 420 -210 0 0 {name=p12 sig_type=std_logic lab=DIP2}
C {comparator/schematic/preamp_dyn.sym} 180 -220 0 0 {name=x1}
C {comparator/schematic/strongarm_2.sym} 640 -220 0 0 {name=x2}
