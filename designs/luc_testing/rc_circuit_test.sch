v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 40 -560 840 -160 {flags=graph
y1=0
y2=2
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-6.5797519e-24
x2=1e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
node=""
color=""
dataset=-1
unitx=1
logx=0
logy=0
}
N 30 -60 30 -40 {lab=0}
N 30 -120 90 -120 {lab=VIN}
N 150 -120 200 -120 {lab=VOUT}
N 200 -60 200 -40 {lab=0}
C {vsource.sym} 30 -90 0 0 {name=V1 value="PULSE(0 1 0.5n 100p 100p 1n 2n)" savecurrent=false}
C {res.sym} 120 -120 1 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {capa.sym} 200 -90 0 0 {name=C1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 200 -40 0 0 {name=l1 lab=0}
C {gnd.sym} 30 -40 0 0 {name=l2 lab=0}
C {lab_wire.sym} 70 -120 0 0 {name=p1 sig_type=std_logic lab=VIN
}
C {lab_wire.sym} 190 -120 0 0 {name=p2 sig_type=std_logic lab=VOUT
}
C {code_shown.sym} 270 -100 0 0 {name=s1 only_toplevel=false 
value="
.tran 100p 10n
.save all

"}
C {launcher.sym} 150 -600 0 0 {name=h5
descr="load waves (press ctrl + left click)"
tclcommand="xschem raw_read $netlist_dir/rc_circuit_test.raw tran"
}
