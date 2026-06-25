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
C {vsource.sym} 770 -730 0 0 {name=VVIN1 value="PWL(0 0.9 60n 1.5)" savecurrent=false}
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
.param sw_stat_global = 1
.param sw_stat_mismatch = 1

.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {devices/code_shown.sym} -140 -1290 0 0 {name=NGSPICE only_toplevel=true
value="
.control
let mc_runs = 200
let run = 1

* Create a vector in the global control plot to store offset measurements
set curplatenv = $curplot
let offset_results = unitvec(mc_runs) * -999

* Start monte carlo loop
while run <= mc_runs
  reset

  * Run transient simulation
  tran 10p 60n

  * Capture this iteration's plot name
  set current_tran = $curplot

  * FIX 1: compute difference vector to avoid the vexprint1 parser bug
  * when v(out1)=v(out2) causes NGSpice to mangle the RHS into 'vexprint1'
  let vdiff = v(out1) - v(out2)

  * Measure the zero-crossing of the difference vector
  meas tran trip_time when vdiff=0 cross=1

  * FIX 2: evaluate run to a plain integer before arithmetic
  * $& forces immediate integer evaluation; plain 'idx' loses scope across setplot
  let idx = $&run - 1

  if $?trip_time

    * Find VIN1 voltage at the crossing time
    meas tran v_in_at_trip find v(vin1) at=trip_time
    let current_offset = v_in_at_trip - 1.200

    * Switch to the global plot for array write
    setplot $curplatenv

    * FIX 3: use $&idx (forced integer) in array index and cross-plot ref
    let offset_results[$&idx] = {$current_tran}.current_offset

  else

    * Comparator did not latch; sentinel already set, just switch plot
    setplot $curplatenv

  end

  let run = run + 1
end

* Return to the global plot and dump results
setplot $curplatenv
write comp_mc_offsets.raw offset_results
print offset_results
.endc
"}
C {lab_wire.sym} 700 -850 0 0 {name=p1 sig_type=std_logic lab=CK}
C {lab_wire.sym} 770 -800 0 0 {name=p3 sig_type=std_logic lab=VIN1}
C {lab_wire.sym} 840 -770 0 0 {name=p4 sig_type=std_logic lab=VIN2}