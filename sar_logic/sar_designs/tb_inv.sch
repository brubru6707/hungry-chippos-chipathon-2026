v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -450 160 -450 190 {lab=0}
N -450 180 -60 180 {lab=0}
N -60 160 -60 180 {lab=0}
N -350 160 -350 180 {lab=0}
N -350 40 -350 100 {lab=vin}
N -350 40 -260 40 {lab=vin}
N -450 -60 -450 100 {lab=vdd}
N -450 -60 -230 -60 {lab=vdd}
N -230 -60 -230 -30 {lab=vdd}
N -130 40 -60 40 {lab=vout}
N -60 40 -60 100 {lab=vout}
N -230 100 -230 180 {lab=0}
C {vsource.sym} -350 130 0 0 {name=V1 value="0 PULSE('PAR_VDD' 0 PAR_DEL PAR_SLEW PAR_SLEW '0.5*PAR_PER' '1.0*PAR_PER')" savecurrent=false}
C {vsource.sym} -450 130 0 0 {name=Vsup value=PAR_VDD savecurrent=false}
C {capa.sym} -60 130 0 0 {name=C1
m=1
value='PAR_CLOAD'
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} -450 190 0 0 {name=l1 lab=0}
C {lab_pin.sym} -310 -60 0 0 {name=p1 sig_type=std_logic lab=vdd}
C {lab_pin.sym} -290 40 0 0 {name=p2 sig_type=std_logic lab=vin}
C {lab_pin.sym} -80 40 0 0 {name=p3 sig_type=std_logic lab=vout}
C {code_shown.sym} -475 -225 0 0 {name=MODELS only_toplevel=true  
format="tcleval( @value )" 
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/smbb000149.ngspice typical
"}
C {code_shown.sym} 225 -210 0 0 {name=NGSPICE only_toplevel=true  
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
write tb_inv.raw
plot v(vin) v(vout)
.endc

"}
C {inv.sym} -160 40 0 0 {name=x1}
