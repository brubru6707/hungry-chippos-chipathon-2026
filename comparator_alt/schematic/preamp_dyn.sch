v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -160 -230 210 -230 {lab=VDD}
N -170 -230 -170 -180 {lab=VDD}
N -170 -230 -160 -230 {lab=VDD}
N -260 -230 -170 -230 {lab=VDD}
N 170 -230 170 -180 {lab=VDD}
N 170 -120 170 20 {lab=DIP2}
N 170 -50 220 -50 {lab=DIP2}
N -170 -120 -170 20 {lab=DIP1}
N -220 -50 -170 -50 {lab=DIP1}
N -250 300 240 300 {lab=VSS}
N -170 80 -170 130 {lab=TAIL}
N 170 80 170 130 {lab=TAIL}
N -170 130 170 130 {lab=TAIL}
N 0 130 -0 170 {lab=TAIL}
N 0 230 -0 300 {lab=VSS}
N -270 50 -210 50 {lab=VIN1}
N 210 50 260 50 {lab=VIN2}
N 260 50 270 50 {lab=VIN2}
N 210 -150 260 -150 {lab=CK}
N -280 -150 -210 -150 {lab=CK}
N -90 200 -40 200 {lab=CK}
N -170 50 0 50 {lab=VSS}
N 0 50 170 50 {lab=VSS}
N 0 200 70 200 {lab=VSS}
N 70 200 70 230 {lab=VSS}
N 0 230 70 230 {lab=VSS}
N -170 -150 -90 -150 {lab=VDD}
N -90 -180 -90 -150 {lab=VDD}
N -170 -180 -90 -180 {lab=VDD}
N 100 -150 170 -150 {lab=VDD}
N 100 -180 100 -150 {lab=VDD}
N 100 -180 170 -180 {lab=VDD}
C {symbols/nfet_03v3.sym} -20 200 0 0 {name=MT1
L=1u
W=1u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X}
C {symbols/pfet_03v3.sym} -190 -150 0 0 {name=MP1
L=0.3u
W=3u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
C {symbols/pfet_03v3.sym} 190 -150 0 1 {name=MP2
L=0.3u
W=3u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X}
C {ipin.sym} -270 50 0 0 {name=p1 lab=VIN1}
C {ipin.sym} 270 50 2 0 {name=p2 lab=VIN2}
C {iopin.sym} 210 -230 0 0 {name=p4 lab=VDD}
C {iopin.sym} 240 300 0 0 {name=p5 lab=VSS}
C {opin.sym} -220 -50 2 0 {name=p6 lab=DIP1}
C {opin.sym} 220 -50 0 0 {name=p7 lab=DIP2}
C {ipin.sym} -90 200 0 0 {name=p9 lab=CK}
C {lab_wire.sym} 0 130 0 0 {name=p11 sig_type=std_logic lab=TAIL}
C {lab_pin.sym} 0 50 1 0 {name=p10 sig_type=std_logic lab=VSS}
C {lab_pin.sym} -280 -150 0 0 {name=p12 sig_type=std_logic lab=CK}
C {lab_pin.sym} 260 -150 2 0 {name=p13 sig_type=std_logic lab=CK
}
C {symbols/nfet_06v0_nvt.sym} -190 50 0 0 {name=M1P
L=1u
W=4u
nf=1
m=16
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_06v0
spiceprefix=X
}
C {symbols/nfet_06v0_nvt.sym} 190 50 0 1 {name=M2P
L=1u
W=4u
nf=1
m=16
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_06v0
spiceprefix=X
}
