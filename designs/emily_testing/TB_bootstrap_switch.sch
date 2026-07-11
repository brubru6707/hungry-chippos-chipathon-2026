v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 270 -185 270 -160 {lab=CLK}
N 60 -80 60 -55 {lab=CLK_INV}
N -350 -330 -350 -310 {lab=VIN}
N -165 -150 -80 -150 {lab=#net1}
N -165 -150 -165 10 {lab=#net1}
N -165 10 70 10 {lab=#net1}
N -20 -150 10 -150 {lab=Vc}
N 10 -190 10 -150 {lab=Vc}
N 10 -150 30 -150 {lab=Vc}
N 30 -150 30 -120 {lab=Vc}
N 90 -120 150 -120 {lab=VBS}
N 210 -120 240 -120 {lab=#net2}
N 50 -220 115 -220 {lab=VBS}
N 115 -220 115 -120 {lab=VBS}
N 70 10 85 10 {lab=#net1}
N 115 -120 115 -30 {lab=VBS}
N 145 10 170 10 {lab=VIN}
N 115 -30 200 -30 {lab=VBS}
N 230 10 280 10 {lab=VOUT}
N -15 -60 10 -60 {lab=CLK}
N -100 -90 -60 -90 {lab=#net1}
N -100 -150 -100 -90 {lab=#net1}
N 160 10 160 40 {lab=VIN}
N -15 -220 10 -220 {lab=VDD}
N 180 -120 180 -110 {lab=0}
N 180 -120 180 -110 {lab=0}
N 270 -120 270 -110 {lab=0}
N 115 10 115 20 {lab=0}
N 200 10 200 20 {lab=0}
N -65 -60 -55 -60 {lab=0}
N 60 -155 60 -120 {lab=Vc}
C {symbols/nfet_03v3.sym} 180 -140 1 0 {name=M1
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
C {symbols/nfet_03v3.sym} 270 -140 1 0 {name=M3
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
C {symbols/nfet_03v3.sym} -35 -60 2 0 {name=M4
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
C {symbols/nfet_03v3.sym} 115 -10 1 0 {name=M5
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
C {symbols/nfet_03v3.sym} 200 -10 1 0 {name=M6
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
C {symbols/cap_mim_2f0fF.sym} 280 40 2 0 {name=C3
W=1e-6
L=1e-6
model=cap_mim_2f0fF
spiceprefix=X
m=1}
C {symbols/pfet_03v3.sym} 30 -220 2 0 {name=M7
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
C {symbols/pfet_03v3.sym} 60 -100 3 0 {name=M8
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
C {symbols/cap_mim_2f0fF.sym} -50 -150 1 0 {name=C2
W=10u
L=10u
model=cap_mim_2f0fF
spiceprefix=X
m=1}
C {vdd.sym} 10 -250 0 0 {name=l1 lab=VDD}
C {vdd.sym} -360 -190 0 0 {name=l2 lab=VDD}
C {vsource.sym} -360 -160 0 0 {name=V1 value=3.3 savecurrent=false}
C {gnd.sym} -360 -130 0 0 {name=l3 lab=0}
C {vdd.sym} 180 -160 0 0 {name=l4 lab=VDD}
C {gnd.sym} 300 -120 0 0 {name=l5 lab=0}
C {vsource.sym} -350 -280 0 0 {name=VIN value="sin(1.65 1.65 10k)" savecurrent=false}
C {gnd.sym} -350 -250 0 0 {name=l6 lab=0}
C {lab_wire.sym} -350 -330 0 0 {name=p2 sig_type=std_logic lab=VIN}
C {lab_wire.sym} 10 -60 0 0 {name=p1 sig_type=std_logic lab=CLK}
C {lab_wire.sym} 270 -185 0 0 {name=p3 sig_type=std_logic lab=CLK}
C {vsource.sym} -385 40 0 0 {name=VCLK value="pulse(0 3.3 0 1n 1n 0.5u 1u)" savecurrent=false}
C {gnd.sym} -385 70 0 0 {name=l7 lab=0}
C {lab_wire.sym} -385 10 0 0 {name=p5 sig_type=std_logic lab=CLK}
C {gnd.sym} 280 70 0 0 {name=l8 lab=0}
C {gnd.sym} -55 -30 0 0 {name=l9 lab=0}
C {lab_wire.sym} 160 40 0 0 {name=p6 sig_type=std_logic lab=VIN}
C {vdd.sym} -15 -220 0 0 {name=l10 lab=VDD}
C {gnd.sym} 180 -110 0 0 {name=l11 lab=0}
C {gnd.sym} 270 -110 0 0 {name=l12 lab=0}
C {gnd.sym} 115 20 0 0 {name=l13 lab=0}
C {gnd.sym} 200 20 0 0 {name=l14 lab=0}
C {gnd.sym} -65 -60 1 0 {name=l15 lab=0}
C {code.sym} 390 -310 0 0 {name=s1 only_toplevel=false value="
.param mim_corner_1p0fF=1 mim_corner_1p5fF=1 mim_corner_2p0fF=1
.param mc_c_cox_1p0fF=0 mc_c_cox_1p5fF=0 mc_c_cox_2p0fF=0
.param var_vth=0 var_k=0
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice cap_mim
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.options savecurrents
* Simple Ideal Inverter to generate CLKB from CLK for PMOS M8
Ainv1 CLK CLKB ideal_inv
.model ideal_inv d_inverter(rise_delay=1n fall_delay=1n)
.control
save all
tran 2n 3u
plot v(CLK) v(VIN) v(Vc) v(VOUT)
plot V(vbs)-V(vin)
.endc
"}
C {designs/emily_testing/inv1.sym} -285 10 0 0 {name=x1}
C {lab_wire.sym} -355 -60 0 0 {name=p7 sig_type=std_logic lab=VIN}
C {gnd.sym} -355 70 0 0 {name=l16 lab=0}
C {lab_wire.sym} -255 10 0 0 {name=p8 sig_type=std_logic lab=CLK_INV}
C {lab_wire.sym} 60 -55 0 0 {name=p9 sig_type=std_logic lab=CLK_INV}
C {lab_wire.sym} 60 -155 0 0 {name=p10 sig_type=std_logic lab=Vc}
C {lab_wire.sym} -10 -150 0 0 {name=p4 sig_type=std_logic lab=Vc}
C {lab_wire.sym} 280 10 0 0 {name=p11 sig_type=std_logic lab=VOUT}
C {lab_wire.sym} 140 -30 0 0 {name=p12 sig_type=std_logic lab=VBS}
