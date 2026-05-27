v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {pmos} 160 -60 0 0 0.4 0.4 {}
T {nmos} 160 80 0 0 0.4 0.4 {}
T {CMOS Inverter} -200 -110 0 0 0.4 0.4 {}
N -20 -30 -20 80 {lab=vi}
N -50 30 -20 30 {lab=vi}
N 20 0 20 50 {lab=vo}
N 20 110 20 160 {lab=vss}
N 20 -90 20 -60 {lab=vdd}
N 20 30 110 30 {lab=vo}
N 20 80 80 80 {lab=vss}
N 80 80 80 130 {lab=vss}
N 20 130 80 130 {lab=vss}
N 20 -30 70 -30 {lab=vdd}
N 70 -80 70 -30 {lab=vdd}
N 20 -80 70 -80 {lab=vdd}
C {symbols/pfet_03v3.sym} 0 -30 0 0 {name=M1
L=0.28u
W=0.22u
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
C {symbols/nfet_03v3.sym} 0 80 0 0 {name=M2
L=0.28u
W=0.22u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {ipin.sym} -50 30 0 0 {name=p1 lab=vi}
C {opin.sym} 110 30 2 1 {name=p2 lab=vo}
C {iopin.sym} 20 -90 3 0 {name=p3 lab=vdd}
C {iopin.sym} 20 160 3 1 {name=p4 lab=vss}
