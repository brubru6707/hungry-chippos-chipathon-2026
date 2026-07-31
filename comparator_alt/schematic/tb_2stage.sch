v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {title.sym} 60 -30 0 0 {name=l1 author="Luc Bastien"}
C {lab_pin.sym} 60 -170 0 0 {name=p1 sig_type=std_logic lab=VIN2}
C {lab_pin.sym} 60 -150 0 0 {name=p2 sig_type=std_logic lab=VIN1}
C {lab_pin.sym} 60 -130 0 0 {name=p3 sig_type=std_logic lab=CK}
C {lab_pin.sym} 360 -190 2 0 {name=p4 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 360 -170 2 0 {name=p5 sig_type=std_logic lab=VOUT2}
C {lab_pin.sym} 360 -150 2 0 {name=p6 sig_type=std_logic lab=VOUT1}
C {gnd.sym} 360 -130 0 0 {name=l2 lab=0}
C {code_shown.sym} 20 -470 0 0 {name=MODELS only_toplevel=false value="
.param sw_stat_global   = 0
.param sw_stat_mismatch = 0
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
"}
C {code_shown.sym} -900 -1290 0 0 {name=NGSPICE only_toplevel=false value="
* ===== stimulus =====
Vvdd  VDD  0 3.3
Vvin1 VIN1 0 PWL(0 1.62 1e-6 1.68)
Vvin2 VIN2 0 1.65
Vck   CK   0 PULSE(0 3.3 2n   100p 100p 8n 20n)
Vckl  CKL  0 PULSE(0 3.3 3.3n 100p 100p 8n 20n)

.control
let mc_runs = 100
let svt_pre = 0.78e-3
let svt_sa = 2.19e-3
let run = 0
let offset_results = vector(mc_runs)
let ngood = 0
let sumx = 0
let sumx2 = 0
set homeplot = $curplot
dowhile run < mc_runs
  echo ---- run $&run ----
  unset s_up
  unset s_dn
  alter @m.x1.x1.xm1p.m0[delvto] = svt_pre * sgauss(0)
  alter @m.x1.x1.xm2p.m0[delvto] = svt_pre * sgauss(0)
  alter @m.x1.x2.xm10.m0[delvto] = svt_sa  * sgauss(0)
  alter @m.x1.x2.xm8.m0[delvto]  = svt_sa  * sgauss(0)
  alter @vvin1[pwl] = [ 0 1.62 1e-6 1.68 ]
  tran 10p 1u
  let t_up = -1
  meas tran t_up when v(vout1)=1.5 fall=LAST
  if t_up > 0
    meas tran vin_up find v(vin1) at=t_up
    set s_up = $&vin_up
  end
  destroy $curplot
  alter @vvin1[pwl] = [ 0 1.68 1e-6 1.62 ]
  tran 10p 1u
  let t_dn = -1
  meas tran t_dn when v(vout1)=1.5 fall=1
  if t_dn > 0
    meas tran vin_dn find v(vin1) at=t_dn
    set s_dn = $&vin_dn
  end
  destroy $curplot
  setplot $homeplot
  if $?s_up * $?s_dn
    let cur = (($s_up - 1.65) + ($s_dn - 1.65)) / 2
    let offset_results[run] = cur
    let ngood = ngood + 1
    let sumx = sumx + cur
    let sumx2 = sumx2 + cur*cur
    echo   up=$s_up dn=$s_dn offset=$&cur
  else
    let offset_results[run] = -999
    echo   WARN: miss on run $&run
  end
  let run = run + 1
end
setplot $homeplot
let mu = sumx/ngood
let sig = sqrt(sumx2/ngood - mu*mu)
echo ==================================================
echo Two-stage offset MC:  N=$&mc_runs good=$&ngood
echo   mean = $&mu V   sigma = $&sig V
echo ==================================================

* --- save raw results to disk for later plotting ---
wrdata /foss/designs/comparator/comp2_mc_offsets.txt offset_results
echo MC N=$&mc_runs good=$&ngood mean=$&mu sigma=$&sig > /foss/designs/comparator/comp2_mc_report.txt
print offset_results >> /foss/designs/comparator/comp2_mc_report.txt
.endc
"}
C {lab_pin.sym} 60 -190 0 0 {name=p7 sig_type=std_logic lab=CKL}
C {comparator_alt/schematic/comparator_2stage.sym} 210 -160 0 0 {name=x2}
