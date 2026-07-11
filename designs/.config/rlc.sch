v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -440 -250 -440 -230 {lab=A}
N -440 -250 -290 -250 {lab=A}
N -290 -250 -290 -180 {lab=A}
N -440 20 -440 30 {lab=0}
N -290 -120 -290 30 {lab=0}
N -440 30 -300 30 {lab=0}
N -300 30 -290 30 {lab=0}
N -440 -70 -440 -40 {lab=#net1}
N -440 -170 -440 -130 {lab=#net2}
C {capa.sym} -440 -200 0 0 {name=C1
m=1
value=50nF
footprint=1206
device="ceramic capacitor"}
C {res.sym} -290 -150 0 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {ind.sym} -440 -100 0 0 {name=L1
m=1
value=10mH
footprint=1206
device=inductor}
C {vsource_arith.sym} -440 -10 0 0 {name=E1 VOL="'3*cos(time*time*1e11)'"}
C {lab_pin.sym} -290 -250 0 1 {name=p1 sig_type=std_logic lab=A
}
C {lab_pin.sym} -290 30 0 1 {name=p2 sig_type=std_logic lab=0
}
C {code.sym} -70 -180 0 0 {name=STIMULI
only_toplevel=false 
value="
.tran 10n 2000u uic
.save all
"}
C {title.sym} -440 120 0 0 {name=l2 author="Maxwell A"}
