v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 415 15 415 75 {lab=#net1}
N -200 -20 -200 40 {lab=#net2}
N -200 -130 -200 -20 {lab=#net2}
N -200 -130 -140 -130 {lab=#net2}
N -140 -110 -140 -0 {lab=#net3}
N -30 -130 105 -130 {lab=#net1}
N -290 -210 -135 -210 {lab=#net4}
N -290 -210 -290 35 {lab=#net4}
N -290 35 -290 45 {lab=#net4}
N -35 -210 105 -210 {lab=#net1}
N 105 -210 105 -130 {lab=#net1}
N -245 -40 -140 -40 {lab=#net3}
N -245 -190 -245 -40 {lab=#net3}
N -245 -190 -135 -190 {lab=#net3}
N -175 -260 -175 -210 {lab=#net4}
N -175 -260 -10 -260 {lab=#net4}
N -10 -260 -10 -190 {lab=#net4}
N -30 -190 -10 -190 {lab=#net4}
N -35 -190 -30 -190 {lab=#net4}
N -140 -0 -140 150 {lab=#net3}
N -140 150 -125 150 {lab=#net3}
N -140 125 -65 125 {lab=#net3}
N -35 5 -35 55 {lab=#net4}
N -290 5 -35 5 {lab=#net4}
N 65 125 125 125 {lab=#net5}
N 125 85 125 125 {lab=#net5}
N -235 20 -200 20 {lab=#net2}
N -235 20 -235 230 {lab=#net2}
N -235 230 50 230 {lab=#net2}
N 50 230 50 235 {lab=#net2}
N 50 235 50 240 {lab=#net2}
N 105 -60 160 -60 {lab=#net6}
N 160 -60 160 240 {lab=#net6}
N -185 265 50 265 {lab=#net3}
N -185 135 -185 265 {lab=#net3}
N -185 135 -140 135 {lab=#net3}
N 50 260 50 265 {lab=#net3}
N 105 -160 175 -160 {lab=#net1}
N 175 -160 175 -155 {lab=#net1}
N -150 -295 -150 -190 {lab=#net3}
N -150 -295 285 -295 {lab=#net3}
N 285 -295 285 -155 {lab=#net3}
N -140 -15 40 -15 {lab=#net3}
N 40 -145 40 -15 {lab=#net3}
N 40 -145 175 -145 {lab=#net3}
N 175 -145 175 -135 {lab=#net3}
N 95 125 95 155 {lab=#net5}
N 95 155 370 155 {lab=#net5}
N 370 -155 370 155 {lab=#net5}
N 370 -155 380 -155 {lab=#net5}
N 380 -160 380 -155 {lab=#net5}
N 285 -265 490 -265 {lab=#net3}
N 490 -265 490 -180 {lab=#net3}
N 105 -190 315 -190 {lab=#net1}
N 315 -190 315 15 {lab=#net1}
N 315 15 415 15 {lab=#net1}
N 410 90 415 75 {lab=#net1}
N 410 150 415 165 {lab=0}
N 100 -70 105 -60 {lab=#net6}
N 105 -25 110 -60 {lab=#net6}
C {vsource.sym} -125 180 0 0 {name=VCLK value="pulse(0 3.3 0 1n 1n 0.5u 1u)" savecurrent=false}
C {vsource.sym} -200 70 0 0 {name=VIN value="sin(1.65 1.65 10k)" savecurrent=false}
C {gnd.sym} -125 210 0 0 {name=l1 lab=0}
C {code.sym} 545 -240 0 0 {name=s1 only_toplevel=false value="
.param mim_corner_1p0fF=1 mim_corner_1p5fF=1 mim_corner_2p0fF=1
.param mc_c_cox_1p0fF=0 mc_c_cox_1p5fF=0 mc_c_cox_2p0fF=0
.param var_vth=0 var_k=0
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice cap_mim
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
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
C {gnd.sym} -200 100 0 0 {name=l2 lab=0}
C {gnd.sym} 415 165 0 0 {name=l3 lab=0}
C {designs/emily_testing/pfet3.3.sym} 15 -200 0 0 {name=x2}
C {designs/emily_testing/nfet3.3.sym} 10 -120 0 0 {name=x3
}
C {gnd.sym} -30 -110 3 0 {name=l5 lab=0}
C {designs/emily_testing/nfet3.3.sym} 115 -65 3 0 {name=x4}
C {designs/emily_testing/nfet3.3.sym} 325 -145 0 0 {name=x5}
C {designs/emily_testing/nfet3.3.sym} 200 250 0 0 {name=x6}
C {designs/emily_testing/nfet3.3.sym} 530 -170 0 0 {name=x7}
C {vsource.sym} -290 75 0 0 {name=VDD value="dc 3.3" savecurrent=false}
C {gnd.sym} -290 105 0 0 {name=l4 lab=0}
C {gnd.sym} 105 85 0 0 {name=l6 lab=0}
C {designs/emily_testing/inv1.sym} 35 125 0 0 {name=x1}
C {gnd.sym} -35 185 0 0 {name=l7 lab=0}
C {gnd.sym} 125 -25 2 0 {name=l8 lab=0}
C {gnd.sym} 160 260 0 0 {name=l9 lab=0}
C {gnd.sym} 285 -135 3 0 {name=l10 lab=0}
C {gnd.sym} 490 -160 3 0 {name=l11 lab=0}
C {gnd.sym} 380 -180 1 0 {name=l12 lab=0}
C {symbols/cap_mim_2f0fF.sym} 410 120 0 0 {name=C2
W=1e-6
L=1e-6
model=cap_mim_2f0fF
spiceprefix=X
m=1}
C {symbols/cap_mim_2f0fF.sym} 100 -100 0 0 {name=C3
W=1e-6
L=1e-6
model=cap_mim_2f0fF
spiceprefix=X
m=1}
