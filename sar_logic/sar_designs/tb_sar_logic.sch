v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 120 80 260 80 {lab=BIT_0}
N 260 80 260 100 {lab=BIT_0}
N 120 60 320 60 {lab=BIT_1}
N 320 60 320 100 {lab=BIT_1}
N 120 40 390 40 {lab=BIT_2}
N 390 40 390 100 {lab=BIT_2}
N 120 20 460 20 {lab=BIT_3}
N 460 20 460 100 {lab=BIT_3}
N 120 0 530 -0 {lab=BIT_4}
N 530 0 530 100 {lab=BIT_4}
N 120 -20 600 -20 {lab=BIT_5}
N 600 -20 600 100 {lab=BIT_5}
N 120 -40 670 -40 {lab=BIT_6}
N 670 -40 670 100 {lab=BIT_6}
N 120 -60 740 -60 {lab=BIT_7}
N 740 -60 740 100 {lab=BIT_7}
N 120 -100 880 -100 {lab=EOC}
N 880 -100 880 100 {lab=EOC}
N 740 160 740 220 {lab=0}
N 670 160 670 220 {lab=0}
N 600 160 600 220 {lab=0}
N 530 160 530 220 {lab=0}
N 460 160 460 220 {lab=0}
N 390 160 390 220 {lab=0}
N 320 160 320 220 {lab=0}
N 260 160 260 220 {lab=0}
N -590 60 -590 220 {lab=0}
N -590 -60 -590 -0 {lab=CLK}
N -590 -60 -120 -60 {lab=CLK}
N -520 140 -520 220 {lab=0}
N -520 0 -520 80 {lab=RST_N}
N -520 0 -120 -0 {lab=RST_N}
N -650 -240 0 -240 {lab=VDD}
N 0 -240 0 -160 {lab=VDD}
N -450 60 -120 60 {lab=CMP_OUT}
N -650 -30 -650 220 {lab=0}
N -650 -240 -650 -90 {lab=VDD}
N -650 220 0 220 {lab=0}
N 0 220 880 220 {lab=0}
N 880 160 880 220 {lab=0}
N -0 160 -0 220 {lab=0}
N -450 210 -450 220 {lab=0}
N -450 60 -450 150 {lab=CMP_OUT}
C {sar_logic.sym} 0 0 0 0 {name=XSAR1}
C {vsource.sym} -650 -60 0 0 {name=VVDD value=3.3 savecurrent=false}
C {vsource.sym} -590 30 0 0 {name=VCLK value="PULSE(0 3.3 100n 1n 1n 49n 100n)" savecurrent=false}
C {vsource.sym} -520 110 0 0 {name=VRST value="PULSE(0 3.3 40n 1n 1n 2u 4u)" savecurrent=false}
C {vsource.sym} -450 180 0 0 {name=VCMP value="PWL(0 0 49n 0 50n 3.3 149n 3.3 150n 0 249n 0 250n 3.3 349n 3.3 350n 0 449n 0 450n 3.3 549n 3.3 550n 0 649n 0 650n 3.3 749n 3.3 750n 0 1u 0)" savecurrent=false}
C {capa.sym} 320 130 0 0 {name=CB1
m=1
value=10f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 390 130 0 0 {name=CB2
m=1
value=10f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 460 130 0 0 {name=CB3
m=1
value=10f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 530 130 0 0 {name=CB4
m=1
value=10f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 600 130 0 0 {name=CB5
m=1
value=10f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 670 130 0 0 {name=CB6
m=1
value=10f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 740 130 0 0 {name=CB7
m=1
value=10f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 880 130 0 0 {name=CEOC
m=1
value=10f
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 260 130 0 0 {name=CB0
m=1
value=10f
footprint=1206
device="ceramic capacitor"}
C {gnd.sym} 0 220 0 0 {name=l1 lab=0}
C {lab_pin.sym} 430 -60 0 0 {name=p1 sig_type=std_logic lab=BIT_7}
C {lab_pin.sym} 460 -100 0 0 {name=p2 sig_type=std_logic lab=EOC}
C {lab_pin.sym} 400 -40 0 0 {name=p3 sig_type=std_logic lab=BIT_6}
C {lab_pin.sym} 370 -20 0 0 {name=p4 sig_type=std_logic lab=BIT_5}
C {lab_pin.sym} 340 0 0 0 {name=p5 sig_type=std_logic lab=BIT_4}
C {lab_pin.sym} 300 20 0 0 {name=p6 sig_type=std_logic lab=BIT_3}
C {lab_pin.sym} 280 40 0 0 {name=p7 sig_type=std_logic lab=BIT_2}
C {lab_pin.sym} 250 60 0 0 {name=p8 sig_type=std_logic lab=BIT_1}
C {lab_pin.sym} 230 80 0 0 {name=p9 sig_type=std_logic lab=BIT_0}
C {lab_pin.sym} -210 60 1 0 {name=p10 sig_type=std_logic lab=CMP_OUT}
C {code_shown.sym} 280 -300 0 0 {name=MODELS
only_toplevel=true
value="
.include /foss/pdks/gf180mcuD/libs.tech/ngspice/design.ngspice
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/sm141064.ngspice typical
.lib /foss/pdks/gf180mcuD/libs.tech/ngspice/smbb000149.ngspice typical
"}
C {code_shown.sym} 980 -300 0 0 {name=MODELS1
only_toplevel=true
value="
.options method=gear reltol=1e-3 abstol=1e-12 vntol=1e-6

.control
  save all
  tran 20p 1u

  * Decode BIT_7 through BIT_0 into an approximately integer-valued waveform.
  * Keep this entire let command on one physical line.
  let sar_code = (128/3.3)*v(BIT_7)+(64/3.3)*v(BIT_6)+(32/3.3)*v(BIT_5)+(16/3.3)*v(BIT_4)+(8/3.3)*v(BIT_3)+(4/3.3)*v(BIT_2)+(2/3.3)*v(BIT_1)+(1/3.3)*v(BIT_0)

  * Sample the walking trial-code sequence.
  meas tran code070 FIND sar_code AT=70n
  meas tran code130 FIND sar_code AT=130n
  meas tran code230 FIND sar_code AT=230n
  meas tran code330 FIND sar_code AT=330n
  meas tran code430 FIND sar_code AT=430n
  meas tran code530 FIND sar_code AT=530n
  meas tran code630 FIND sar_code AT=630n
  meas tran code730 FIND sar_code AT=730n
  meas tran code830 FIND sar_code AT=830n
  meas tran code930 FIND sar_code AT=930n

  * Check EOC before, during, and after completion.
  meas tran eoc070 FIND v(EOC) AT=70n
  meas tran eoc730 FIND v(EOC) AT=730n
  meas tran eoc830 FIND v(EOC) AT=830n
  meas tran eoc930 FIND v(EOC) AT=930n

  * Keep each complete timing measurement on one physical line.
  meas tran tclk8_eoc TRIG v(CLK) VAL=1.65 RISE=8 TARG v(EOC) VAL=1.65 RISE=1
  meas tran eoc_width TRIG v(EOC) VAL=1.65 RISE=1 TARG v(EOC) VAL=1.65 FALL=1

  * Start with a failure value. It is cleared only if the essential
  * measurements were successfully created.
  let failures = 999

  if code930 > -0.5
    if tclk8_eoc > -1
      if eoc_width > 0
        let failures = 0

        * 70 ns: reset-created MSB trial, 10000000 = 128.
        if code070 < 127.5
          echo FAIL_code070_below_128
          let failures = failures + 1
        end
        if code070 > 128.5
          echo FAIL_code070_above_128
          let failures = failures + 1
        end

        * 130 ns: accepted C7 plus bit-6 trial, 11000000 = 192.
        if code130 < 191.5
          echo FAIL_code130_below_192
          let failures = failures + 1
        end
        if code130 > 192.5
          echo FAIL_code130_above_192
          let failures = failures + 1
        end

        * 230 ns: bit-6 rejected and bit-5 trial, 10100000 = 160.
        if code230 < 159.5
          echo FAIL_code230_below_160
          let failures = failures + 1
        end
        if code230 > 160.5
          echo FAIL_code230_above_160
          let failures = failures + 1
        end

        * 330 ns: bit-4 trial, 10110000 = 176.
        if code330 < 175.5
          echo FAIL_code330_below_176
          let failures = failures + 1
        end
        if code330 > 176.5
          echo FAIL_code330_above_176
          let failures = failures + 1
        end

        * 430 ns: bit-4 rejected and bit-3 trial, 10101000 = 168.
        if code430 < 167.5
          echo FAIL_code430_below_168
          let failures = failures + 1
        end
        if code430 > 168.5
          echo FAIL_code430_above_168
          let failures = failures + 1
        end

        * 530 ns: bit-2 trial, 10101100 = 172.
        if code530 < 171.5
          echo FAIL_code530_below_172
          let failures = failures + 1
        end
        if code530 > 172.5
          echo FAIL_code530_above_172
          let failures = failures + 1
        end

        * 630 ns: bit-2 rejected and bit-1 trial, 10101010 = 170.
        if code630 < 169.5
          echo FAIL_code630_below_170
          let failures = failures + 1
        end
        if code630 > 170.5
          echo FAIL_code630_above_170
          let failures = failures + 1
        end

        * 730 ns: bit-0 trial, 10101011 = 171.
        if code730 < 170.5
          echo FAIL_code730_below_171
          let failures = failures + 1
        end
        if code730 > 171.5
          echo FAIL_code730_above_171
          let failures = failures + 1
        end

        * 830 ns: final C0 decision captured, 10101010 = 170.
        if code830 < 169.5
          echo FAIL_code830_below_170
          let failures = failures + 1
        end
        if code830 > 170.5
          echo FAIL_code830_above_170
          let failures = failures + 1
        end

        * 930 ns: EOC clears while the code remains stored.
        if code930 < 169.5
          echo FAIL_code930_below_held_170
          let failures = failures + 1
        end
        if code930 > 170.5
          echo FAIL_code930_above_held_170
          let failures = failures + 1
        end

        * EOC must be low before completion.
        if eoc070 > 0.33
          echo FAIL_EOC_high_at_70ns
          let failures = failures + 1
        end
        if eoc730 > 0.33
          echo FAIL_EOC_high_before_final_capture
          let failures = failures + 1
        end

        * EOC must be high after the eighth clock edge.
        if eoc830 < 2.97
          echo FAIL_EOC_not_high_at_830ns
          let failures = failures + 1
        end

        * EOC must clear after the following edge.
        if eoc930 > 0.33
          echo FAIL_EOC_not_low_at_930ns
          let failures = failures + 1
        end

        * EOC should rise shortly after the eighth clock edge.
        if tclk8_eoc < 0
          echo FAIL_negative_clock_to_EOC_delay
          let failures = failures + 1
        end
        if tclk8_eoc > 10n
          echo FAIL_clock_to_EOC_delay_above_10ns
          let failures = failures + 1
        end

        * EOC should remain high for approximately one 100 ns period.
        if eoc_width < 90n
          echo FAIL_EOC_width_below_90ns
          let failures = failures + 1
        end
        if eoc_width > 110n
          echo FAIL_EOC_width_above_110ns
          let failures = failures + 1
        end
      end
    end
  end

  echo
  echo SAR_SEQUENCE_RESULTS
  print code070 code130 code230 code330 code430
  print code530 code630 code730 code830 code930

  echo
  echo EOC_RESULTS
  print eoc070 eoc730 eoc830 eoc930

  echo
  echo EOC_TIMING
  print tclk8_eoc eoc_width
  echo

  if failures < 0.5
    echo PASS_tb_sar_logic_digital_only
  else
    echo FAIL_tb_sar_logic_digital_only
    print failures
  end

  write tb_sar_logic_digital.raw

  plot v(CLK) v(RST_N) v(CMP_OUT) v(EOC)
  plot v(BIT_7) v(BIT_6) v(BIT_5) v(BIT_4)
  plot v(BIT_3) v(BIT_2) v(BIT_1) v(BIT_0)
.endc
"}
C {lab_pin.sym} -330 -60 1 0 {name=p11 sig_type=std_logic lab=CLK}
C {lab_pin.sym} -280 0 1 0 {name=p12 sig_type=std_logic lab=RST_N}
C {lab_pin.sym} -390 -240 1 0 {name=p13 sig_type=std_logic lab=VDD}
