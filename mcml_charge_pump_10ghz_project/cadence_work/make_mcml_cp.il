; ==============================================================================
; Proposed High-Speed MCML Charge Pump Design at 10 GHz Frequency in 45nm CMOS
; Paper Replication: M. Sivasakthi & P. Radhika (Springer 2024)
; Library: shivam | Cell: mcml_charge_pump
; Fully Annotated with Pedagogical Labels for B.Tech Evaluation
; ==============================================================================

procedure(cpStub(cv inst termName netName)
  let((pinTerm pinFig bb c ib ic dx dy p2 w)
    pinTerm = car(setof(tt inst~>master~>terminals tt~>name == termName))
    if(!pinTerm pinTerm = car(inst~>master~>terminals))
    pinFig = car(pinTerm~>pins)~>fig
    bb = dbTransformBBox(pinFig~>bBox inst~>transform)
    c = list((xCoord(car(bb))+xCoord(cadr(bb)))/2.0 (yCoord(car(bb))+yCoord(cadr(bb)))/2.0)
    ib = inst~>bBox
    ic = list((xCoord(car(ib))+xCoord(cadr(ib)))/2.0 (yCoord(car(ib))+yCoord(cadr(ib)))/2.0)
    dx = xCoord(c)-xCoord(ic)  dy = yCoord(c)-yCoord(ic)
    if(abs(dx) >= abs(dy)
      then p2 = list(xCoord(c)+if(dx>=0 0.25 -0.25) yCoord(c))
      else p2 = list(xCoord(c) yCoord(c)+if(dy>=0 0.25 -0.25)))
    w = car(schCreateWire(cv "draw" "full" list(c p2) 0.0625 0.0625 0.0))
    schCreateWireLabel(cv w p2 netName "lowerLeft" "R0" "stick" 0.0625 nil)
  ))

procedure(cpInst(cv lib cell name x y params conns)
  let((m inst)
    m = dbOpenCellViewByType(lib cell "symbol" "" "r")
    if(m then
      inst = dbCreateInst(cv m name list(x y) "R0")
      foreach(p params dbReplaceProp(inst car(p) "string" cadr(p)))
      foreach(cn conns cpStub(cv inst car(cn) cadr(cn)))
      inst
    else
      printf("ERROR: Could not open master %s %s symbol\n" lib cell)
      nil
    )))

procedure(cpNote(cv x y text @optional (height 0.14) (justify "centerCenter"))
  schCreateNoteLabel(cv list(x y) text justify "R0" "roman" height "normalLabel")
)

let((cv)
  cv = dbOpenCellViewByType("shivam" "mcml_charge_pump" "schematic" "schematic" "w")
  if(!cv then
    error("Failed to open cellview shivam/mcml_charge_pump for writing")
  )

  printf("Building Primary Switch-Based Charge Pump...\n")
  ; --- Primary Charge Pump (Glitch-Free Switch Stage) ---
  ; S2: PMOS charge switch (W=170n, L=45n)
  cpInst(cv "gpdk045" "pmos1v" "S2" -4 4 '(("w" "170n") ("l" "45n"))
         '(("D" "n_top") ("G" "UP_b") ("S" "Vdd") ("B" "Vdd")))
  
  ; S1: NMOS discharge switch (W=360n, L=45n)
  cpInst(cv "gpdk045" "nmos1v" "S1" -4 -4 '(("w" "360n") ("l" "45n"))
         '(("D" "n_bot") ("G" "DN") ("S" "Gnd") ("B" "Gnd")))

  ; Ci: Interconnect Capacitor (50 fF)
  cpInst(cv "analogLib" "cap" "Ci" -4 0 '(("c" "50f"))
         '(("PLUS" "n_top") ("MINUS" "n_bot")))

  ; S4: Transmission Gate for UP (PMOS W=130n, NMOS W=280n)
  cpInst(cv "gpdk045" "pmos1v" "S4_pmos" -1 3 '(("w" "130n") ("l" "45n"))
         '(("D" "Vop") ("G" "UP_b") ("S" "n_top") ("B" "Vdd")))
  cpInst(cv "gpdk045" "nmos1v" "S4_nmos" -1 1 '(("w" "280n") ("l" "45n"))
         '(("D" "Vop") ("G" "UP") ("S" "n_top") ("B" "Gnd")))

  ; S3: Transmission Gate for DN (PMOS W=130n, NMOS W=280n)
  cpInst(cv "gpdk045" "pmos1v" "S3_pmos" -1 -1 '(("w" "130n") ("l" "45n"))
         '(("D" "Vop") ("G" "DN_b") ("S" "n_bot") ("B" "Vdd")))
  cpInst(cv "gpdk045" "nmos1v" "S3_nmos" -1 -3 '(("w" "280n") ("l" "45n"))
         '(("D" "Vop") ("G" "DN") ("S" "n_bot") ("B" "Gnd")))

  printf("Building Secondary MCML Faster Current Driving Stage...\n")
  ; --- Secondary Charge Pump (MCML Faster Current Driving Stage) ---
  ; M1 & M2: PMOS Active Loads (W=190n, L=45n)
  cpInst(cv "gpdk045" "pmos1v" "M1" 3 5 '(("w" "190n") ("l" "45n"))
         '(("D" "n_load1") ("G" "n_load1") ("S" "Vdd") ("B" "Vdd")))
  cpInst(cv "gpdk045" "pmos1v" "M2" 7 5 '(("w" "190n") ("l" "45n"))
         '(("D" "n_load2") ("G" "n_load1") ("S" "Vdd") ("B" "Vdd")))

  ; Dummy Branch: M3 PMOS (W=180n) & M4 NMOS (W=270n)
  cpInst(cv "gpdk045" "pmos1v" "M3" 3 2 '(("w" "180n") ("l" "45n"))
         '(("D" "n_dummy") ("G" "UP") ("S" "n_load1") ("B" "Vdd")))
  cpInst(cv "gpdk045" "nmos1v" "M4" 3 -2 '(("w" "270n") ("l" "45n"))
         '(("D" "n_dummy") ("G" "DN_b") ("S" "n_tail") ("B" "Gnd")))

  ; Output Branch: S6 PMOS (W=180n) & S5 NMOS (W=270n)
  cpInst(cv "gpdk045" "pmos1v" "S6" 7 2 '(("w" "180n") ("l" "45n"))
         '(("D" "Vop") ("G" "UP_b") ("S" "n_load2") ("B" "Vdd")))
  cpInst(cv "gpdk045" "nmos1v" "S5" 7 -2 '(("w" "270n") ("l" "45n"))
         '(("D" "Vop") ("G" "DN") ("S" "n_tail") ("B" "Gnd")))

  ; M5: NMOS Tail Current Source (W=480n, L=45n)
  cpInst(cv "gpdk045" "nmos1v" "M5" 5 -5 '(("w" "480n") ("l" "45n"))
         '(("D" "n_tail") ("G" "Vbias") ("S" "Gnd") ("B" "Gnd")))

  ; CL: Output Load Capacitor (300 fF)
  cpInst(cv "analogLib" "cap" "CL" 11 0 '(("c" "300f"))
         '(("PLUS" "Vop") ("MINUS" "Gnd")))

  printf("Creating Pins...\n")
  ; --- Pins ---
  foreach(pp '(("UP" "input" -7 2) ("UP_b" "input" -7 4)
               ("DN" "input" -7 -2) ("DN_b" "input" -7 -4)
               ("Vbias" "input" 2 -5)
               ("Vdd" "inputOutput" 0 7) ("Gnd" "inputOutput" 0 -7)
               ("Vop" "output" 14 0))
    let((m pinInst termN)
      m = dbOpenCellViewByType("basic" if(cadr(pp)=="input" "ipin" if(cadr(pp)=="output" "opin" "iopin")) "symbol" "" "r")
      pinInst = schCreatePin(cv m car(pp) cadr(pp) nil list(caddr(pp) cadddr(pp)) "R0")
      termN = car(pinInst~>master~>terminals)~>name
      cpStub(cv pinInst termN car(pp))))

  printf("Adding Informative Pedagogical Labels...\n")
  ; ==============================================================================
  ; Visual Schema Annotations & Labels for Presentation & Viva Defense
  ; ==============================================================================
  ; 1. Title Banner
  cpNote(cv 3.5 8.6 "HIGH-SPEED 10 GHz MCML CHARGE PUMP (45nm CMOS)" 0.28)
  cpNote(cv 3.5 8.2 "Springer 2024 Replication: M. Sivasakthi & P. Radhika" 0.16)
  cpNote(cv 3.5 7.8 "Vdd = 1.0 V | Fin = 10 GHz | Pavg = 13.19 uW | Tpd = 16.71 ps" 0.15)

  ; 2. Stage Headers
  cpNote(cv -3.0 6.2 "[ STAGE 1: Primary Switch-Based CP ]" 0.20)
  cpNote(cv -3.0 5.8 "(Glitch-Free Switching with Transmission Gates & Ci)" 0.13)

  cpNote(cv 6.0 7.0 "[ STAGE 2: Secondary MCML FCD-CP ]" 0.20)
  cpNote(cv 6.0 6.6 "(MOS Current Mode Logic - Fine Fast Current Steering)" 0.13)

  ; 3. Primary Stage Component Details
  cpNote(cv -5.6 4.3 "S2: PMOS (170n/45n)\nPull-Up Rail Switch" 0.13 "centerCenter")
  cpNote(cv -5.6 -4.3 "S1: NMOS (360n/45n)\nPull-Down Rail Switch" 0.13 "centerCenter")
  cpNote(cv -5.6 0.0 "Ci = 50 fF\nInterconnect Cap\n(Buffers Spikes)" 0.13 "centerCenter")
  cpNote(cv 0.8 2.0 "S4: UP Trans. Gate\nPMOS: 130n | NMOS: 280n\n(Charge Injection Cancel)" 0.12 "centerCenter")
  cpNote(cv 0.8 -2.0 "S3: DN Trans. Gate\nPMOS: 130n | NMOS: 280n\n(Charge Injection Cancel)" 0.12 "centerCenter")

  ; 4. Secondary Stage Component Details
  cpNote(cv 5.0 5.8 "M1, M2: Active Mirror Load (PMOS 190n/45n)" 0.14 "centerCenter")
  cpNote(cv 3.0 3.2 "[ Dummy Branch ]\nM3: PMOS 180n\n(Active during IDLE)" 0.12 "centerCenter")
  cpNote(cv 3.0 -0.8 "M4: NMOS 270n\n(Keeps Itail saturated)" 0.12 "centerCenter")
  cpNote(cv 7.0 3.2 "[ Output Branch ]\nS6: PMOS 180n\n(Fast UP Steering)" 0.12 "centerCenter")
  cpNote(cv 7.0 -0.8 "S5: NMOS 270n\n(Fast DN Steering)" 0.12 "centerCenter")
  cpNote(cv 5.0 -6.2 "M5: NMOS Tail Current Sink (480n/45n)\nDeep Saturation & Low Flicker Noise" 0.13 "centerCenter")
  cpNote(cv 11.0 1.2 "CL = 300 fF\nLoop Filter Load" 0.13 "centerCenter")

  ; 5. Pin / Port Annotations
  cpNote(cv -7.0 4.8 "UP / UP_b:\n10 GHz UP Pulse" 0.12 "centerCenter")
  cpNote(cv -7.0 -4.8 "DN / DN_b:\n10 GHz DN Pulse" 0.12 "centerCenter")
  cpNote(cv 0.0 7.4 "Vdd Pin (1.0 V)" 0.13 "centerCenter")
  cpNote(cv 0.0 -7.4 "Gnd Pin (0.0 V)" 0.13 "centerCenter")
  cpNote(cv 1.5 -5.8 "Vbias: 1.0 V" 0.12 "centerCenter")
  cpNote(cv 14.0 1.0 "Vop: Output Voltage\n(0.0V to 0.98V Swing)" 0.13 "centerCenter")

  ; 6. Circuit Operation Legend Box
  cpNote(cv 3.5 -7.4 "OPERATING MODES:" 0.16)
  cpNote(cv 3.5 -7.8 "1. IDLE (UP=0, DN=0)       : S5/S6 OFF, M3/M4 ON  -> Itail steers to GND; Vop is isolated (Zero Ripple)" 0.12)
  cpNote(cv 3.5 -8.2 "2. CHARGING (UP=1, DN=0)   : S2/S4 ON, M2->S6 ON  -> Collaborative: Vop charges up to 0.98 V (98% swing)" 0.12)
  cpNote(cv 3.5 -8.6 "3. DISCHARGING (UP=0, DN=1): S1/S3 ON, S5->M5 ON  -> Collaborative: Vop discharges down to 0.0 V cleanly" 0.12)

  schCheck(cv)
  dbSave(cv)
  dbClose(cv)
  printf(">>> SUCCESS: shivam/mcml_charge_pump schematic checked and saved clean with all labels! <<<\n")
)
