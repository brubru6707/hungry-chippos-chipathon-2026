v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 30 -70 30 -40 {lab=#net1}
N -50 80 -50 100 {lab=Z}
N -50 80 150 80 {lab=Z}
N 150 80 150 100 {lab=Z}
N 30 20 30 80 {lab=Z}
N -50 160 -50 180 {lab=VSS}
N -50 180 150 180 {lab=VSS}
N 150 160 150 180 {lab=VSS}
N -140 -100 -10 -100 {lab=A}
N -140 -100 -140 130 {lab=A}
N -140 130 -90 130 {lab=A}
N 70 -10 220 -10 {lab=B}
N 220 -10 220 130 {lab=B}
N 190 130 220 130 {lab=B}
N -50 130 -10 130 {lab=VSS}
N -10 130 -10 180 {lab=VSS}
N 110 130 150 130 {lab=VSS}
N 110 130 110 180 {lab=VSS}
N -40 -10 30 -10 {lab=VDD}
N -40 -130 -40 -10 {lab=VDD}
N -40 -130 30 -130 {lab=VDD}
N 30 -100 60 -100 {lab=VDD}
N 60 -130 60 -100 {lab=VDD}
N 30 -130 60 -130 {lab=VDD}
C {symbols/pfet_03v3.sym} 50 -10 0 1 {name=M1
L=0.28u
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
C {symbols/pfet_03v3.sym} 10 -100 0 0 {name=M2
L=0.28u
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
C {symbols/nfet_03v3.sym} -70 130 0 0 {name=M3
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
C {symbols/nfet_03v3.sym} 170 130 0 1 {name=M4
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
C {iopin.sym} 30 180 1 0 {name=p1 lab=VSS}
C {iopin.sym} 30 -130 3 0 {name=p2 lab=VDD}
C {ipin.sym} -140 20 0 0 {name=p3 lab=A}
C {ipin.sym} 220 60 2 0 {name=p4 lab=B}
C {opin.sym} 30 80 1 0 {name=p5 lab=Z}
