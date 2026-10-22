; Virtuoso CIW integration for measured ngspice results.
; The ADE Netlist and Run button invokes the local ngspice bridge; this timer
; displays the completed numerical results inside the current Virtuoso session.

procedure(mcmlBridgePoll()
  let((ready seen)
    ready = "/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/ade_popup_ready.il"
    seen = "/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/ade_popup_seen.il"
    when(isFile(ready)
      system(strcat("mv " ready " " seen))
      when(isFile(seen)
        load(seen)
      )
    )
    hiRegTimer("mcmlBridgePoll()" 20)
  )
)

procedure(mcmlShowLastResult()
  load("/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/cadence_work/show_native_psf_results.il")
)

printf("ADE ngspice bridge armed. Netlist and Run will use ngspice/FreePDK45, not Spectre.\n")
hiEnqueueCmd("mcmlBridgePoll()")
