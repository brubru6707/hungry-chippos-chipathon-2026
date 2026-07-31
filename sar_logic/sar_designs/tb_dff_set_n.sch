v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -200 40 -200 70 {lab=RST_N}
N -200 40 -30 40 {lab=RST_N}
N -270 -20 -270 70 {lab=CLK}
N -270 -20 -30 -20 {lab=CLK}
N -350 -90 -350 70 {lab=D}
N -350 -90 -30 -90 {lab=D}
N -420 -220 -420 70 {lab=VDD}
N -420 -220 50 -220 {lab=VDD}
N 50 -220 50 -140 {lab=VDD}
N 50 100 50 160 {lab=0}
N -420 150 50 150 {lab=0}
N -420 130 -420 150 {lab=0}
N -350 130 -350 150 {lab=0}
N -270 130 -270 150 {lab=0}
N -200 130 -200 150 {lab=0}
N 130 -20 260 -20 {lab=Q}
N 260 -20 260 40 {lab=Q}
N 260 100 260 150 {lab=0}
N 50 150 260 150 {lab=0}
C {vsource.sym} -200 100 0 0 {name=VRST value="PULSE(3.3 0 100n 1n 1n 100n 1000n)" savecurrent=false}
C {vsource.sym} -270 100 0 0 {name=VCLK value="PULSE(0 3.3 0 1n 1n 50n 100n)" savecurrent=false}
C {vsource.sym} -350 100 0 0 {name=VDATA value="PULSE(0 3.3 10n 1n 1n 120n 240n)" savecurrent=false}
C {vsource.sym} -420 100 0 0 {name=VVDD value=3.3 savecurrent=false}
C {gnd.sym} 50 160 0 0 {name=l1 lab=0}
C {capa.sym} 260 70 0 0 {name=CLOAD
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {code_shown.sym} 220 -200 0 0 {name=MODELS only_toplevel=true  
format="tcleval( @value )" 
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical
.lib $::180MCU_MODELS/smbb000149.ngspice typical
"}
C {code_shown.sym} 340 -10 0 0 {name=COMMANDS only_toplevel=false value="
.control
  tran 1n 500n
  run
  plot V(CLK) V(RST_N) V(Q)
.endc
"}
C {lab_pin.sym} -220 -220 0 0 {name=p1 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -200 -90 0 0 {name=p2 sig_type=std_logic lab=D}
C {lab_pin.sym} -160 -20 0 0 {name=p3 sig_type=std_logic lab=CLK}
C {lab_pin.sym} -130 40 0 0 {name=p4 sig_type=std_logic lab=RST_N}
C {lab_pin.sym} 230 -20 0 0 {name=p5 sig_type=std_logic lab=Q}
C {dff_set_n.sym} 50 -20 0 0 {name=x1}
