v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -305 -170 -305 -140 {lab=0}
N -305 -150 35 -150 {lab=0}
N 35 -170 35 -150 {lab=0}
N -215 -170 -215 -150 {lab=0}
N -215 -320 -215 -230 {lab=vin}
N -215 -320 -165 -320 {lab=vin}
N -140 -255 -140 -150 {lab=0}
N -305 -410 -305 -230 {lab=dvdd}
N -137.5 -415 -137.5 -377.5 {lab=dvdd}
N -305 -415 -137.5 -415 {lab=dvdd}
N -305 -415 -305 -410 {lab=dvdd}
N -45 -320 35 -320 {lab=vout}
N 35 -320 35 -230 {lab=vout}
C {Tutorials/inv1.sym} -85 -270 0 0 {name=x1}
C {vsource.sym} -305 -200 0 0 {name=Vsup value='PAR_VDD' savecurrent=false}
C {vsource.sym} -215 -200 0 0 {name=Vpulse value="0 PULSE('PAR_VDD' 0 PAR_DEL PAR_SLEW PAR_SLEW '0.5*PAR_PER' '1.0*PAR_PER')"
savecurrent=false}
C {capa.sym} 35 -200 0 0 {name=C1
m=1
value='PAR_CLOAD'
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} -305 -140 0 0 {name=l1 lab=0}
C {lab_pin.sym} -225 -415 0 0 {name=p1 sig_type=std_logic lab=dvdd}
C {lab_pin.sym} -190 -320 0 0 {name=p2 sig_type=std_logic lab=vin}
C {lab_pin.sym} 10 -320 0 0 {name=p3 sig_type=std_logic lab=vout}
C {code_shown.sym} -360 -540 0 0 {name=MODELS only_toplevel=false 
value="
.include \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/design.ngspice\\"
.lib \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/sm141064.ngspice\\" typical
.lib \\"$PDK_ROOT/gf180mcuD/libs.tech/ngspice/smbb000149.ngspice\\" typical
"}
C {code_shown.sym} 305 -545 0 0 {name=NGSPICE only_toplevel=false 
value="
**PARAMETERS
.PARAM PAR_VDD=3.3
.PARAM PAR_CLOAD=10f
.PARAM PAR_SLEW=100p
.PARAM PAR_PER=10n
.PARAM PAR_DEL='0.1*PAR_PER'

** Rise/Fall 10-90%
.MEASURE TRAN tr1090 TRIG v(vout) VAL='0.1*PAR_VDD' RISE=1 TARG v(vout) VAL='0.9*PAR_VDD' RISE=1
.MEASURE TRAN tf9010 TRIG v(vout) VAL='0.9*PAR_VDD' FALL=1 TARG v(vout) VAL='0.1*PAR_VDD' FALL=1

** Delay Rise Fall
.MEASURE TRAN tdrise TRIG v(vin) VAL='0.5*PAR_VDD' FALL=1 TARG v(vout) VAL='0.5*PAR_VDD' RISE=1
.MEASURE TRAN tdfall TRIG v(vin) VAL='0.5*PAR_VDD' RISE=1 TARG v(vout) VAL='0.5*PAR_VDD' FALL=1

**Leakage current and average current
.MEASURE TRAN iavg AVG	vsup#branch FROM=PAR_DEL TO='PAR_DEL+PAR_PER'
.MEASURE TRAN ileak AVG	vsup#branch FROM='PAR_DEL+0.4*PAR_PER' TO='PAR_DEL+0.45*PAR_PER'

.control
  save all
  OP
  TRAN 1p 21n
  write tb_inv1.raw
  plot v(vin) v(vout)
.endc
" }
