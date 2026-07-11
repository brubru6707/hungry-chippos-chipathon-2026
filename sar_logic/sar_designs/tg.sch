v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 20 -110 40 -110 {lab=A}
N 20 -110 20 50 {lab=A}
N 20 50 40 50 {lab=A}
N 100 50 120 50 {lab=B}
N 120 -110 120 50 {lab=B}
N 100 -110 120 -110 {lab=B}
C {symbols/pfet_03v3.sym} 70 -130 1 0 {name=M1
L=1u
W=0.28u
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
C {symbols/nfet_03v3.sym} 70 70 3 0 {name=M2
L=0.28u
W=0.5u
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
C {iopin.sym} 70 -110 1 0 {name=p1 lab=VDD}
C {iopin.sym} 70 50 3 0 {name=p2 lab=VSS}
C {iopin.sym} 20 -30 0 1 {name=p3 lab=A}
C {iopin.sym} 120 -30 0 0 {name=p4 lab=B}
C {ipin.sym} 70 -150 1 0 {name=p5 lab=CTRL_B}
C {ipin.sym} 70 90 3 0 {name=p6 lab=CTRL}
