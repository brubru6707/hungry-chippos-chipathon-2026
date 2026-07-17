v {xschem version=3.4.8RC file_version=1.3}
G {}
K {type=subcircuit
format="@name @pinlist @symname nfet_wid=@nfet_wid pfet_wid=@pfet_wid nfet_len=@nfet_len pfet_len=@pfet_len"
spectre_format="@name ( @pinlist ) @symname"
template="name=x1 nfet_wid=0.85u pfet_wid=3.4u nfet_len=0.3u pfet_len=0.3u"
}
V {}
S {}
F {}
E {}
T {2-input NOR (DAC SAMPLE-gating, Brief #5). Two NMOS in parallel
(source=DVSS, drain=y, gates=a,b) at normal inv1 nfet width (nfet_wid,
default 0.85u). Two PMOS in series (top: source=DVDD gate=a drain=mid;
bottom: source=mid gate=b drain=y) sized ~2x single-inverter PMOS
width (pfet_wid, default 3.4u = 2x1.7u) to compensate series
resistance. Connectivity is via pin-coincident lab_wire.sym / ipin /
opin / iopin only (no drawn N wires) - see nand2.sch header comment
and dac/WORKLOG.md 2026-07-17 Brief #3 entry for why.} -320 -180 0 0 0.2 0.2 {}
C {symbols/pfet_03v3.sym} 0 0 0 0 {name=M1
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
C {symbols/pfet_03v3.sym} 0 150 0 0 {name=M2
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
C {symbols/nfet_03v3.sym} 250 0 0 0 {name=M3
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
C {symbols/nfet_03v3.sym} 250 150 0 0 {name=M4
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
C {lab_wire.sym} -20 0 0 0 {name=lp1a sig_type=std_logic lab=a}
C {lab_wire.sym} 20 30 0 0 {name=lp1d sig_type=std_logic lab=mid}
C {lab_wire.sym} 20 -30 0 0 {name=lp1s sig_type=std_logic lab=DVDD}
C {lab_wire.sym} 20 0 0 0 {name=lp1bulk sig_type=std_logic lab=DVDD}
C {lab_wire.sym} -20 150 0 0 {name=lp2b sig_type=std_logic lab=b}
C {lab_wire.sym} 20 180 0 0 {name=lp2y sig_type=std_logic lab=y}
C {lab_wire.sym} 20 120 0 0 {name=lp2s sig_type=std_logic lab=mid}
C {lab_wire.sym} 20 150 0 0 {name=lp2bulk sig_type=std_logic lab=DVDD}
C {lab_wire.sym} 230 0 0 0 {name=ln1a sig_type=std_logic lab=a}
C {lab_wire.sym} 270 -30 0 0 {name=ln1y sig_type=std_logic lab=y}
C {lab_wire.sym} 270 30 0 0 {name=ln1s sig_type=std_logic lab=DVSS}
C {lab_wire.sym} 270 0 0 0 {name=ln1bulk sig_type=std_logic lab=DVSS}
C {lab_wire.sym} 230 150 0 0 {name=ln2b sig_type=std_logic lab=b}
C {lab_wire.sym} 270 120 0 0 {name=ln2y sig_type=std_logic lab=y}
C {lab_wire.sym} 270 180 0 0 {name=ln2s sig_type=std_logic lab=DVSS}
C {lab_wire.sym} 270 150 0 0 {name=ln2bulk sig_type=std_logic lab=DVSS}
C {ipin.sym} -150 0 0 0 {name=pa lab=a}
C {ipin.sym} -150 150 0 0 {name=pb lab=b}
C {opin.sym} 350 -30 0 0 {name=py lab=y}
C {iopin.sym} -150 -30 0 0 {name=pDVDD lab=DVDD}
C {iopin.sym} -150 220 0 0 {name=pDVSS lab=DVSS}
