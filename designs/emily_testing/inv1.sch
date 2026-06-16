v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {lab=#net4
}
F {}
E {}
N 20 -10 20 10 {lab=vout}
N -70 -50 -20 -50 {lab=vin}
N -70 -0 -70 40 {lab=vin}
N -70 40 -20 40 {lab=vin}
N 20 -90 20 -80 {lab=DVDD}
N 20 -90 50 -90 {lab=DVDD}
N 50 -90 50 -50 {lab=DVDD}
N 20 -50 50 -50 {lab=DVDD}
N 30 70 50 70 {lab=DVSS}
N 50 40 50 70 {lab=DVSS}
N 20 40 50 40 {lab=DVSS}
N 20 -10 40 -10 {lab=vout}
N -100 0 -70 -0 {lab=vin}
N 20 -110 20 -90 {lab=DVDD}
N 30 70 30 80 {lab=DVSS}
N 20 -20 20 -10 {lab=vout}
N -70 -50 -70 -0 {lab=vin}
N 20 70 30 70 {lab=DVSS}
C {symbols/pfet_03v3.sym} 0 -50 0 0 {name=M1
L=0.3u
W=1.7u
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
C {symbols/nfet_03v3.sym} 0 40 0 0 {name=M2
L=0.3u
W=0.85u
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
C {ipin.sym} -100 0 0 0 {name=p1 lab=vin
}
C {iopin.sym} 40 -10 0 0 {name=p2 lab=vout
}
C {iopin.sym} 20 -110 3 0 {name=p3 lab=DVDD}
C {iopin.sym} 30 80 1 0 {name=p4 lab=DVSS}
