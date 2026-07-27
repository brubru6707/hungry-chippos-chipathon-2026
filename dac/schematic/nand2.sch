v {xschem version=3.4.8RC file_version=1.3}
G {}
K {type=subcircuit
format="@name @pinlist @symname pfet_wid=@pfet_wid nfet_wid=@nfet_wid pfet_len=@pfet_len nfet_len=@nfet_len"
spectre_format="@name ( @pinlist ) @symname"
template="name=x1 pfet_wid=1.7u nfet_wid=1.7u pfet_len=0.3u nfet_len=0.3u"
}
V {}
S {}
F {}
E {}
T {2-input NAND (DAC SAMPLE-gating, Brief #5). Two PMOS in parallel
(source=DVDD, drain=y, gates=a,b) at normal inv1 pfet width (pfet_wid,
default 1.7u). Two NMOS in series (top: drain=y gate=a source=mid;
bottom: drain=mid gate=b source=DVSS) sized ~2x single-inverter NMOS
width (nfet_wid, default 1.7u = 2x0.85u) to compensate series
resistance and keep fall time comparable to a single inverter stage.
Connectivity is via pin-coincident lab_wire.sym / ipin / opin / iopin
only (no drawn N wires) - each component's single pin is placed
exactly at the transistor pin coordinate it represents, and same-lab
components merge sheet-wide per the established cap_array.sch
convention (see dac/WORKLOG.md 2026-07-17 Brief #3 entry: plain wire
lab= is cosmetic-only; only real label-type components merge nets).} -320 -180 0 0 0.2 0.2 {}
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
C {symbols/nfet_03v3.sym} 0 200 0 0 {name=M3
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
C {symbols/nfet_03v3.sym} 0 350 0 0 {name=M4
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
C {lab_wire.sym} 20 30 0 0 {name=lp1y sig_type=std_logic lab=y}
C {lab_wire.sym} 20 -30 0 0 {name=lp1s sig_type=std_logic lab=DVDD}
C {lab_wire.sym} 20 0 0 0 {name=lp1bulk sig_type=std_logic lab=DVDD}
C {lab_wire.sym} 180 0 0 0 {name=lp2b sig_type=std_logic lab=b}
C {lab_wire.sym} 220 30 0 0 {name=lp2y sig_type=std_logic lab=y}
C {lab_wire.sym} 220 -30 0 0 {name=lp2s sig_type=std_logic lab=DVDD}
C {lab_wire.sym} 220 0 0 0 {name=lp2bulk sig_type=std_logic lab=DVDD}
C {lab_wire.sym} -20 200 0 0 {name=ln1a sig_type=std_logic lab=a}
C {lab_wire.sym} 20 170 0 0 {name=ln1y sig_type=std_logic lab=y}
C {lab_wire.sym} 20 230 0 0 {name=ln1s sig_type=std_logic lab=mid}
C {lab_wire.sym} 20 200 0 0 {name=ln1bulk sig_type=std_logic lab=DVSS}
C {lab_wire.sym} -20 350 0 0 {name=ln2b sig_type=std_logic lab=b}
C {lab_wire.sym} 20 320 0 0 {name=ln2d sig_type=std_logic lab=mid}
C {lab_wire.sym} 20 380 0 0 {name=ln2s sig_type=std_logic lab=DVSS}
C {lab_wire.sym} 20 350 0 0 {name=ln2bulk sig_type=std_logic lab=DVSS}
C {ipin.sym} -200 0 0 0 {name=pa lab=a}
C {ipin.sym} -200 350 0 0 {name=pb lab=b}
C {opin.sym} 300 30 0 0 {name=py lab=y}
C {iopin.sym} -200 -30 0 0 {name=pDVDD lab=DVDD}
C {iopin.sym} -200 380 0 0 {name=pDVSS lab=DVSS}
