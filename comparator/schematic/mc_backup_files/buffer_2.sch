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
C {vsource.sym} 770 -730 0 0 {name=VVIN1 value="PWL(0 1.1 2u 1.3)" savecurrent=false}
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
.options seed=random
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
"}
C {devices/code_shown.sym} -140 -1290 0 0 {name=NGSPICE only_toplevel=true
value="
.control
set seed=random
let mc_runs = 50
let run = 1

* Create a vector in the 'global' control plot to store offset measurements
set curplatenv = $curplot
let offset_results = vector(mc_runs)

* Define timing parameters
let fclk = 50e6
let tper = 1/fclk

* Start monte carlo loop
while run <= mc_runs
	echo ----------------------------------------
	echo Run $&run of $&mc_runs
    setseed $&run
    set seed = $&run
	reset

	* Run a 2us transient to sweep across 100 clock cycles (for ~2mV resolution)
	tran 10p 2u

	set current_tran = $curplot

	* Pre-init as -1; meas overwrites on success. Use trip_time>0 not $?trip_time.
	let trip_time = -1
	meas tran trip_time when v(out1)=1.5 fall=LAST
	echo   trip_time = $&trip_time

	if trip_time > 0
		meas tran v_in_at_trip find v(vin1) at=trip_time
		let current_offset = v_in_at_trip - 1.200
		echo   v_in_at_trip = $&v_in_at_trip  offset = $&current_offset

		setplot $curplatenv
		let idx = run - 1
		let offset_results[idx] = \{$current_tran\}.current_offset
		echo   stored at idx $&idx

	else
		echo Warning: out1 never recovered on run $&run

		setplot $curplatenv
		let idx = run - 1
		let offset_results[idx] = -999
		echo   stored sentinel -999 at idx $&idx
	end

	let run = run + 1
end

* Switch back to environment plot to write out accumulated array
setplot $curplatenv
write comp_mc_offsets.raw offset_results

print offset_results
.endc
"}
C {lab_wire.sym} 700 -850 0 0 {name=p1 sig_type=std_logic lab=CK}
C {lab_wire.sym} 770 -800 0 0 {name=p3 sig_type=std_logic lab=VIN1}
C {lab_wire.sym} 840 -770 0 0 {name=p4 sig_type=std_logic lab=VIN2}
