v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -10 -20 -10 30 {lab=VOUT}
N -10 -80 20 -80 {lab=DVDD}
N 20 -80 20 -50 {lab=DVDD}
N -10 -50 20 -50 {lab=DVDD}
N -10 60 20 60 {lab=VSS}
N 20 60 20 90 {lab=VSS}
N -10 90 20 90 {lab=VSS}
N -50 -50 -50 60 {lab=VIN}
C {symbols/pfet_03v3.sym} -30 -50 0 0 {name=M1
L=0.28u
W=1.0u
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
C {symbols/nfet_03v3.sym} -30 60 0 0 {name=M2
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
C {ipin.sym} -50 0 0 0 {name=p1 lab=VIN}
C {opin.sym} -10 0 0 0 {name=p2 lab=VOUT}
C {iopin.sym} -10 90 1 0 {name=p3 lab=VSS}
C {iopin.sym} -10 -80 3 0 {name=p4 lab=VDD}
