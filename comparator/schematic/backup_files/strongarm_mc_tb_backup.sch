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
C {vsource.sym} 840 -730 0 0 {name=VVIN2 value=3 savecurrent=false}
C {vsource.sym} 770 -730 0 0 {name=VVIN1 value=3 savecurrent=false}
C {vsource.sym} 630 -730 0 0 {name=VDD value=3 savecurrent=false}
C {vsource.sym} 700 -730 0 0 {name=VCK value=3 savecurrent=false}
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
C {devices/code_shown.sym} 10 -1010 0 0 {name=NGSPICE only_toplevel=true
value="
.control
let mc_runs = 200
let run = 1

* create a vector to store 200 offset measurements
let  offset_results = vector(mc_runs)

* set clock permanently high (3.3v) for dc sweep
alter @VCK[DC] =  3.3
alter @VCK[PULSE] = [ 3.3 3.3 0  1n 1n 10n 20n 0 ]
alter @VVIN2[DC] = 1.200

* start monte carlo loop
while run <= mc_runs
* reset forces NGSPICE to re-roll the transistor stats
reset

* run a 10 microsecond transient simulation (500 clock cycles)
tran 100p 10u

print 'This is the current run:'
print run

* sweep vin1 from 1.15v to 1.25v in tiny 0.1mV steps
dc VVIN1 1.15 1.25 0.1m

* measure the voltage of VIN1 exactly when OUT1 crosses OUT2
meas dc trip_point find v(vin1) when v(out1)=v(out2)

* offset is the difference between the trip point and VIN2 (1.2V)
let current_offset = trip_point - 1.2

* save this run's offset into our array
let offset_results[run-1] = current_offset

* increment the loop counter
let run = run + 1
end

* write teh final array of 200 offsets to a text file for Python parsing
write comp_mc_offsets.raw offset_results

print offset_results
.endc"}
C {lab_wire.sym} 700 -850 0 0 {name=p1 sig_type=std_logic lab=CK}
C {lab_wire.sym} 770 -810 0 0 {name=p3 sig_type=std_logic lab=VIN1}
C {lab_wire.sym} 840 -770 0 0 {name=p4 sig_type=std_logic lab=VIN2}
