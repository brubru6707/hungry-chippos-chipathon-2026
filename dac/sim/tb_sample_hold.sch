v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Sample-and-hold characterization testbench (Brief #6/DAC-6).
No top-plate switch exists anywhere in this design (Step 0 finding) --
DAC_TOP is a purely passive node tied only to the 8 cap top plates + the
20fF comparator-input placeholder. Sampling is 100% bottom-plate: SAMPLE=1
ties every bit's bottom plate straight to VIN (in-cell gated, contention-free
per commit 02a5400). Timeline: 0-20n SAMPLE=0/code=0 (clean pre-sample state,
bottom plates + DAC_TOP settle to 0V). 20n SAMPLE->1 (acquire): bottom plates
step to VIN_TARGET; DAC_TOP asymptotically approaches VIN*Ctot/(Ctot+Cload)
(NOT exactly VIN, since Cload divides the floating top node -- flagged as a
secondary gain-error consequence of the missing top-plate reset). 170n
SAMPLE->0 (hold), code stays 0 (bottom plates -> GND) for the rest of the run.
v_hold_ref sampled at 220n (170n + 50n, safely past the Gate-2 settling
transient of the SAMPLE-low step) and v_hold_end at 540n (220n + 320n, a
conservative 8-bit x 40ns Gate-2-ceiling conversion window) isolate leakage
-only droop from the deterministic step.
VIN_TARGET/VDD_VAL are .param so a driver script can text-substitute VIN
level and PVT corner without re-netlisting from Xschem.} 0 -340 0 0 0.25 0.25 {}
N -400 -100 -400 -80 {lab=VIN}
N -400 -20 -400 0 {lab=0}
N -300 -100 -300 -80 {lab=VREF}
N -300 -20 -300 0 {lab=0}
N -200 -100 -200 -80 {lab=VDD}
N -200 -20 -200 0 {lab=0}
N -100 -100 -100 -80 {lab=SAMPLE}
N -100 -20 -100 0 {lab=0}
N -85 70 -110 70 {lab=VIN}
N -85 90 -110 90 {lab=VREF}
N -85 110 -110 110 {lab=VDD}
N -85 130 -110 130 {lab=SAMPLE}
N -85 150 -110 150 {lab=B0}
N -85 170 -110 170 {lab=B1}
N -85 190 -110 190 {lab=B2}
N -85 210 -110 210 {lab=B3}
N -85 230 -110 230 {lab=B4}
N -85 250 -110 250 {lab=B5}
N -85 270 -110 270 {lab=B6}
N -85 290 -110 290 {lab=B7}
N 85 200 200 200 {lab=DAC_TOP}
N 200 200 200 230 {lab=DAC_TOP}
N 200 290 200 310 {lab=0}
C {vsource.sym} -400 -50 0 0 {name=V_VIN value="'VIN_TARGET'" savecurrent=false}
C {vsource.sym} -300 -50 0 0 {name=V_VREF value=1.65 savecurrent=false}
C {vsource.sym} -200 -50 0 0 {name=V_VDD value="'VDD_VAL'" savecurrent=false}
C {vsource.sym} -100 -50 0 0 {name=V_SAMPLE value="pulse(0 3.3 20n 1n 1n 150n 1000n)" savecurrent=false}
C {gnd.sym} -400 0 0 0 {name=l1 lab=0}
C {gnd.sym} -300 0 0 0 {name=l2 lab=0}
C {gnd.sym} -200 0 0 0 {name=l3 lab=0}
C {gnd.sym} -100 0 0 0 {name=l4 lab=0}
C {lab_wire.sym} -400 -80 0 0 {name=p1 sig_type=std_logic lab=VIN}
C {lab_wire.sym} -300 -80 0 0 {name=p2 sig_type=std_logic lab=VREF}
C {lab_wire.sym} -200 -80 0 0 {name=p3 sig_type=std_logic lab=VDD}
C {lab_wire.sym} -100 -80 0 0 {name=p4 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} -110 70 0 0 {name=p13 sig_type=std_logic lab=VIN}
C {lab_wire.sym} -110 90 0 0 {name=p14 sig_type=std_logic lab=VREF}
C {lab_wire.sym} -110 110 0 0 {name=p15 sig_type=std_logic lab=VDD}
C {lab_wire.sym} -110 130 0 0 {name=p16 sig_type=std_logic lab=SAMPLE}
C {lab_wire.sym} -110 150 0 0 {name=p17 sig_type=std_logic lab=0}
C {lab_wire.sym} -110 170 0 0 {name=p18 sig_type=std_logic lab=0}
C {lab_wire.sym} -110 190 0 0 {name=p19 sig_type=std_logic lab=0}
C {lab_wire.sym} -110 210 0 0 {name=p20 sig_type=std_logic lab=0}
C {lab_wire.sym} -110 230 0 0 {name=p21 sig_type=std_logic lab=0}
C {lab_wire.sym} -110 250 0 0 {name=p22 sig_type=std_logic lab=0}
C {lab_wire.sym} -110 270 0 0 {name=p23 sig_type=std_logic lab=0}
C {lab_wire.sym} -110 290 0 0 {name=p24 sig_type=std_logic lab=0}
C {lab_wire.sym} 150 200 0 0 {name=p25 sig_type=std_logic lab=DAC_TOP}
C {capa.sym} 200 260 0 0 {name=Cload m=1 value=20f}
C {gnd.sym} 200 310 0 0 {name=l13 lab=0}
C {dac/schematic/cap_array.sym} 0 200 0 0 {name=x1}
C {code.sym} 0 -560 0 0 {name=s1 only_toplevel=false value="
.param nfet_wid=0.42u nfet_len=0.28u
.param mim_corner_1p0fF=1 mim_corner_1p5fF=1 mim_corner_2p0fF=1
.param mc_c_cox_1p0fF=0 mc_c_cox_1p5fF=0 mc_c_cox_2p0fF=0
.param var_vth=0 var_k=0
.param VIN_TARGET=0.3
.param VDD_VAL=3.3
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice cap_mim
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.options savecurrents
.control
save all
* Brief #10 top-plate-sampling fix: with the TG now providing a resistive
* DVDD-free leakage path from DAC_TOP to VIN even while nominally OFF, the
* no-'uic' DC operating-point solve (true t=inf steady state, where any
* finite leakage resistance still forces zero current / V(DAC_TOP)=VIN
* exactly) pre-charges DAC_TOP to VIN_TARGET *before* SAMPLE ever goes
* high, making the acquisition transient measured below meaningless (it
* would just be measuring re-entry into a band the solver already started
* inside). uic + ic v(DAC_TOP)=0 forces a physically meaningful cold start
* so the SAMPLE-high transient actually exercises the TG's charging path.
.ic v(DAC_TOP)=0
tran 0.02n 600n uic
* Acquisition (SAMPLE high 20n-170n): settle vs the value DAC_TOP actually
* reaches at end of acquire window (own-final method, same convention as
* Gate-2). gap_to_vin_target_mV reports the residual Cload-loading gain
* error separately (no top-plate reset -> DAC_TOP asymptote is
* VIN*Ctot/(Ctot+Cload), not exactly VIN).
meas tran v_acq_final FIND v(DAC_TOP) AT=170n
let acq_err = v(DAC_TOP) - v_acq_final
meas tran t_acq_hi_last WHEN acq_err=6.45m CROSS=LAST TD=20n
meas tran t_acq_lo_last WHEN acq_err=-6.45m CROSS=LAST TD=20n
echo acquire_settle_after_sample_high_hi_lo_ns:
print (t_acq_hi_last-20e-9)/1e-9 (t_acq_lo_last-20e-9)/1e-9
echo v_acq_final_V:
print v_acq_final
echo gap_to_vin_target_mV:
print (v_acq_final-VIN_TARGET)/1e-3
* Hold droop (SAMPLE low at 170n, code=0 constant -> bottom plates to GND).
* v_hold_ref sampled after Gate-2's own settling transient has died out;
* v_hold_end 320ns later (8 bits x 40ns Gate-2 ceiling, conservative
* conversion-window proxy in the absence of a committed conversion-rate spec).
meas tran v_hold_ref FIND v(DAC_TOP) AT=220n
meas tran v_hold_end FIND v(DAC_TOP) AT=540n
echo hold_droop_mV:
print (v_hold_end-v_hold_ref)/1e-3
.endc
"}
