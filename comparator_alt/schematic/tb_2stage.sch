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
Vvin1 VIN1 0 PWL(0 1.64 1e-6 1.66)
Vvin2 VIN2 0 1.65
Vck   CK   0 PULSE(0 3.3 2n   100p 100p 8n 20n)
Vckl  CKL  0 PULSE(0 3.3 3.1n 100p 100p 5n 20n)

.control
let mc_runs = 200
let svt_pre = 1.44e-3
let svt_sa = 2.19e-3
let run = 0
set rndseed = 12345
let offset_results = vector(mc_runs)
let ngood = 0
let sumx = 0
let sumx2 = 0
set homeplot = $curplot
dowhile run < mc_runs
  echo ---- run $&run/$&mc_runs ----
  unset s_up
  unset s_dn
  alter @m.x1.x1.xm1p.m0[delvto] = svt_pre * sgauss(0)
  alter @m.x1.x1.xm2p.m0[delvto] = svt_pre * sgauss(0)
  alter @m.x1.x2.xm10.m0[delvto] = svt_sa  * sgauss(0)
  alter @m.x1.x2.xm8.m0[delvto]  = svt_sa  * sgauss(0)
  alter @vvin1[pwl] = [ 0 1.64 1e-6 1.66 ]
  tran 1n 1u
  let t_up = -1
  meas tran t_up when v(vout1)=1.5 fall=LAST
  if t_up > 0
    meas tran vin_up find v(vin1) at=t_up
    set s_up = $&vin_up
  end
  destroy $curplot
  alter @vvin1[pwl] = [ 0 1.66 1e-6 1.64 ]
  tran 1n 1u
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
let mu_mv = mu*1e3
let sig_mv = sig*1e3
echo ==================================================
echo Two-stage offset MC:  N=$&mc_runs good=$&ngood
echo   mean = $&mu_mv mV   sigma = $&sig_mv mV
echo ==================================================

* --- save raw results to disk for later plotting ---
wrdata /foss/designs/comparator_alt/results/comp2_mc_offsets.txt offset_results
echo MC ckl=2.8n seed=12345 N=$&mc_runs good=$&ngood mean_mv=$&mu_mv sigma_mv=$&sig_mv > /foss/designs/comparator_alt/results/comp2_mc_report.txt
print offset_results >> /foss/designs/comparator_alt/results/comp2_mc_report.txt
.endc
"}
C {lab_pin.sym} 60 -190 0 0 {name=p7 sig_type=std_logic lab=CKL}
C {comparator_alt/schematic/comparator_2stage.sym} 210 -160 0 0 {name=x1}
C {code_shown.sym} -1620 -1290 0 0 {name=COMMENTS only_toplevel=false value="
* SPICE component: <name> <node+> <node-> <value>
* V means voltage source, M is MOSFET, X is a subcircuit
* Node 0 is global ground
* PWL is a linear sweep from t=0, V=1.64, to t=1u, V=1.66, +/- 10 mV
* PULSE(v_low v_high initial_delay t_rise t_fall up_time period)
*
*
* Above .control is static netlist, below is simulation scripting
* let creates a vector (including length 1), set creates a shell var
* svt = sigma (standard deviation) of V threshold
* _pre = preamp input pair transistors, XM1P/XM2P
* _sa = strongarm input pair, XM8/XM10
* Random seed so that our results are reproducible exactly
* Create a vector with the number of slots equal to the number of runs
* Keep track of the sum of offsets and the sum of squares of offsets
* It lets us calculate variance later
*
* A new .tran opens a new plot, so keep track of the current plot
* Loop the following for each run of the Monte Carlo
* Print run number to terminal
* Clear s_up and s_dn so a failed run doesn't use last run's value
*
* alter changes an already-loaded variable. @=device instance parameter,
* m=MOSFET, x1.x1=preamp_dyn, m1p=transistor, m0=MOSFET inside nfet_03v3,
* [delvto]=parameter (delta v threshold), s_gauss(0)=random distribution
* centered on 0 with std. dev. 1, multiply by sigma to scale it right
* Start the up sweep of vin1 (Vvin1 denotes voltage of vin1)
* Transient simulation with 10ps steps ending at 1us
* Define t_up with a nonsense value so we know if it didn't change
* measure, let t_up=time when comparator flips (hits 1.5V)
* fall=LAST excludes the precharge to VDD; we want the most recent flip
* if there wasn't a flip, t_up would stay at -1 ^
* measure, let vin_up be the voltage at t_up that caused the flip ^
* save it in a shell variable so it doesn't get erased with the plot
* destroy the plot so we only have to remember our s_up voltage
* Do it again sweeping down to eliminate systematic bias
* 
* 
* 
* 
* 
* 
* 
*
* Get back to the home plot where our variables are
* $?s_up asks if it exists (0 or 1), so this checks if both exist
* Calculate offset with average of up and down sweep offsets
* Add it to the vector of all the offsets
* Increase number of good runs, since we made it to this point
* Add to the sum of offsets and the sum of their squares
* 
* Print the outputs for every run
*
* If we missed, set the value to -999 so it's clearly wrong
* Also give a warning of a miss in the terminal
* 
* Increase run number
*
* Back to homeplot (a little bit of redundancy)
* mu is the mean
* sig calculates variance, mean of squares minus square of the mean
* and then take the square root of that number
* Convert to mV for readability
* 
* echo to print results to terminal
*
*
*
*
* wrdata writes to a plain text file for plotting elsewhere
* Single bracket (>) creates a file, double (>>) appends
"}
C {code_shown.sym} 100 -1170 0 0 {name=s1 only_toplevel=false value="* per-DEVICE sigma(Vth) = A_VT / sqrt(W*L), A_VT = 6.2 mV*um (NMOS, per-device convention)
* pair mismatch is sqrt(2)x larger, but MC produces that automatically
* preamp XM1P/XM2P: 4u x 16 x 1u  = 64 um^2 -> 0.78 mV
* latch  XM8/XM10:  8u x 1u       =  8 um^2 -> 2.19 mV"}
