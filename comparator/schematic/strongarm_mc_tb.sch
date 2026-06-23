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
* ============================================================
* StrongArm comparator — input-referred offset Monte Carlo
* offset = midpoint of UP-sweep and DOWN-sweep trip points.
* RULE: never put '>' inside a 'let' — ngspice reads it as a file
* redirect. Comparisons are only safe inside 'if'.
* MODELS block must have: sw_stat_mismatch=0, sw_stat_global=0
* ============================================================

let mc_runs = 100
let svt     = 24.8e-3
let run     = 0
let offset_results = vector(mc_runs)
let ngood = 0
let sumx  = 0
let sumx2 = 0
set homeplot = $curplot

dowhile run < mc_runs
  echo ---- run $&run ----
  unset s_up
  unset s_dn

  * fresh mismatch draw, applied to both sweeps
  alter @m.x1.xm10.m0[delvto] = svt * sgauss(0)
  alter @m.x1.xm8.m0[delvto]  = svt * sgauss(0)

  * -------- UP sweep: VIN1 1.05 -> 1.35 --------
  alter @vvin1[pwl] = [ 0 1.05 6e-6 1.35 ]
  tran 10p 6u
  let t_up = -1
  meas tran t_up when v(out1)=1.5 fall=LAST
  if t_up > 0
    meas tran vin_up find v(vin1) at=t_up
    set s_up = $&vin_up
  end
  destroy $curplot

  * -------- DOWN sweep: VIN1 1.35 -> 1.05 --------
  alter @vvin1[pwl] = [ 0 1.35 6e-6 1.05 ]
  tran 10p 6u
  let t_dn = -1
  meas tran t_dn when v(out1)=1.5 fall=1
  if t_dn > 0
    meas tran vin_dn find v(vin1) at=t_dn
    set s_dn = $&vin_dn
  end
  destroy $curplot

  * -------- combine, back in the home plot --------
  setplot $homeplot
  if $?s_up * $?s_dn
    let cur = (($s_up - 1.2) + ($s_dn - 1.2)) / 2
    let offset_results[run] = cur
    let ngood = ngood + 1
    let sumx  = sumx  + cur
    let sumx2 = sumx2 + cur*cur
    echo   up=$s_up dn=$s_dn offset=$&cur
  else
    let offset_results[run] = -999
    echo   WARN: miss on run $&run
  end

  let run = run + 1
end

* ================= stats (valid runs only) =================
setplot $homeplot
let mu  = sumx / ngood
let sig = sqrt( sumx2/ngood - mu*mu )
echo ======================================================
echo MC done: N=$&mc_runs  good=$&ngood
echo   mean offset = $&mu V
echo   sigma       = $&sig V
echo ======================================================

unset wr_singlescale
write  /foss/designs/comparator/comp_mc_offsets.raw offset_results
wrdata /foss/designs/comparator/comp_mc_offsets.txt offset_results
echo MC N=$&mc_runs good=$&ngood mean=$&mu sigma=$&sig > /foss/designs/comparator/comp_mc_report.txt
print offset_results >> /foss/designs/comparator/comp_mc_report.txt
.endc
"}
C {lab_wire.sym} 700 -850 0 0 {name=p1 sig_type=std_logic lab=CK}
C {lab_wire.sym} 770 -800 0 0 {name=p3 sig_type=std_logic lab=VIN1}
C {lab_wire.sym} 840 -770 0 0 {name=p4 sig_type=std_logic lab=VIN2}