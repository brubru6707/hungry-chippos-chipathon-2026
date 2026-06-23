v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 770 -830 940 -830 {lab=VIN1}
N 480 -850 480 -760 {lab=CK}
N 1080 -830 1210 -830 {lab=OUT1}
N 1080 -810 1170 -810 {lab=OUT2}
N 770 -830 770 -700 {lab=VIN1}
N 940 -810 940 -590 {lab=VIN2}
N 480 -850 940 -850 {lab=CK}
C {comparator/schematic/strongarm.sym} 930 -770 0 0 {name=X1}
C {vsource.sym} 940 -560 0 0 {name=VVIN2 value=1.2 savecurrent=false}
C {vsource.sym} 770 -670 0 0 {name=VVIN1 value="PWL(0 1.23 6u 1.17)" savecurrent=false}
C {vsource.sym} 410 -730 0 0 {name=VDD value=3 savecurrent=false}
C {vsource.sym} 480 -730 0 0 {name=VCK value="PULSE(0 3 0 100p 100p 10n 20n)" savecurrent=false}
C {title.sym} 180 -60 0 0 {name=l1 author="Bruno R.M."}
C {gnd.sym} 480 -700 0 0 {name=l2 lab=0}
C {gnd.sym} 410 -700 0 0 {name=l3 lab=0}
C {gnd.sym} 770 -640 0 0 {name=l4 lab=0}
C {gnd.sym} 940 -530 0 0 {name=l5 lab=0}
C {vdd.sym} 1080 -850 1 0 {name=l6 lab=VDD}
C {vdd.sym} 410 -760 0 0 {name=l7 lab=VDD}
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
C {devices/code_shown.sym} -150 -1320 0 0 {name=NGSPICE only_toplevel=true
value="
.control
let mc_runs = 10
set curplotenv = $curplot
unset wr_singlescale

* 1-sigma Vth mismatch per input device (volts).
let svt = 3.0e-3

* common-mode points to test
compose vcm_list values 1.0 1.2 1.4

* storage for the per-VCM results (printed all together at the end)
let mu_list  = vector(length(vcm_list))
let sig_list = vector(length(vcm_list))

let ci = 0
dowhile ci < length(vcm_list)
  let vcm = vcm_list[ci]
  set svcm = $&vcm
  let vlo = vcm - 0.05
  let vhi = vcm + 0.05
  set svlo = $&vlo
  set svhi = $&vhi

  alter vvin2 = $svcm

  let offset_results = vector(mc_runs)
  let run = 0
  echo ########## VCM = $svcm V ##########

  dowhile run < mc_runs
    alter @m.x1.xm10.m0[delvto] = svt * sgauss(0)
    alter @m.x1.xm8.m0[delvto]  = svt * sgauss(0)

    unset s_up
    unset s_dn

    * ---- UP sweep ; trip = LAST fall ----
    alter @vvin1[pwl] = [ 0 $svlo 6e-6 $svhi ]
    tran 10p 6u
    let t_up = -1
    meas tran t_up when v(out1)=1.5 fall=LAST
    if t_up > 0
      meas tran vin_up find v(vin1) at=t_up
      let off_up = vin_up - $svcm
      set s_up = $&off_up
    end
    destroy $curplot

    * ---- DOWN sweep ; trip = FIRST fall ----
    alter @vvin1[pwl] = [ 0 $svhi 6e-6 $svlo ]
    tran 10p 6u
    let t_dn = -1
    meas tran t_dn when v(out1)=1.5 fall=1
    if t_dn > 0
      meas tran vin_dn find v(vin1) at=t_dn
      let off_dn = vin_dn - $svcm
      set s_dn = $&off_dn
    end
    destroy $curplot

    if ( $?s_up * $?s_dn ) = 1
      let offset_results[run] = ( ($s_up) + ($s_dn) ) / 2
    else
      let offset_results[run] = -999
    end

    let run = run + 1
  end

  * ---- stats for this common mode ----
  setplot $curplotenv
  let mu  = mean(offset_results)
  let sig = sqrt(mean((offset_results - mu)^2))
  let mu_list[ci]  = mu
  let sig_list[ci] = sig
  let ci = ci + 1
end

* ===== final summary: all VCM points together, at the very bottom =====
setplot $curplotenv
echo
echo ========== COMMON-MODE SWEEP SUMMARY ==========
let k = 0
dowhile k < length(vcm_list)
  let onev   = vcm_list[k]
  let onemu  = mu_list[k]
  let onesig = sig_list[k]
  echo VCM= $&onev V   systematic= $&onemu V   sigma= $&onesig V
  let k = k + 1
end
echo ===============================================
.endc
"}
C {lab_wire.sym} 510 -850 0 0 {name=p1 sig_type=std_logic lab=CK}
C {lab_wire.sym} 770 -800 0 0 {name=p3 sig_type=std_logic lab=VIN1}
C {lab_wire.sym} 940 -600 0 0 {name=p4 sig_type=std_logic lab=VIN2}
