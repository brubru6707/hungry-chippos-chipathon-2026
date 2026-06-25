v {xschem version=3.4.8RC file_version=1.3}
** PROBLEM THAT BOOTSTRAP SOLVES
G {}
K {}
V {}
S {}
F {}
E {}
N -200 100 360 100 {lab=0}
N 360 -10 360 40 {lab=vout}
N 280 -10 360 -10 {lab=vout}
N 90 -50 90 -40 {lab=vout}
N 250 -10 280 -10 {lab=vout}
N 90 -10 180 -10 {lab=0}
N 90 -70 90 -40 {lab=vout}
N 90 -70 250 -70 {lab=vout}
N 250 -70 250 -10 {lab=vout}
N -200 20 90 20 {lab=vin}
N -200 20 -200 40 {lab=vin}
N -120 -10 -120 40 {lab=clk}
N -120 -10 50 -10 {lab=clk}
C {vsource.sym} -120 70 0 0 {name=V1 value="pulse(0 3.3 0 1n 1n 0.5u 1u)" savecurrent=false}
C {vsource.sym} -200 70 0 0 {name=Vsup value="sin(1.65 1.65 10k)" savecurrent=false}
C {capa.sym} 360 70 0 0 {name=C1 m=1 value=13p footprint=1206 device="ceramic capacitor"}
C {gnd.sym} 40 100 0 0 {name=l1 lab=0}
C {gnd.sym} 180 -10 0 0 {name=l2 lab=0}
C {symbols/nfet_03v3.sym} 70 -10 0 0 {name=M1
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
C {code.sym} 360 -110 0 0 {name=s1 only_toplevel=false value="
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice nfet_03v3_t
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice fets_mm
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.param var_vth=0 var_k=0
.options savecurrents
.control
  save all
  tran 2n 3u
  let clk = v(net3)
  let vin = v(net2)
  let vout = v(net1)
  plot clk vin vout
.endc
"}