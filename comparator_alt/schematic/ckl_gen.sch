v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -80 -130 90 -130 {lab=VDD}
N 90 -130 390 -130 {lab=VDD}
N 390 -130 690 -130 {lab=VDD}
N 690 -130 990 -130 {lab=VDD}
N 990 -130 1290 -130 {lab=VDD}
N 1290 -130 1590 -130 {lab=VDD}
N 1290 -30 1590 -30 {lab=VSS}
N 990 -30 1290 -30 {lab=VSS}
N 690 -30 990 -30 {lab=VSS}
N 390 -30 690 -30 {lab=VSS}
N 90 -30 390 -30 {lab=VSS}
N -80 -30 90 -30 {lab=VSS}
N 1590 -220 1590 -130 {lab=VDD}
N 1590 -220 1830 -220 {lab=VDD}
N 1830 -220 1970 -220 {lab=VDD}
N 1970 -220 2150 -220 {lab=VDD}
N 1830 -160 1830 -140 {lab=#net1}
N 1970 -160 1970 -140 {lab=#net1}
N 1830 -140 1970 -140 {lab=#net1}
N 1970 -140 2100 -140 {lab=#net1}
N 1910 -140 1910 -120 {lab=#net1}
N 1830 -190 1900 -190 {lab=VDD}
N 1900 -220 1900 -190 {lab=VDD}
N 1970 -190 2040 -190 {lab=VDD}
N 2040 -220 2040 -190 {lab=VDD}
N 1910 -60 1910 -30 {lab=#net2}
N 1590 30 1910 30 {lab=VSS}
N 1590 -30 1590 30 {lab=VSS}
N 1910 30 2150 30 {lab=VSS}
N 1910 0 2000 0 {lab=VSS}
N 2000 0 2000 30 {lab=VSS}
N 1910 -90 2000 -90 {lab=VSS}
N 2000 -90 2000 0 {lab=VSS}
N 2100 -140 2130 -140 {lab=#net1}
N 2150 -220 2240 -220 {lab=VDD}
N 2190 -220 2190 -210 {lab=VDD}
N 2130 -140 2150 -140 {lab=#net1}
N 2150 -180 2150 -140 {lab=#net1}
N 2150 -140 2150 -60 {lab=#net1}
N 2190 -30 2190 30 {lab=VSS}
N 2150 30 2250 30 {lab=VSS}
N 2190 -60 2280 -60 {lab=VSS}
N 2280 -60 2280 30 {lab=VSS}
N 2250 30 2330 30 {lab=VSS}
N 2190 -180 2260 -180 {lab=VDD}
N 2260 -220 2260 -180 {lab=VDD}
N 2240 -220 2340 -220 {lab=VDD}
N 2190 -150 2190 -130 {lab=CKL}
N 2190 -120 2190 -90 {lab=CKL}
N 2190 -130 2190 -120 {lab=CKL}
N 2190 -120 2290 -120 {lab=CKL}
C {comparator_alt/schematic/inv_slow.sym} 90 -80 0 0 {name=x1}
C {comparator_alt/schematic/inv_slow.sym} 390 -80 0 0 {name=x2}
C {comparator_alt/schematic/inv_slow.sym} 690 -80 0 0 {name=x3}
C {comparator_alt/schematic/inv_slow.sym} 990 -80 0 0 {name=x4}
C {comparator_alt/schematic/inv_slow.sym} 1290 -80 0 0 {name=x5}
C {comparator_alt/schematic/inv_slow.sym} 1590 -80 0 0 {name=x6}
C {iopin.sym} -80 -130 2 0 {name=p1 lab=VDD}
C {iopin.sym} -80 -30 2 0 {name=p2 lab=VSS}
C {ipin.sym} -60 -80 0 0 {name=p3 lab=CK}
C {symbols/pfet_03v3.sym} 1810 -190 0 0 {name=M1
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
C {symbols/pfet_03v3.sym} 1950 -190 0 0 {name=M2
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
C {symbols/nfet_03v3.sym} 1890 -90 0 0 {name=M3
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
model=nfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} 1890 0 0 0 {name=M4
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
model=nfet_03v3
spiceprefix=X
}
C {lab_pin.sym} 1740 -80 2 0 {name=p4 sig_type=std_logic lab=CKD}
C {lab_pin.sym} 1930 -190 0 0 {name=p5 sig_type=std_logic lab=CKD}
C {lab_pin.sym} 1870 0 0 0 {name=p6 sig_type=std_logic lab=CKD}
C {lab_pin.sym} 1870 -90 0 0 {name=p7 sig_type=std_logic lab=CK}
C {lab_pin.sym} 1790 -190 0 0 {name=p8 sig_type=std_logic lab=CK}
C {symbols/nfet_03v3.sym} 2170 -60 0 0 {name=M5
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
C {symbols/pfet_03v3.sym} 2170 -180 0 0 {name=M6
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
C {opin.sym} 2290 -120 0 0 {name=p9 lab=CKL}
