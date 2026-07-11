v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 1520 -470 1650 -470 {lab=OUT2}
N 1520 -450 1610 -450 {lab=OUT1}
C {title.sym} 180 -60 0 0 {name=l1 author="Luc Bastien"}
C {devices/code_shown.sym} 1090 -710 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.param sw_stat_global   = 0
.param sw_stat_mismatch = 0
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {devices/code_shown.sym} -50 -1550 0 0 {name=NGSPICE only_toplevel=true value="

* ===== stimulus (converted from source symbols to code-block sources) =====
Vvdd  VDD  0 3.3
Vvin1 VIN1 0 PWL(0 1.2 6e-6 1.2)        ; MUST be named Vvin1 and be PWL -> alter @vvin1[pwl] targets it
Vvin2 VIN2 0 1.2
Vck   CK   0 PULSE(0 3.3 2n 100p 100p 8n 20n)
Vckl  CKL  0 PULSE(0 3.3 2n 100p 100p 8n 20n)

.control
* ============================================================
* Two-stage comparator (preamp + StrongARM) — offset Monte Carlo
* ============================================================
let mc_runs = 100
let svt_pre = 0.78e-3    ; preamp input pair (64 um^2)
let svt_sa  = 3.58e-3    ; StrongARM input pair (3 um^2)
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
  * fresh mismatch draw each run, on BOTH input pairs
  alter @m.x1.x1.xm1p.m0[delvto] = svt_pre * sgauss(0)
  alter @m.x1.x1.xm2p.m0[delvto] = svt_pre * sgauss(0)
  alter @m.x1.x2.xm10.m0[delvto] = svt_sa  * sgauss(0)
  alter @m.x1.x2.xm8.m0[delvto]  = svt_sa  * sgauss(0)
  * -------- UP sweep: VIN1 1.15 -> 1.25 --------
  alter @vvin1[pwl] = [ 0 1.15 6e-6 1.25 ]
  tran 10p 6u
  let t_up = -1
  meas tran t_up when v(out2)=1.5 fall=LAST
  if t_up > 0
    meas tran vin_up find v(vin1) at=t_up
    set s_up = $&vin_up
  end
  destroy $curplot
  * -------- DOWN sweep: VIN1 1.25 -> 1.15 --------
  alter @vvin1[pwl] = [ 0 1.25 6e-6 1.15 ]
  tran 10p 6u
  let t_dn = -1
  meas tran t_dn when v(out2)=1.5 fall=1
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
setplot $homeplot
let mu  = sumx / ngood
let sig = sqrt( sumx2/ngood - mu*mu )
echo ======================================================
echo MC done: N=$&mc_runs  good=$&ngood
echo   mean offset = $&mu V
echo   sigma       = $&sig V
echo ======================================================
unset wr_singlescale
write  /foss/designs/comparator/comp2_mc_offsets.raw offset_results
wrdata /foss/designs/comparator/comp2_mc_offsets.txt offset_results
echo MC N=$&mc_runs good=$&ngood mean=$&mu sigma=$&sig > /foss/designs/comparator/comp2_mc_report.txt
print offset_results >> /foss/designs/comparator/comp2_mc_report.txt
.endc
"}
C {vdd.sym} 1520 -490 1 0 {name=l2 lab=VDD}
C {gnd.sym} 1520 -430 3 0 {name=l3 lab=0}
C {noconn.sym} 1610 -450 0 1 {name=l4}
C {noconn.sym} 1840 -640 0 1 {name=l5}
C {lab_wire.sym} 1630 -470 0 0 {name=p1 sig_type=std_logic lab=OUT2}
C {lab_wire.sym} 1560 -450 2 0 {name=p3 sig_type=std_logic lab=OUT1}
C {comparator_2stage.sym} 1370 -460 0 0 {name=x2}
C {lab_pin.sym} 1220 -490 0 0 {name=p4 sig_type=std_logic lab=CKL}
C {lab_pin.sym} 1220 -470 0 0 {name=p6 sig_type=std_logic lab=VIN2}
C {lab_pin.sym} 1220 -450 0 0 {name=p7 sig_type=std_logic lab=VIN1}
C {lab_pin.sym} 1220 -430 0 0 {name=p8 sig_type=std_logic lab=CK}
