v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {kT/C sampling-noise cross-check (Brief #6/DAC-6, Step 3).
SAMPLE held DC-high (steady acquire state, all 8 M1 in triode tying bottom
plates to VIN, M2/M3 off per the SAMPLE-gated cell) so the operating point
matches the actual sampling instant. V_VIN carries ac=1 so ngspice's .noise
analysis can report the small-signal transfer function; the switch channel
thermal noise (4kT*gamma/gm-style device noise, already modeled by the PDK
BSIM cards) integrates through that transfer function onto DAC_TOP.
ngspice prints onoise_total (V_rms, integrated 1Hz-100GHz) automatically at
the end of a decade .noise sweep -- this is the SPICE-level cross-check
against the analytical sqrt(kT/C) figure (kT/C with C=255*Cu=12.75pF predicts
~18 uV rms, see dac/WORKLOG.md).} 0 -260 0 0 0.25 0.25 {}
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
C {vsource.sym} -400 -50 0 0 {name=V_VIN value="dc 1.65 ac 1" savecurrent=false}
C {vsource.sym} -300 -50 0 0 {name=V_VREF value=1.65 savecurrent=false}
C {vsource.sym} -200 -50 0 0 {name=V_VDD value=3.3 savecurrent=false}
C {vsource.sym} -100 -50 0 0 {name=V_SAMPLE value=3.3 savecurrent=false}
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
C {code.sym} 0 -450 0 0 {name=s1 only_toplevel=false value="
.param nfet_wid=0.42u nfet_len=0.28u
.param mim_corner_1p0fF=1 mim_corner_1p5fF=1 mim_corner_2p0fF=1
.param mc_c_cox_1p0fF=0 mc_c_cox_1p5fF=0 mc_c_cox_2p0fF=0
.param var_vth=0 var_k=0
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice cap_mim
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.options savecurrents
.control
save all
noise v(DAC_TOP) V_VIN dec 20 1 100g
print onoise_total
print inoise_total
.endc
"}
