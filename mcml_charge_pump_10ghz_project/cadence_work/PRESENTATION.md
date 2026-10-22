# Tomorrow's MCML charge-pump demo

## Before the demo

1. Keep the Cadence container running. Check `systemctl --user is-active mcml-ade-bridge.service`; it should say `active`. If needed, start it with `systemctl --user start mcml-ade-bridge.service`.
2. Restart Virtuoso from this `cadence_work` directory to load `.cdsinit`. In an already open Virtuoso, enter `load("/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/cadence_work/ade_ngspice_ui.il")` in CIW once.
3. Open `shivam/tb_mcml_charge_pump/schematic`, **not** the DUT as the ADE design. Check and Save. `V_BIAS=0.45 V` drives the `Vbias` net and M5 tail gate. `V_VDD=1 V`; UP/UP_b pulse; DN=0 V; DN_b=1 V; real gnd; only internal CL=300 fF.
4. Launch ADE L from the testbench. Load the testbench's `step1_final` state if useful; confirm transient stop `10n`, maximum step `0.5p`, temperature 27 °C.
5. Click **Netlist and Run**. Wait about 20–30 seconds. The host ngspice bridge produces binary Cadence PSF waveforms, separate four-strip ViVA windows for charging and discharging, and the result popup. If the Spectre-specific `ADE-3070` warning appears, show the actual ngspice bridge log and ViVA result; the warning is from ADE's unsupported simulator name.

## Results currently measured

| Metric | Value |
|---|---:|
| UP mean delay | 13.811 ps |
| DN mean delay | 15.447 ps |
| Paper TT delay comparison | 16.710 ps reference; measured delay is 7.56% lower (different load and models) |
| UP VDD power | 22.528 µW |
| DN VDD power | 16.097 µW |
| Worst-direction PDP | 0.24865 fJ |
| Settled output swing | 0.993524 V |
| 10% current-compliance dynamic range | No valid interval at 0.5 V; 115.47% UP/DN mismatch |

**What to say:** “The schematic and ADE launch are inside Virtuoso. This machine lacks licensed Spectre, so ADE's Netlist and Run invokes ngspice 45.2 through a local bridge. The waveforms and calculations are numerical ngspice results from the current Virtuoso netlist, with FreePDK45 nominal VTG models. They are not Cadence Spectre or foundry signoff results.”

Show `/home/shivam/simulation/tb_mcml_charge_pump/spectre/schematic/psf/spectre.out` for the solver label and netlist hash, `mcml_cp_sim/verified_flow/results/verified_results.png` for the plots, and `mcml_cp_sim/verified_flow/results/metrics.json` for all measured values and model hashes. The complete procedure is in `../../GUIDE.md`.
