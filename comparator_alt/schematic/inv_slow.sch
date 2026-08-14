v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 60 -90 80 -90 {lab=A}
N 80 -140 80 -90 {lab=A}
N 80 -90 80 -40 {lab=A}
N -10 -200 240 -200 {lab=VDD}
N -20 30 240 30 {lab=VSS}
N 120 -10 120 30 {lab=VSS}
N 120 -40 130 -40 {lab=VSS}
N 130 -40 130 30 {lab=VSS}
N 120 -200 120 -170 {lab=VDD}
N 120 -140 130 -140 {lab=VDD}
N 130 -200 130 -140 {lab=VDD}
N 120 -110 120 -70 {lab=xxx}
N 120 -90 190 -90 {lab=xxx}
C {symbols/nfet_03v3.sym} 100 -40 0 0 {name=MT1
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
C {symbols/pfet_03v3.sym} 100 -140 0 0 {name=M1
L=1u
W=2u
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
C {iopin.sym} 240 -200 0 0 {name=p1 lab=VDD}
C {iopin.sym} 240 30 0 0 {name=p2 lab=VSS}
C {opin.sym} 190 -90 0 0 {name=p3 lab=Y}
C {ipin.sym} 60 -90 0 0 {name=p4 lab=A}
