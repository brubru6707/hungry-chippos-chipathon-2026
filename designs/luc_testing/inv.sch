v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Simple CMOS Inverter
} 350 -730 0 0 0.4 0.4 {}
N 410 -240 420 -240 {lab=vi}
N 370 -470 410 -470 {lab=vi}
N 370 -470 370 -240 {lab=vi}
N 370 -240 410 -240 {lab=vi}
N 340 -360 370 -360 {lab=vi}
N 450 -440 450 -270 {lab=vo}
N 450 -360 650 -360 {lab=vo}
N 450 -590 450 -500 {lab=vdd}
N 450 -210 450 -150 {lab=vss}
N 450 -470 490 -470 {lab=vdd}
N 490 -530 490 -470 {lab=vdd}
N 450 -530 490 -530 {lab=vdd}
N 450 -240 490 -240 {lab=vss}
N 490 -240 490 -190 {lab=vss}
N 450 -190 490 -190 {lab=vss}
C {title.sym} 210 -70 0 0 {name="l1" author="Luc Bastien"
}
C {symbols/nfet_03v3.sym} 430 -240 0 0 {name=M1
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
C {symbols/pfet_03v3.sym} 430 -470 0 0 {name=M2
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
C {iopin.sym} 450 -590 3 0 {name=p1 lab=vdd}
C {iopin.sym} 450 -150 1 0 {name=p2 lab=vss
}
C {ipin.sym} 340 -360 0 0 {name=p3 lab=vi
}
C {opin.sym} 650 -360 0 0 {name=p4 lab=vo
}
