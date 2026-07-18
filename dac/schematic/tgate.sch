v {xschem version=3.4.8RC file_version=1.3}
G {}
K {type=subcircuit
format="@name @pinlist @symname pfet_wid=@pfet_wid nfet_wid=@nfet_wid pfet_len=@pfet_len nfet_len=@nfet_len"
spectre_format="@name ( @pinlist ) @symname"
template="name=x1 pfet_wid=1.7u nfet_wid=1.7u pfet_len=0.28u nfet_len=0.28u"
}
V {}
S {}
F {}
E {}
T {Transmission gate (Brief #9/#10 top-plate sampling switch). Parallel
nfet_03v3 (gate=SAMPLE) + pfet_03v3 (gate=SAMPLE_N), sized via
nfet_wid/pfet_wid params like unit_switch/nand2/nor2 so it can be
resized later. Complementary devices avoid the single-ended
near-rail Vgs-collapse failure that killed both the NMOS-only
bottom-plate switch (Brief #6) and the bootstrap switch's
VIN-referenced CLK_INV pump (Brief #9). Connectivity via
pin-coincident lab_wire.sym only, same convention as nand2/nor2.} -320 -180 0 0 0.2 0.2 {}
C {symbols/nfet_03v3.sym} 0 0 0 0 {name=M1
L='nfet_len'
W='nfet_wid'
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
C {symbols/pfet_03v3.sym} 200 0 0 0 {name=M2
L='pfet_len'
W='pfet_wid'
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
C {lab_wire.sym} -20 0 0 0 {name=lm1g sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} 20 -30 0 0 {name=lm1d sig_type=std_logic lab=A}
C {lab_wire.sym} 20 30 0 0 {name=lm1s sig_type=std_logic lab=B}
C {lab_wire.sym} 20 0 0 0 {name=lm1b sig_type=std_logic lab=DVSS}
C {lab_wire.sym} 180 0 0 0 {name=lm2g sig_type=std_logic lab=SAMPLE_N}
C {lab_wire.sym} 220 30 0 0 {name=lm2d sig_type=std_logic lab=B}
C {lab_wire.sym} 220 -30 0 0 {name=lm2s sig_type=std_logic lab=A}
C {lab_wire.sym} 220 0 0 0 {name=lm2b sig_type=std_logic lab=DVDD}
C {iopin.sym} -200 -100 0 0 {name=pa lab=A}
C {iopin.sym} -200 -60 0 0 {name=pb lab=B}
C {ipin.sym} -200 -20 0 0 {name=psample lab=SAMPLE}
C {ipin.sym} -200 20 0 0 {name=psamplen lab=SAMPLE_N}
C {iopin.sym} -200 60 0 0 {name=pdvdd lab=DVDD}
C {iopin.sym} -200 100 0 0 {name=pdvss lab=DVSS}
