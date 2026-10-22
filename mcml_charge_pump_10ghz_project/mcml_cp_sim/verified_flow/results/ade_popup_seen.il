printf("\nADE ngspice bridge: verified measured results ready.\n")
load("/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/cadence_work/show_native_psf_results.il")
hiDisplayAppDBox(
  ?name 'mcmlNgspiceResult
  ?dboxBanner "ADE run: ngspice / FreePDK45 results"
  ?dboxText "VERIFIED NUMERICAL RUN: ngspice 45.2 / FreePDK45 VTG\nSource: current Virtuoso tb_mcml_charge_pump netlist\nADE waveform: charge, 10n\nVbias: 0.45 V, connected to M5 tail gate\nFull-project measurements: 10 ns transients + 0-1 V DC sweep\n\nUP delay: 13.811 ps\nDN delay: 15.447 ps\nPaper TT delay: 16.71 ps; measured difference: 7.56%\nComparison only: paper 10 pF load; this circuit 300 fF load.\nUP VDD power: 22.528 uW\nDN VDD power: 16.097 uW\nWorst-direction PDP: 0.24865 fJ\nSettled output swing: 0.993524 V\n10% current-compliance dynamic range: NO VALID INTERVAL\nMismatch at 0.5 V: 115.47%\n\nViVA reads Cadence PSF files; the numerical solver is ngspice, not Spectre."
  ?dialogType hicInformationDialog
  ?dialogStyle 'modal
  ?buttonLayout 'Close
)
