v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -70 -130 -70 -110 {lab=VDD}
N -70 -130 90 -130 {lab=VDD}
N 90 -130 90 -110 {lab=VDD}
N 90 -50 90 -30 {lab=xxx}
N -70 -30 90 -30 {lab=xxx}
N -70 -50 -70 -30 {lab=xxx}
N 10 -30 10 -0 {lab=xxx}
N 10 60 10 90 {lab=#net1}
N -150 -80 -110 -80 {lab=A}
N -150 -80 -150 30 {lab=A}
N -150 30 -30 30 {lab=A}
N 50 120 160 120 {lab=B}
N 160 -80 160 120 {lab=B}
N 130 -80 160 -80 {lab=B}
N 10 30 70 30 {lab=VSS}
N 70 30 70 150 {lab=VSS}
N 10 150 70 150 {lab=VSS}
N -20 120 10 120 {lab=VSS}
N -20 120 -20 150 {lab=VSS}
N -20 150 10 150 {lab=VSS}
N -70 -80 -40 -80 {lab=VDD}
N -40 -130 -40 -80 {lab=VDD}
N 60 -80 90 -80 {lab=VDD}
N 60 -130 60 -80 {lab=VDD}
C {symbols/pfet_03v3.sym} -90 -80 0 0 {name=M1
L=0.28u
W=1u
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
C {symbols/pfet_03v3.sym} 110 -80 0 1 {name=M2
L=0.28u
W=1u
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
C {symbols/nfet_03v3.sym} -10 30 0 0 {name=M3
L=0.28u
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
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 30 120 0 1 {name=M4
L=0.28u
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
spiceprefix=X
}
C {ipin.sym} -150 -20 0 0 {name=p1 lab=A}
C {ipin.sym} 160 20 0 1 {name=p2 lab=B}
C {iopin.sym} 10 150 1 0 {name=p3 lab=VSS}
C {iopin.sym} 10 -130 3 0 {name=p4 lab=VDD}
C {opin.sym} 10 -30 3 0 {name=p5 lab=Z}
