v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 30 -70 30 -50 {lab=vout}
N -50 -20 -10 -20 {lab=clk}
N 30 10 30 30 {lab=vin}
N 30 -20 70 -20 {lab=0}
C {symbols/nfet_03v3.sym} 10 -20 0 0 {name=M1
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
C {ipin.sym} 30 30 3 0 {name=p1 lab=vin
}
C {ipin.sym} -40 -20 0 0 {name=p2 lab=clk}
C {opin.sym} 30 -70 3 0 {name=p3 lab=vout
}
C {gnd.sym} 70 -20 0 0 {name=l1 lab=0}
