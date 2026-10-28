; Change drawing annotations only. Wire labels and pin names carry connectivity.
let((cv count old new)
  cv=dbOpenCellViewByType("shivam" "mcml_charge_pump" "schematic" "schematic" "a")
  unless(cv error("Cannot open mcml_charge_pump schematic for editing"))
  count=0
  foreach(shape cv~>shapes
    when(shape~>objType=="label" && shape~>purpose=="drawing" && !shape~>parent
      old=shape~>theLabel
      new=lowerCase(old)
      when(old=="Vbias: 1.0 V" new="vbias: 0.45 v (testbench)")
      when(old=="Vdd = 1.0 V | Fin = 10 GHz | Pavg = 13.19 uW | Tpd = 16.71 ps"
        new="paper reference: vdd = 1.0 v | fin = 10 ghz | pavg = 13.19 uw | tpd = 16.71 ps")
      unless(new==old
        shape~>theLabel=new
        count=count+1)
    )
  )
  schCheck(cv)
  dbSave(cv)
  printf("MCML_NOTES_LOWERCASED=%d\n" count)
)
