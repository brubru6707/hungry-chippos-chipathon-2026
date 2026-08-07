v {xschem version=3.4.8RC file_version=1.3}
G {}
K {type=subcircuit
format="@name @pinlist @symname pfet_wid=@pfet_wid nfet_wid=@nfet_wid pfet_len=@pfet_len nfet_len=@nfet_len pfet_m=@pfet_m nfet_m=@nfet_m"
spectre_format="@name ( @pinlist ) @symname"
template="name=x1 pfet_wid=0.84u nfet_wid=0.42u pfet_len=0.28u nfet_len=0.28u pfet_m=1 nfet_m=1"
}
V {}
S {}
F {}
E {}
T {Per-bit bottom-plate CMOS rail driver (VREF=VDD rework, replaces the
old dual-NMOS VREF/GND pass-gate scheme). Single control input bN_bar
(the existing NAND2(B,SAMPLE_N) output from cap_array.sch, reused
directly - HIGH during SAMPLE or bit=0 pulls VOUT to GND; LOW during
CONVERT with bit=1 pulls VOUT to VDD). PMOS pull-up required (an NMOS
pass transistor cannot pull a node to the full VDD rail); PMOS sized 2x
the NMOS pulldown (pfet_wid/nfet_wid, default 0.84u/0.42u) matching the
inv1/nand2/tgate P:N=2:1 mobility-compensation convention already used
elsewhere in this design. This cell is topologically just a sized CMOS
inverter (input bN_bar, output VOUT) - copied from inv1.sch's proven
rot0/flip0 + pin-coincident lab_wire.sym connectivity (plain wire lab=
alone is cosmetic-only per dac/WORKLOG.md Brief #3), then parametrized.
pfet_m/nfet_m (default 1) let the widest bits use parallel multiplicity
instead of raw W: gf180mcuD's binned nfet_03v3/pfet_03v3 models cap out
at W<=100.001u regardless of nf (empirically confirmed - SPICE "nf" only
repartitions parasitic R/C, it does NOT change drive current for a fixed
W, unlike "m" which linearly scales it, same as the m= convention already
used for cap_mim_2f0fF binary weighting elsewhere in this design). The
MSB's PMOS (bit7) needs 107.52u total width > the 100.001u bin ceiling,
so it's built as pfet_wid=53.76u (in-bin) with pfet_m=2 - set per-instance
in cap_array.sch, not here.} -340 -220 0 0 0.2 0.2 {}
N -0 -30 -0 10 {lab=VOUT}
N -60 -60 -40 -60 {lab=bN_bar}
N -60 -60 -60 40 {lab=bN_bar}
N -60 40 -40 40 {lab=bN_bar}
N -0 -60 20 -60 {lab=VDD}
N 20 -100 20 -60 {lab=VDD}
N 0 -100 20 -100 {lab=VDD}
N -0 -100 -0 -90 {lab=VDD}
N -0 40 20 40 {lab=GND}
N 20 40 20 80 {lab=GND}
N 0 80 20 80 {lab=GND}
N -0 70 -0 80 {lab=GND}
N -0 80 0 90 {lab=GND}
N -0 -10 20 -10 {lab=VOUT}
N -80 -10 -60 -10 {lab=bN_bar}
N -0 -110 0 -100 {lab=VDD}
C {symbols/pfet_03v3.sym} -20 -60 0 0 {name=M1
L='pfet_len'
W='pfet_wid'
nf=1
m='pfet_m'
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_03v3
spiceprefix=X
}
C {symbols/nfet_03v3.sym} -20 40 0 0 {name=M2
L='nfet_len'
W='nfet_wid'
nf=1
m='nfet_m'
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_03v3
spiceprefix=X
}
C {ipin.sym} -80 -10 0 0 {name=p1 lab=bN_bar}
C {iopin.sym} 20 -10 0 0 {name=p2 lab=VOUT}
C {iopin.sym} 0 -110 3 0 {name=p3 lab=VDD}
C {iopin.sym} 0 90 1 0 {name=p4 lab=GND}
