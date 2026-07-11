v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -700 -0 -620 0 {lab=D}
N -500 -0 -390 0 {lab=#net1}
N -450 40 -390 40 {lab=RST_N}
N 110 20 200 20 {lab=#net2}
N 150 60 200 60 {lab=RST_N}
N -290 20 -10 20 {lab=#net3}
N 300 40 510 40 {lab=#net4}
N 640 40 670 40 {lab=Q}
N -70 -200 -70 20 {lab=#net3}
N -90 -200 -70 -200 {lab=#net3}
N -280 -200 -220 -200 {lab=#net5}
N -450 -200 -400 -200 {lab=#net1}
N -450 -200 -450 -0 {lab=#net1}
N 500 -200 500 40 {lab=#net4}
N 480 -200 500 -200 {lab=#net4}
N 300 -200 350 -200 {lab=#net6}
N 140 -200 180 -200 {lab=#net2}
N 140 -200 140 20 {lab=#net2}
N 150 60 150 240 {lab=RST_N}
N -450 240 150 240 {lab=RST_N}
N -450 40 -450 240 {lab=RST_N}
N -100 -580 -10 -580 {lab=CLK}
N -100 -420 -100 -390 {lab=#net7}
N -500 50 -500 110 {lab=#net7}
N -660 110 -500 110 {lab=#net7}
N -660 -390 -660 110 {lab=#net7}
N -660 -390 -100 -390 {lab=#net7}
N -10 -390 -10 -40 {lab=#net7}
N -100 -390 -10 -390 {lab=#net7}
N 180 -150 180 -100 {lab=#net7}
N 130 -100 180 -100 {lab=#net7}
N 130 -390 130 -100 {lab=#net7}
N -10 -390 130 -390 {lab=#net7}
N -10 -580 90 -580 {lab=CLK}
N 90 -580 90 -330 {lab=CLK}
N -620 -330 -620 -60 {lab=CLK}
N -620 -330 90 -330 {lab=CLK}
N -400 -150 -400 -110 {lab=CLK}
N -470 -110 -400 -110 {lab=CLK}
N -470 -330 -470 -110 {lab=CLK}
N 110 70 110 100 {lab=CLK}
N 110 100 120 100 {lab=CLK}
N 120 -330 120 100 {lab=CLK}
N 90 -330 120 -330 {lab=CLK}
N 300 -330 300 -260 {lab=CLK}
N 120 -330 300 -330 {lab=CLK}
N -560 -670 -560 -30 {lab=VDD}
N -560 -670 -60 -670 {lab=VDD}
N -340 -670 -340 -230 {lab=VDD}
N 50 -670 50 -10 {lab=VDD}
N -60 -670 50 -670 {lab=VDD}
N -60 -690 -60 -670 {lab=VDD}
N 240 -670 240 -230 {lab=VDD}
N 50 -670 240 -670 {lab=VDD}
N 540 -670 540 -30 {lab=VDD}
N 240 -670 540 -670 {lab=VDD}
N 450 -670 450 -270 {lab=VDD}
N 230 -80 230 -0 {lab=VDD}
N 230 -80 540 -80 {lab=VDD}
N -360 -90 -360 -20 {lab=VDD}
N -560 -90 -360 -90 {lab=VDD}
N -560 20 -560 350 {lab=VSS}
N -560 350 -80 350 {lab=VSS}
N -80 350 -80 360 {lab=VSS}
N -360 60 -360 350 {lab=VSS}
N -340 -180 -340 -60 {lab=VSS}
N -340 -60 -120 -60 {lab=VSS}
N -120 -140 -120 -60 {lab=VSS}
N -120 -60 -120 350 {lab=VSS}
N -80 350 50 350 {lab=VSS}
N 230 80 230 350 {lab=VSS}
N 50 350 230 350 {lab=VSS}
N 540 100 540 350 {lab=VSS}
N 230 350 540 350 {lab=VSS}
N 450 -150 450 350 {lab=VSS}
N 240 -180 240 -110 {lab=VSS}
N 240 -110 450 -110 {lab=VSS}
N -200 -520 -170 -520 {lab=VDD}
N -200 -670 -200 -520 {lab=VDD}
N -40 -520 -40 350 {lab=VSS}
N -120 -300 -120 -270 {lab=VDD}
N -340 -300 -120 -300 {lab=VDD}
N 50 40 50 350 {lab=VSS}
N -280 -390 -280 -260 {lab=#net7}
N -100 -580 -100 -550 {lab=CLK}
C {tg.sym} -360 -200 0 1 {name=x1}
C {tg.sym} -540 0 0 0 {name=x2}
C {tg.sym} 70 20 0 0 {name=x3}
C {tg.sym} 220 -200 0 1 {name=x4}
C {nand2.sym} -310 20 0 0 {name=x5}
C {nand2.sym} 280 40 0 0 {name=x6}
C {inv.sym} -190 -200 0 1 {name=x7}
C {inv.sym} 610 40 0 0 {name=x8}
C {inv.sym} 380 -200 0 1 {name=x9}
C {ipin.sym} -700 0 0 0 {name=p1 lab=D}
C {ipin.sym} -10 -580 1 0 {name=p2 lab=CLK}
C {ipin.sym} -30 240 3 0 {name=p3 lab=RST_N}
C {opin.sym} 670 40 0 0 {name=p4 lab=Q}
C {iopin.sym} -60 -690 3 0 {name=p5 lab=VDD}
C {iopin.sym} -80 360 1 0 {name=p6 lab=VSS}
C {inv.sym} -100 -450 3 1 {name=x10}
