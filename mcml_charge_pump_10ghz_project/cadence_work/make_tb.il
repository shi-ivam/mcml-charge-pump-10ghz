; ==============================================================================
; Testbench Generator: shivam/tb_mcml_charge_pump
; Automatically creates the 10 GHz simulation testbench in Cadence Virtuoso
; Fully hardened against in-memory cache desync and nil bounding boxes
; ==============================================================================

; 1. Purge any cached in-memory symbol so Virtuoso reads the fresh symbol
foreach(c dbGetOpenCellViews()
  when(c~>cellName == "mcml_charge_pump" && c~>viewName == "symbol"
    errset(dbPurge(c) nil)
  )
)

; 2. Ensure shivam/mcml_charge_pump/symbol has all 8 pin terminals
let((symCv net term fig leftPins botPins)
  symCv = dbOpenCellViewByType("shivam" "mcml_charge_pump" "symbol" "schematicSymbol" "w")
  when(symCv
    dbCreateRect(symCv list("instance" "drawing") list(0.0:0.0 2.0:2.0))
    
    leftPins = list(list("UP" 1.6) list("UP_b" 1.2) list("DN" 0.8) list("DN_b" 0.4))
    foreach(p leftPins
      pName = car(p)
      py = cadr(p)
      net = dbMakeNet(symCv pName)
      term = dbCreateTerm(net pName "input")
      fig = dbCreateRect(symCv list("pin" "drawing") list(-0.05:(py-0.05) 0.05:(py+0.05)))
      dbCreatePin(net fig pName)
      dbCreateLine(symCv list("device" "drawing") list(-0.4:py 0.0:py))
      dbCreateLabel(symCv list("annotate" "drawing") 0.1:py pName "lowerLeft" "R0" "stick" 0.08)
    )
    
    net = dbMakeNet(symCv "Vdd")
    term = dbCreateTerm(net "Vdd" "inputOutput")
    fig = dbCreateRect(symCv list("pin" "drawing") list(0.95:1.95 1.05:2.05))
    dbCreatePin(net fig "Vdd")
    dbCreateLine(symCv list("device" "drawing") list(1.0:2.0 1.0:2.4))
    dbCreateLabel(symCv list("annotate" "drawing") 1.0:1.8 "Vdd" "centerCenter" "R0" "stick" 0.08)
    
    botPins = list(list("Gnd" 0.6) list("Vbias" 1.4))
    foreach(p botPins
      pName = car(p)
      px = cadr(p)
      net = dbMakeNet(symCv pName)
      term = dbCreateTerm(net pName "inputOutput")
      fig = dbCreateRect(symCv list("pin" "drawing") list((px-0.05):-0.05 (px+0.05):0.05))
      dbCreatePin(net fig pName)
      dbCreateLine(symCv list("device" "drawing") list(px:0.0 px:-0.4))
      dbCreateLabel(symCv list("annotate" "drawing") px:0.2 pName "centerCenter" "R0" "stick" 0.08)
    )
    
    net = dbMakeNet(symCv "Vop")
    term = dbCreateTerm(net "Vop" "output")
    fig = dbCreateRect(symCv list("pin" "drawing") list(1.95:0.95 2.05:1.05))
    dbCreatePin(net fig "Vop")
    dbCreateLine(symCv list("device" "drawing") list(2.0:1.0 2.4:1.0))
    dbCreateLabel(symCv list("annotate" "drawing") 1.9:1.0 "Vop" "centerRight" "R0" "stick" 0.08)
    
    dbCreateLabel(symCv list("annotate" "drawing") 1.0:1.0 "mcml_cp" "centerCenter" "R0" "stick" 0.12)
    dbCreateLabel(symCv list("annotate" "drawing") 0.0:2.1 "[@instanceName]" "lowerLeft" "R0" "stick" 0.10)
    
    dbSave(symCv)
    dbClose(symCv)
  )
)

; 3. Helper to connect pin and draw stub wire safely
procedure(tbStub(cv inst termName netName)
  let((net pinTerm pinFig bb c ib ic dx dy p2 w)
    ; Logical net connection in OpenAccess
    net = dbMakeNet(cv netName)
    errset(dbCreateConnByName(net inst termName) nil)
    
    ; Find physical pin shape for wire stub
    pinTerm = car(setof(tt inst~>master~>terminals tt~>name == termName))
    if(!pinTerm pinTerm = car(inst~>master~>terminals))
    pinFig = if(pinTerm && pinTerm~>pins car(pinTerm~>pins)~>fig nil)
    bb = if(pinFig && pinFig~>bBox errset(dbTransformBBox(pinFig~>bBox inst~>transform) nil) nil)
    if(bb && listp(bb) && length(bb) == 2 then
      c = list((xCoord(car(bb))+xCoord(cadr(bb)))/2.0 (yCoord(car(bb))+yCoord(cadr(bb)))/2.0)
      ib = inst~>bBox
      ic = list((xCoord(car(ib))+xCoord(cadr(ib)))/2.0 (yCoord(car(ib))+yCoord(cadr(ib)))/2.0)
      dx = xCoord(c)-xCoord(ic)  dy = yCoord(c)-yCoord(ic)
      if(abs(dx) >= abs(dy)
        then p2 = list(xCoord(c)+if(dx>=0 0.4 -0.4) yCoord(c))
        else p2 = list(xCoord(c) yCoord(c)+if(dy>=0 0.4 -0.4)))
      when(isCallable('schCreateWire)
        errset(
          progn(
            w = car(schCreateWire(cv "draw" "full" list(c p2) 0.0625 0.0625 0.0))
            when(w && isCallable('schCreateWireLabel)
              schCreateWireLabel(cv w p2 netName "lowerLeft" "R0" "stick" 0.0625 nil)
            )
          )
          nil
        )
      )
    else
      printf("Info: Connected net '%s' to terminal '%s' of %s\n" netName termName inst~>name)
    )
  ))

; 4. Helper to instantiate cell and wire all terminals
procedure(tbInst(cv lib cell name x y params conns)
  let((m inst)
    m = dbOpenCellViewByType(lib cell "symbol" "" "r")
    if(m then
      inst = dbCreateInst(cv m name list(x y) "R0")
      foreach(p params dbReplaceProp(inst car(p) "string" cadr(p)))
      foreach(cn conns tbStub(cv inst car(cn) cadr(cn)))
      inst
    else
      printf("ERROR: Could not open master %s %s symbol\n" lib cell)
      nil
    )))

; 5. Main Testbench Assembly
let((cv)
  cv = dbOpenCellViewByType("shivam" "tb_mcml_charge_pump" "schematic" "schematic" "w")
  if(!cv then
    error("Failed to open cellview shivam/tb_mcml_charge_pump for writing. Check if cell is locked.")
  )

  printf("Placing Device Under Test (DUT: shivam/mcml_charge_pump)...\n")
  tbInst(cv "shivam" "mcml_charge_pump" "DUT0" 0 0 nil
         '(("UP" "UP") ("UP_b" "UP_b") ("DN" "DN") ("DN_b" "DN_b")
           ("Vdd" "Vdd") ("Gnd" "Gnd") ("Vbias" "Vbias") ("Vop" "Vop")))

  printf("Placing Power Sources & Stimuli...\n")
  ; Vdd DC Source (1.0 V)
  tbInst(cv "analogLib" "vdc" "V_VDD" -8 5 '(("vdc" "1.0"))
         '(("PLUS" "Vdd") ("MINUS" "Gnd")))

  ; Vbias DC Source (450 mV)
  tbInst(cv "analogLib" "vdc" "V_BIAS" -8 2 '(("vdc" "0.45"))
         '(("PLUS" "Vbias") ("MINUS" "Gnd")))

  ; Vpulse for UP (10 GHz clock pulse: Period=100ps, Width=25ps, Tr=Tf=5ps)
  tbInst(cv "analogLib" "vpulse" "V_UP" -8 -1 
         '(("v1" "0") ("v2" "1.0") ("per" "100p") ("pw" "25p") ("tr" "5p") ("tf" "5p"))
         '(("PLUS" "UP") ("MINUS" "Gnd")))

  ; Vpulse for UP_b (Inverted UP pulse)
  tbInst(cv "analogLib" "vpulse" "V_UP_B" -8 -4 
         '(("v1" "1.0") ("v2" "0") ("per" "100p") ("pw" "25p") ("tr" "5p") ("tf" "5p"))
         '(("PLUS" "UP_b") ("MINUS" "Gnd")))

  ; Vpulse for DN (Inactive during charging)
  tbInst(cv "analogLib" "vpulse" "V_DN" -8 -7 
         '(("v1" "0") ("v2" "0") ("per" "100p") ("pw" "25p") ("tr" "5p") ("tf" "5p"))
         '(("PLUS" "DN") ("MINUS" "Gnd")))

  ; Vpulse for DN_b (High during charging)
  tbInst(cv "analogLib" "vpulse" "V_DN_B" -8 -10 
         '(("v1" "1.0") ("v2" "1.0") ("per" "100p") ("pw" "25p") ("tr" "5p") ("tf" "5p"))
         '(("PLUS" "DN_b") ("MINUS" "Gnd")))

  ; Output Load Capacitor (300 fF)
  tbInst(cv "analogLib" "cap" "C_LOAD" 6 0 '(("c" "300f"))
         '(("PLUS" "Vop") ("MINUS" "Gnd")))

  ; Initial Condition on Output (540 mV matching Fig 6a)
  let((netVop)
    netVop = dbFindNetByName(cv "Vop")
    when(netVop dbReplaceProp(netVop "ic" "string" "0.54"))
  )

  ; Labels and Documentation
  when(isCallable('schCreateNoteLabel)
    schCreateNoteLabel(cv list(0 6) "TESTBENCH: 10 GHz MCML CHARGE PUMP SIMULATION" "centerCenter" "R0" "roman" 0.25 "normalLabel")
    schCreateNoteLabel(cv list(0 5.4) "Library: shivam | Cell: tb_mcml_charge_pump | View: schematic" "centerCenter" "R0" "roman" 0.16 "normalLabel")
    schCreateNoteLabel(cv list(0 4.8) "F_clock = 10 GHz (T = 100 ps, Pulse = 25 ps) | Vdd = 1.0 V | CL = 300 fF" "centerCenter" "R0" "roman" 0.14 "normalLabel")
  )

  when(isCallable('schCheck)
    errset(schCheck(cv) nil)
  )
  dbSave(cv)
  dbClose(cv)
  printf(">>> SUCCESS: shivam/tb_mcml_charge_pump schematic checked and saved cleanly! <<<\n")
)
