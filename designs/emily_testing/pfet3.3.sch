v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {symbols/pfet_03v3.sym} 90 0 0 0 {name=M1
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
C {opin.sym} 110 30 1 0 {name=p1 lab=vout}
C {ipin.sym} 70 0 0 0 {name=p2 lab=vgate
}
C {iopin.sym} 110 -30 3 0 {name=p3 lab=vin
}
C {ipin.sym} 110 0 2 0 {name=p4 lab=vbulk
}
