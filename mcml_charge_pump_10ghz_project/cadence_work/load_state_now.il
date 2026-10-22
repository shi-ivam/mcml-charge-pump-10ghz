; Archived helper: the old state targets the DUT instead of the wired testbench.
error("Old ADE state helper disabled. Open shivam/tb_mcml_charge_pump/schematic and load its step1_final state.\n")
; ==============================================================================
; CADENCE VIRTUOSO: INSTANT ADE L STATE LOADER
; Loads the 10 GHz MCML Charge Pump simulation state into ADE L with 1 command
; ==============================================================================

let((sess loaded)
  loaded = nil
  ; Find any active ADE L session
  foreach(s (list (and (boundp 'sevSession1) sevSession1)
                  (and (boundp 'sevSession2) sevSession2)
                  (and (boundp 'sevSession3) sevSession3)
                  (and (fboundp 'sevSession) (sevSession (getCurrentWindow()))))
    when(s && !loaded
      errset(
        progn(
          sevLoadState(s "state1")
          printf("\n>>> SUCCESS: Loaded 'state1' into ADE L session %L! <<<\n" s)
          printf("    - Analyses: 10 ns transient (10 GHz clock)\n")
          printf("    - Models: gpdk045 BSIM4 level 54\n")
          printf("    - Outputs: /Vop, /UP, /DN, /n_tail\n")
          printf("    -> Click the green 'Netlist and Run' button in ADE L to simulate!\n\n")
          loaded = t
        )
        nil
      )
    )
  )

  unless(loaded
    printf("\n>>> To load state in ADE L GUI:\n")
    printf("    1. In ADE L, click: Session -> Load State...\n")
    printf("    2. Under 'What to Load', select: Directory\n")
    printf("    3. Directory is set to: /home/shivam/.artist_states\n")
    printf("    4. Click on 'state1' or 'spectre_state1' in the State Name box, then click OK.\n\n")
  )
  loaded
)
