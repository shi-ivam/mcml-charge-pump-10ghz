let((cv s)
  cv = dbOpenCellViewByType("shivam" "mcml_charge_pump" "schematic" "schematic" "r")
  if(cv then
    printf("Schematic terminals: %L\n" cv~>terminals~>name)
    schPinListToSymbol("shivam" "mcml_charge_pump" "symbol" 
      list(
        list("left" list("UP" "UP_b" "DN" "DN_b"))
        list("top" list("Vdd"))
        list("bottom" list("Gnd" "Vbias"))
        list("right" list("Vop"))
      )
    )
    dbClose(cv)
    printf("Symbol generated!\n")
  )
)
