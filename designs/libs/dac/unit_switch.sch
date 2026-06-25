v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -60 -130 -60 -70 {lab=B_PLATE}
N -60 -130 240 -130 {lab=B_PLATE}
N 240 -130 240 -70 {lab=B_PLATE}
N 70 -130 70 -70 {lab=B_PLATE}
N 240 -10 240 20 {lab=GND}
N 70 -10 70 20 {lab=VREF}
N -60 -10 -60 20 {lab=VIN}
N -130 -40 -100 -40 {lab=SAMPLE}
N -60 -40 -30 -40 {lab=GND}
N 70 -150 70 -130 {lab=B_PLATE}
N -30 -40 70 -40 {lab=GND}
N 20 -40 20 10 {lab=GND}
N 20 10 240 10 {lab=GND}
N 200 -40 240 -40 {lab=GND}
N 200 -40 200 10 {lab=GND}
C {symbols/nfet_03v3.sym} -80 -40 0 0 {name=M1
L='ln'
W='wn'
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
C {symbols/nfet_03v3.sym} 90 -40 0 1 {name=M2
L='ln'
W='wn'
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
C {symbols/nfet_03v3.sym} 260 -40 0 1 {name=M3
L='ln'
W='wn'
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
C {ipin.sym} 240 20 3 0 {name=p1 lab=GND}
C {ipin.sym} 70 20 3 0 {name=p2 lab=VREF}
C {ipin.sym} -60 20 3 0 {name=p3 lab=VIN}
C {ipin.sym} -130 -40 0 0 {name=p5 lab=SAMPLE}
C {iopin.sym} 70 -150 0 0 {name=p6 lab=B_PLATE}
C {ipin.sym} 110 -40 2 0 {name=p4 lab=bN}
C {ipin.sym} 280 -40 2 0 {name=p7 lab=bN_bar}
