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
let mc_runs = 300
let run = 0
let offset_results = vector(mc_runs)
set curplotenv = $curplot

* 1-sigma Vth mismatch per input device (volts).
* Placeholder 3 mV - set from GF180 AVT / sqrt(W*L) for a real spec.
let svt = 3.0e-3

dowhile run < mc_runs
  echo ---- run $&run ----

  * One random device sample per run, applied ONCE so the UP and DOWN
  * sweeps both see the SAME mismatch (that is what makes the average valid).
  alter @m.x1.xm10.m0[delvto] = svt * sgauss(0)
  alter @m.x1.xm8.m0[delvto]  = svt * sgauss(0)

  unset s_up
  unset s_dn

  * ---------------- UP sweep: VIN1 1.17 -> 1.23 ----------------
  * Rising sweep: out1 falls every cycle BELOW the trip, so the
  * trip point is the LAST falling edge.
  alter @vvin1[pwl] = [ 0 1.17 6e-6 1.23 ]
  tran 10p 6u
  let t_up = -1
  meas tran t_up when v(out1)=1.5 fall=LAST
  if t_up > 0
    meas tran vin_up find v(vin1) at=t_up
    let off_up = vin_up - 1.200
    set s_up = $&off_up
  end
  destroy $curplot

  * --------------- DOWN sweep: VIN1 1.23 -> 1.17 ---------------
  * Falling sweep: out1 only starts falling once VIN1 drops BELOW the
  * trip, so the trip point is the FIRST falling edge (not the last!).
  alter @vvin1[pwl] = [ 0 1.23 6e-6 1.17 ]
  tran 10p 6u
  let t_dn = -1
  meas tran t_dn when v(out1)=1.5 fall=1
  if t_dn > 0
    meas tran vin_dn find v(vin1) at=t_dn
    let off_dn = vin_dn - 1.200
    set s_dn = $&off_dn
  end
  destroy $curplot

  * --------- combine: true offset = midpoint of the two sweeps ---------
  if ( $?s_up * $?s_dn ) = 1
    let offset_results[run] = ( ($s_up) + ($s_dn) ) / 2
    echo   up=$s_up  dn=$s_dn
  else
    let offset_results[run] = -999
    echo   WARN: missing trip on run $&run
  end

  let run = run + 1
end

setplot $curplotenv
let mu  = mean(offset_results)
let sig = sqrt(mean((offset_results - mu)^2))
echo ========================================
echo MC done (N=$&mc_runs): mean=$&mu V  sigma=$&sig V
echo ========================================
write  comp_mc_offsets.raw offset_results
unset  wr_singlescale
wrdata comp_mc_offsets.txt offset_results
.endc
"}
C {lab_wire.sym} 700 -850 0 0 {name=p1 sig_type=std_logic lab=CK}
C {lab_wire.sym} 770 -800 0 0 {name=p3 sig_type=std_logic lab=VIN1}
C {lab_wire.sym} 840 -770 0 0 {name=p4 sig_type=std_logic lab=VIN2}