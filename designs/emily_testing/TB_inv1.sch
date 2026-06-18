v {xschem version=3.4.8RC file_version=1.3}
G {}
K {type=subcircuit
format="@name @pinlist @symname"
spectre_format="@name ( @pinlist ) @symname"
template="name=x1"
}
V {}
S {}
F {}
E {}
L 4 -90 -20 -70 -20 {}
L 4 -70 -70 -10 -20 {}
L 4 -70 -70 -70 30 {}
L 4 -70 30 -10 -20 {}
L 4 10 -20 30 -20 {}
L 7 -70 -90 -70 -70 {}
L 7 -70 30 -70 50 {}
B 5 -72.5 -92.5 -67.5 -87.5 {name=DVDD dir=inout}
B 5 27.5 -22.5 32.5 -17.5 {name=vout dir=inout}
B 5 -92.5 -22.5 -87.5 -17.5 {name=vin dir=in}
B 5 -72.5 47.5 -67.5 52.5 {name=DVSS dir=inout}
A 4 0 -15 11.18033988749895 26.56505117707799 360 {}
T {x1} -35 -52 0 0 0.2 0.2 {}
T {DVDD} -74 -65 3 1 0.2 0.2 {}
T {vout} 35 6 0 1 0.2 0.2 {}
T {vin} -65 -14 0 0 0.2 0.2 {}
T {DVSS} -36 55 1 1 0.2 0.2 {}
N -240 80 90 80 {lab=0}
N 90 60 90 80 {lab=0}
N -170 70 -170 80 {lab=0}
N -240 80 -230 80 {lab=0}
N -170 -20 -170 20 {lab=vin}
N -170 -20 -90 -20 {lab=vin}
N -240 -120 -240 20 {lab=dvdd}
N -240 -120 -70 -120 {lab=dvdd}
N -70 -120 -70 -90 {lab=dvdd}
N 30 -20 90 -20 {lab=vout}
N 90 -20 90 -0 {lab=vout}
N -70 50 -70 80 {lab=0}
N -65 80 -55 80 {lab=0}
N -240 80 -195 80 {lab=0}
N -70 30 -70 50 {lab=0}
N -70 45 -70 50 {lab=0}
N -170 10 -170 25 {lab=vin}
N -240 -5 -240 20 {lab=dvdd}
N -240 -5 -240 30 {lab=dvdd}
N -100 -20 -90 -20 {lab=vin}
N -90 -20 -85 -20 {lab=vin}
N -70 -90 -70 -75 {lab=dvdd}
N -70 -100 -70 -90 {lab=dvdd}
N 90 -15 90 -0 {lab=vout}
N 90 -0 90 15 {lab=vout}
N 90 40 90 60 {lab=0}
N 90 60 90 70 {lab=0}
C {vsource.sym} -170 50 0 0 {name=V1 value="0 PULSE('PAR_VDD' 0 PAR_DEL PAR_SLEW PAR_SLEW '0.5*PAR_PER' '1.0*PAR_PER')" savecurrent=false}
C {vsource.sym} -240 50 0 0 {name=Vsup value=PAR_VDD savecurrent=false}
C {capa.sym} 90 30 0 0 {name=C1
m=1
value='PAR_CLOAD'
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} -160 -120 0 0 {name=p1 sig_type=std_logic lab=dvdd
}
C {lab_pin.sym} -120 -20 0 0 {name=p2 sig_type=std_logic lab=vin
}
C {lab_pin.sym} 70 -20 0 0 {name=p3 sig_type=std_logic lab=vout
}
C {code.sym} -100 -250 0 0 {name=MODELS only_toplevel=true  
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/smbb000149.ngspice typical
"}
C {code.sym} 150 -180 0 0 {name=NGSPICE only_toplevel=true  
value="
** PARAMETERS
.PARAM PAR_VDD=3.3
.PARAM PAR_CLOAD=100f
.PARAM PAR_SLEW=100p
.PARAM PAR_PER=10n
.PARAM PAR_DEL='0.1*PAR_PER'

** Rise/Fall 10-90%
.MEASURE TRAN tr1090 TRIG v(vout) VAL='0.1*PAR_VDD' RISE=1 TARG v(vout) VAL='0.9*PAR_VDD' RISE=1
.MEASURE TRAN tf9010 TRIG v(vout) VAL='0.9*PAR_VDD' FALL=1 TARG v(vout) VAL='0.1*PAR_VDD' FALL=1

** Delay Rise Fall
.MEASURE TRAN tdrise TRIG v(vin)  VAL='0.5*PAR_VDD' FALL=1 TARG v(vout) VAL='0.5*PAR_VDD' RISE=1
.MEASURE TRAN tdfall TRIG v(vin)  VAL='0.5*PAR_VDD' RISE=1 TARG v(vout) VAL='0.5*PAR_VDD' FALL=1

**Leakage current and average current
.MEASURE TRAN iavg AVG vsup#branch FROM=PAR_DEL TO='PAR_DEL+PAR_PER'
.MEASURE TRAN ileak AVG vsup#branch FROM='PAR_DEL+0.4*PAR_PER' TO='PAR_DEL+0.45*PAR_PER'

.control
save all
OP
TRAN 1p 21n
write TB_inv1.raw
plot v(vin) v(vout)
.endc

"}
C {gnd.sym} -55 80 0 0 {name=l2 lab=0}
C {vsource.sym} -410 140 0 0 {name=Vsup1 value=PAR_VDD savecurrent=false}
C {vsource.sym} -400 140 0 0 {name=Vsup2 value=PAR_VDD savecurrent=false}
