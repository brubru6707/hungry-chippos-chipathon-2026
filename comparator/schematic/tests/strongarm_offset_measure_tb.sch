v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 770 -830 770 -760 {lab=VIN1}
N 770 -830 940 -830 {lab=VIN1}
N 840 -810 840 -760 {lab=VIN2}
N 840 -810 940 -810 {lab=VIN2}
N 700 -850 700 -760 {lab=CK}
N 700 -850 940 -850 {lab=CK}
N 1080 -830 1210 -830 {lab=OUT1}
N 1080 -810 1170 -810 {lab=OUT2}
C {comparator/schematic/strongarm.sym} 930 -770 0 0 {name=X1}
C {vsource.sym} 840 -730 0 0 {name=VVIN2 value=1.2 savecurrent=false}
C {vsource.sym} 770 -730 0 0 {name=VVIN1 value="PWL(0 1.23 6u 1.17)" savecurrent=false}
C {vsource.sym} 630 -730 0 0 {name=VDD value=3 savecurrent=false}
C {vsource.sym} 700 -730 0 0 {name=VCK value="PULSE(0 3 0 100p 100p 10n 20n)" savecurrent=false}
C {title.sym} 180 -60 0 0 {name=l1 author="Bruno R.M."}
C {gnd.sym} 700 -700 0 0 {name=l2 lab=0}
C {gnd.sym} 630 -700 0 0 {name=l3 lab=0}
C {gnd.sym} 770 -700 0 0 {name=l4 lab=0}
C {gnd.sym} 840 -700 0 0 {name=l5 lab=0}
C {vdd.sym} 1080 -850 1 0 {name=l6 lab=VDD}
C {vdd.sym} 630 -760 0 0 {name=l7 lab=VDD}
C {gnd.sym} 1080 -790 3 0 {name=l8 lab=0}
C {noconn.sym} 1170 -810 0 1 {name=l9}
C {noconn.sym} 1210 -830 0 1 {name=l10}
C {lab_wire.sym} 1190 -830 0 0 {name=p2 sig_type=std_logic lab=OUT1}
C {lab_wire.sym} 1120 -810 2 0 {name=p5 sig_type=std_logic lab=OUT2}
C {devices/code_shown.sym} 690 -1010 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.param sw_stat_global   = 0
.param sw_stat_mismatch = 0
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {devices/code_shown.sym} -140 -1290 0 0 {name=NGSPICE only_toplevel=true
value="
.control
* ---- systematic-offset test: mismatch OFF, no injected offset, deterministic ----
alter vvin2 = 1.2
alter @m.x1.xm10.m0[delvto] = 0
alter @m.x1.xm8.m0[delvto]  = 0

* ===== UP sweep: VIN1 1.15 -> 1.25 =====
alter @vvin1[pwl] = [ 0 1.15 6e-6 1.25 ]
tran 10p 6u
meas tran ta when v(out1)=1.5 fall=1
meas tran tb when v(out1)=1.5 fall=LAST
meas tran va find v(vin1) at=ta
meas tran vb find v(vin1) at=tb
* keep whichever crossing is the real trip (nearest mid-scale, not a ramp end)
if abs(va-1.2) < abs(vb-1.2)
  let vup = va
else
  let vup = vb
end
destroy $curplot

* ===== DOWN sweep: VIN1 1.25 -> 1.15 =====
alter @vvin1[pwl] = [ 0 1.25 6e-6 1.15 ]
tran 10p 6u
meas tran tc when v(out1)=1.5 fall=1
meas tran td when v(out1)=1.5 fall=LAST
meas tran vc find v(vin1) at=tc
meas tran vd find v(vin1) at=td
if abs(vc-1.2) < abs(vd-1.2)
  let vdn = vc
else
  let vdn = vd
end
destroy $curplot

let systematic = ((vup-1.2) + (vdn-1.2))/2
print vup vdn systematic
.endc
"}
C {lab_wire.sym} 700 -850 0 0 {name=p1 sig_type=std_logic lab=CK}
C {lab_wire.sym} 770 -800 0 0 {name=p3 sig_type=std_logic lab=VIN1}
C {lab_wire.sym} 840 -770 0 0 {name=p4 sig_type=std_logic lab=VIN2}