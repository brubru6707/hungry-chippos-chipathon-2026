v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -130 -150 -130 -100 {lab=VDD}
N 130 -150 130 -100 {lab=VDD}
N 360 -150 360 -100 {lab=VDD}
N 520 -150 520 -100 {lab=VDD}
N 130 -40 130 80 {lab=VOUT2}
N 130 140 130 180 {lab=#net1}
N 170 250 220 250 {lab=VIN2}
N 130 280 130 310 {lab=#net2}
N 0 310 130 310 {lab=#net2}
N -130 -40 -130 80 {lab=VOUT1}
N -130 140 -130 180 {lab=#net3}
N -220 250 -170 250 {lab=VIN1}
N -130 280 -130 310 {lab=#net2}
N -130 310 0 310 {lab=#net2}
N 60 40 130 40 {lab=VOUT2}
N -130 40 -60 40 {lab=VOUT1}
N -90 110 60 40 {lab=VOUT2}
N -60 40 90 110 {lab=VOUT1}
N -510 -40 -510 180 {lab=#net3}
N -130 180 -130 220 {lab=#net3}
N 130 180 130 220 {lab=#net1}
N -130 -20 90 -70 {lab=VOUT1}
N -90 -70 130 -20 {lab=VOUT2}
N -580 -70 -550 -70 {lab=#net4}
N 0 310 0 360 {lab=#net2}
N -240 110 -130 110 {lab=#net3}
N -240 110 -240 140 {lab=#net3}
N -240 140 -130 140 {lab=#net3}
N -130 280 -20 280 {lab=#net2}
N -20 250 -20 280 {lab=#net2}
N -130 250 -20 250 {lab=#net2}
N 20 250 130 250 {lab=#net2}
N 20 250 20 280 {lab=#net2}
N 20 280 130 280 {lab=#net2}
N 130 140 240 140 {lab=#net1}
N 240 110 240 140 {lab=#net1}
N 130 110 240 110 {lab=#net1}
N -200 -70 -130 -70 {lab=VDD}
N -200 -100 -200 -70 {lab=VDD}
N -200 -100 -130 -100 {lab=VDD}
N -510 -70 -440 -70 {lab=VDD}
N -440 -100 -440 -70 {lab=VDD}
N -510 -100 -440 -100 {lab=VDD}
N 130 -70 200 -70 {lab=VDD}
N 200 -100 200 -70 {lab=VDD}
N 130 -100 200 -100 {lab=VDD}
N 290 -70 360 -70 {lab=#net5}
N 290 -100 360 -100 {lab=VDD}
N 450 -70 520 -70 {lab=VDD}
N 450 -100 450 -70 {lab=VDD}
N 450 -100 520 -100 {lab=VDD}
N 0 390 70 390 {lab=#net2}
N 70 360 70 390 {lab=#net2}
N 0 360 70 360 {lab=#net2}
N -510 -150 550 -150 {lab=VDD}
N -360 -100 -290 -100 {lab=VDD}
N -290 -100 -290 -70 {lab=VDD}
N -360 -70 -290 -70 {lab=VDD}
N -360 -20 -130 -20 {lab=VOUT1}
N -360 -40 -360 -20 {lab=VOUT1}
N -360 -150 -360 -100 {lab=VDD}
N -510 -150 -510 -100 {lab=VDD}
N -510 180 -130 180 {lab=#net3}
N 130 -20 360 -20 {lab=VOUT2}
N 360 -40 360 -20 {lab=VOUT2}
N 130 180 520 180 {lab=#net1}
N 520 -40 520 180 {lab=#net1}
N 400 -70 400 -0 {lab=#net4}
N 400 -0 560 0 {lab=#net4}
N 560 -70 560 0 {lab=#net4}
N -550 -70 -550 0 {lab=#net4}
N -550 0 -400 -0 {lab=#net4}
N -400 -70 -400 -0 {lab=#net4}
N 80 0 130 0 {lab=VOUT2}
N -130 0 -90 -0 {lab=VOUT1}
N -580 390 -40 390 {lab=#net4}
N -580 -70 -580 390 {lab=#net4}
N 560 -70 660 -70 {lab=#net4}
N 660 -200 660 -70 {lab=#net4}
N -580 -200 660 -200 {lab=#net4}
N -580 -200 -580 -70 {lab=#net4}
C {symbols/nfet_03v3.sym} 110 110 0 0 {name=M1
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
C {symbols/pfet_03v3.sym} -110 -70 0 1 {name=M2
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
C {symbols/pfet_03v3.sym} -380 -70 0 0 {name=M3
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
C {symbols/pfet_03v3.sym} -530 -70 0 0 {name=M4
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
C {symbols/pfet_03v3.sym} 540 -70 0 1 {name=M5
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
C {symbols/pfet_03v3.sym} 380 -70 0 1 {name=M6
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
C {symbols/pfet_03v3.sym} 110 -70 0 0 {name=M7
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
C {symbols/nfet_03v3.sym} 150 250 0 1 {name=M8
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
C {symbols/nfet_03v3.sym} -110 110 0 1 {name=M9
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
C {symbols/nfet_03v3.sym} -150 250 0 0 {name=M10
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
C {symbols/nfet_03v3.sym} -20 390 0 0 {name=M11
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
C {opin.sym} -90 0 0 0 {name=p8 lab=VOUT1}
C {opin.sym} 80 0 0 1 {name=p3 lab=VOUT2}
C {ipin.sym} -220 250 0 0 {name=p2 lab=VIN1}
C {ipin.sym} 220 250 0 1 {name=p9 lab=VIN2}
C {ipin.sym} -580 -70 0 0 {name=CK lab=CK}
C {iopin.sym} 550 -150 0 0 {name=p1 lab=VDD}
C {iopin.sym} 0 420 1 0 {name=p6 lab=VSS}
