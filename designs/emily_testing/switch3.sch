v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
C {vsource.sym} -55 60 0 0 {name=VCLK value="pulse(0 3.3 0 1n 1n 0.5u 1u)" savecurrent=false}
C {vsource.sym} -130 -50 0 0 {name=VIN value="sin(1.65 1.65 10k)" savecurrent=false}
C {code.sym} 65 -200 0 0 {name=s1 only_toplevel=false value="
.param c_area=0
.param mc_c_cox_1p0fF=0 mc_c_cox_1p5fF=0 mc_c_cox_2p0fF=0
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064_mim.ngspice cap_mim_new
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.param var_vth=0 var_k=0
.options savecurrents
.control
  save all
  tran 2n 3u
  let vin = v(net2)
  let clk = v(net3)
  let vout = v(net1)
  plot clk vin vout
.endc

"}
C {vsource.sym} -220 -45 0 0 {name=VDD value="dc 3.3" savecurrent=false}
