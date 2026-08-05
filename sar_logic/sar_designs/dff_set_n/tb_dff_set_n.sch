v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -200 40 -200 70 {lab=SET_N}
N -200 40 -30 40 {lab=SET_N}
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
C {vsource.sym} -200 100 0 0 {name=VSET value="PWL(0 0 30n 0 31n 3.3 374n 3.3 375n 0 425n 0 426n 3.3 750n 3.3)" savecurrent=false}
C {vsource.sym} -270 100 0 0 {name=VCLK value="PULSE(0 3.3 50n 1n 1n 40n 100n)" savecurrent=false}
C {vsource.sym} -350 100 0 0 {name=VDATA value="PWL(0 0 79n 0 80n 3.3 179n 3.3 180n 0 479n 0 480n 3.3 579n 3.3 580n 0 750n 0)" savecurrent=false}
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
.options method=gear reltol=1e-3 abstol=1e-12 vntol=1e-6

.control
  save all
  tran 10p 750n

  meas tran q020 FIND v(Q) AT=20n
  meas tran q070 FIND v(Q) AT=70n
  meas tran q120 FIND v(Q) AT=120n
  meas tran q170 FIND v(Q) AT=170n
  meas tran q220 FIND v(Q) AT=220n
  meas tran q270 FIND v(Q) AT=270n
  meas tran q370 FIND v(Q) AT=370n
  meas tran q385 FIND v(Q) AT=385n
  meas tran q415 FIND v(Q) AT=415n
  meas tran q440 FIND v(Q) AT=440n
  meas tran q470 FIND v(Q) AT=470n
  meas tran q570 FIND v(Q) AT=570n
  meas tran q670 FIND v(Q) AT=670n

  meas tran tcq_rise TRIG v(CLK) VAL=1.65 RISE=1 TD=100n \\
    TARG v(Q) VAL=1.65 RISE=1 TD=149n
  meas tran tcq_fall TRIG v(CLK) VAL=1.65 RISE=1 TD=200n \\
    TARG v(Q) VAL=1.65 FALL=1 TD=249n
  meas tran t_async_set TRIG v(SET_N) VAL=1.65 FALL=1 TD=370n \\
    TARG v(Q) VAL=1.65 RISE=1 TD=374n

  let failures = 0

  if q020 < 2.97
    echo FAIL_q020_preset_did_not_force_Q_high
    let failures = failures + 1
  end

  if q070 > 0.33
    echo FAIL_q070_Q_should_capture_low
    let failures = failures + 1
  end

  if q120 > 0.33
    echo FAIL_q120_Q_changed_before_rising_edge
    let failures = failures + 1
  end

  if q170 < 2.97
    echo FAIL_q170_Q_did_not_capture_high
    let failures = failures + 1
  end

  if q220 < 2.97
    echo FAIL_q220_Q_did_not_hold_high
    let failures = failures + 1
  end

  if q270 > 0.33
    echo FAIL_q270_Q_did_not_capture_low
    let failures = failures + 1
  end

  if q370 > 0.33
    echo FAIL_q370_Q_should_still_be_low
    let failures = failures + 1
  end

  if q385 < 2.97
    echo FAIL_q385_async_preset_did_not_force_Q_high
    let failures = failures + 1
  end

  if q415 < 2.97
    echo FAIL_q415_Q_did_not_remain_preset
    let failures = failures + 1
  end

  if q440 < 2.97
    echo FAIL_q440_Q_changed_immediately_after_preset_release
    let failures = failures + 1
  end

  if q470 > 0.33
    echo FAIL_q470_Q_should_capture_low
    let failures = failures + 1
  end

  if q570 < 2.97
    echo FAIL_q570_Q_should_capture_high
    let failures = failures + 1
  end

  if q670 > 0.33
    echo FAIL_q670_Q_should_capture_low
    let failures = failures + 1
  end

  echo
  echo MEASURED_DELAYS
  print tcq_rise tcq_fall t_async_set
  echo

  if failures < 0.5
    echo PASS_tb_dff_set_n_all_functional_checks_passed
  else
    echo FAIL_tb_dff_set_n
    print failures
  end

  write tb_dff_set_n.raw
  plot v(CLK) v(D) v(SET_N) v(Q)
.endc
"}
C {lab_pin.sym} -220 -220 0 0 {name=p1 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -200 -90 0 0 {name=p2 sig_type=std_logic lab=D}
C {lab_pin.sym} -160 -20 0 0 {name=p3 sig_type=std_logic lab=CLK}
C {lab_pin.sym} -130 40 0 0 {name=p4 sig_type=std_logic lab=SET_N}
C {lab_pin.sym} 230 -20 0 0 {name=p5 sig_type=std_logic lab=Q}
C {dff_set_n.sym} 50 -20 0 0 {name=x1}
