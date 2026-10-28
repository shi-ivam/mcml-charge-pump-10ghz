# MCML charge-pump simulation guide

This project has one transistor-level DUT, `shivam/mcml_charge_pump/schematic`, and one wired transient testbench, `shivam/tb_mcml_charge_pump/schematic`. The schematic and netlist come from Virtuoso. Two simulation routes are described below:

1. **Professor/lab route:** use a genuine licensed Spectre installation from ADE L and calculate the results in ViVA. This is the route that can be described as a Virtuoso/ADE simulation.
2. **Current-machine route:** press ADE L **Netlist and Run** on the testbench. The installed local adapter sends the Virtuoso netlist to host ngspice with FreePDK45 models, writes a Cadence-readable result, calculates the metrics, and opens labeled ViVA plots and a result popup. This is an ADE-launched, ngspice-simulated result; it is **not** a Spectre result.

The original local `spectre` paths were Python waveform generators, not the Cadence solver. They have been backed up as `spectre.synthetic-backup` and replaced with a transparent ngspice adapter. ADE still names its simulator slot “spectre” and may print `ADE-3070` or “Cannot start up spectre,” even when the ngspice run succeeds and its PSF data opens. The decisive evidence is the bridge log, ngspice logs, and actual Cadence-readable traces. A saved ADE setup such as `step1_final` under the DUT does not establish valid testbench results. No script can turn this local adapter into licensed Spectre.

The earlier paper numbers (13.19 µW, 16.71 ps, 0.221 fJ, and 0–980 mV) are comparison targets. Do not substitute them for measured values. The paper's 10 pF load also differs from this project's 300 fF load.

## 1. Confirm the Virtuoso design first

Open `shivam/tb_mcml_charge_pump/schematic` from Library Manager. The supplied testbench was repaired and checked on 22 October 2026. Its current configuration is:

| Item | Current setting |
|---|---|
| DUT | `DUT0`, eight pins, output wire `Vop` |
| Supply and bias | `V_VDD = 1.0 V`, `V_BIAS = 0.45 V` |
| UP controls | `V_UP`: 0→1 V; `V_UP_B`: 1→0 V; 100 ps period, 25 ps width, 5 ps rise/fall, 0 delay |
| DN controls in charging mode | `V_DN = 0 V`, `V_DN_B = 1.0 V` (two `analogLib/vdc` sources) |
| Ground | One actual `analogLib/gnd` connected to the DUT and all sources |
| Load | DUT-internal `CL = 300 fF` only; no external output capacitor |
| Other DUT capacitor | Internal `Ci = 50 fF` between `n_top` and `n_bot` |

Choose **File → Check and Save**. Read the newest CIW message and fix any unconnected pin, floating wire, or missing master. The most recent checked testbench generated a Spectre-format netlist with 22 components, zero netlisting errors, and zero netlisting warnings. Its source is the OpenAccess cellview, not an old picture or hand-written deck. Evidence from the prior check is in `mcml_charge_pump_10ghz_project/cadence_work/stop_check_1_CIW.log` and `annotated_screenshots/stop_check_1_testbench.png` in that directory. Repeat Check and Save after any schematic change.

**STOP CHECK 1:** Confirm the table and a successful Check and Save before opening ADE or netlisting. In particular, the two DN sources are DC sources, not pulse sources.

## 2. Route A: genuine Spectre inside Virtuoso

Use this route on a lab workstation with a real Cadence Spectre executable and license. Open ADE **from the testbench schematic**. The existing `step1_final` state saved under `mcml_charge_pump` is attached to the DUT, not the testbench; it netlists no supply or control sources and is not a valid testbench run. Start or save an ADE state under `tb_mcml_charge_pump` instead.

### 2.1 Verify the solver before taking measurements

In ADE L choose **Setup → Simulator/Directory/Host** and select Spectre. Add the model file required by the lab PDK under **Setup → Model Libraries** and record its exact file, section, and corner. The local `cadence_work/gpdk045.scs` section `mc` is a simplified teaching model, not a complete characterized TT corner. Use 27 °C and 1.0 V unless the assignment specifies otherwise.

Set **Analyses → Choose → tran** with stop `237p` and maximum step `0.5p`. Save `Vop`, `UP`, `UP_b`, `DN`, `DN_b`, `Vdd`, and the positive-terminal current of `V_VDD`. Set `Vop` initial condition to 0.54 V for charging if needed; use one initial-condition method only. Press **Netlist and Run**. Inspect the actual `spectre.out`, the generated netlist, and the plotted time axis. The 237 ps request must end at 237 ps, and the VDD-source current must exist. If the plot ends at a fixed 10 ns or the current is absent, the local synthetic wrapper is active; stop and move to Route B or the lab machine.

A genuine Spectre run should identify its version and licensed solver in `spectre.out`, honor the requested stop time and model deck, and produce a current trace. Once that passes, change only the stop time to `10n`, retain maximum step `0.5p`, and run charging mode. Save the result as `charge_tran`.

### 2.2 Discharging run in the same testbench

Make a copy of the transient testbench or save the charging result before changing controls. Change UP and UP_b to constant `0 V` and `1 V`; change DN and DN_b to complementary pulses with the same `0/1 V`, `100p` period, `25p` width, `5p` rise/fall, and `0` delay. Use a 0.62 V `Vop` initial condition if needed. Check and Save. Reopen ADE from that testbench, run `10n`, and save as `discharge_tran`. Verify DN pulses and UP stays low. Do not attach `Vop` to a voltage source during transient tests.

### 2.3 ADE/ViVA measurements

Use the same definitions for both routes:

| Metric | Extraction |
|---|---|
| UP/DN delay | For each active input rising edge, pulses 11–20, find its 0.5 V crossing. Sample `Vop` 10 ps before and 40 ps after that edge; find the first output crossing of the midpoint of those two local samples in the 0–40 ps window. Average ten delays per direction. Report the larger directional mean. Verify those two samples represent the local levels. |
| Power | `P(t) = -V(Vdd) × I(V_VDD)` with current referenced from the positive VDD terminal into the source. Average from 1 ns through 10 ns separately for charge and discharge. Positive is power delivered by VDD to the core. Control-source power is excluded. |
| PDP | Use the power from the direction that set the larger mean delay: `PDP[fJ] = P[µW] × delay[ps] / 1000`. |
| Settled output swing | After the waveform settles, take five `Vop` samples just before five final input edges in each mode. Upper mean minus lower mean; report the stop time and the first-to-last spread. This is the paper-style dynamic voltage swing. |
| Usable current-compliance dynamic range | In a separate DC testbench, sweep a forcing source on `Vop` from 0 to 1 V in 0.01 V increments. For charge set UP/UP_b/DN/DN_b = 1/0/0/1; for discharge set 0/1/1/0. Define positive charge current as `I(V_FORCE)` and positive discharge magnitude as `-I(V_FORCE)`. At each voltage require charge and discharge currents each within 10% of their respective 0.5 V reference currents **and** `200 × abs(I_UP-I_DN)/(I_UP+I_DN) ≤ 10%`. Report the contiguous passing interval containing 0.5 V. If 0.5 V fails, report **no valid interval under this criterion**. |

For each delay, a Calculator expression sequence is `t_in=cross(IN,0.5,n,"rising")`, `V_before=value(OUT,t_in-10p)`, `V_after=value(OUT,t_in+40p)`, `V_mid=(V_before+V_after)/2`, then find the single rising (`UP`) or falling (`DN`) crossing of `clip(OUT,t_in,t_in+40p)` at `V_mid`; subtract `t_in`. The 40 ps sample and search window should be checked on the trace. Use Calculator `clip`, `average`, `value`, `cross`, and arithmetic to obtain the table values in ADE. The archived detailed ADE click-by-click instructions are at `mcml_charge_pump_10ghz_project/cadence_work/legacy_guide_before_ngspice.md` but its initial testbench status and pulse timing are outdated; use the settings above.

For the DC run, copy the testbench as `tb_mcml_charge_pump_dc`. Replace the four controls with DC sources, add `V_FORCE` from `Vop` to the existing real ground, Check and Save, then use ADE **dc → Component Parameter** to sweep the DC voltage of `V_FORCE`. Save charge and discharge DC runs separately. Plot their currents and the three 10% error curves in ViVA. A short output spike is not a usable current-compliance range.

## 3. Route B: current machine, Virtuoso netlist + ngspice

This route has been run on the current workstation. It uses the **current Virtuoso-generated testbench netlist**, maps its 13 gpdk045 transistor instances to FreePDK45 nominal-VTG HSPICE/BSIM4 models, preserves their netlisted geometry fields, and retains the DUT's `CL=300f` and `Ci=50f`. The model substitution is material: these are illustrative results, not GPDK45/Spectre or a foundry signoff result. The converter checks the exact DUT pin order, 13 MOSFETs, two capacitors, ground, six source settings, and netlist freshness. It stops if the topology or source settings change unexpectedly.

### 3.0 Presentation run: ADE Netlist and Run is connected to ngspice

The adapter and its host service are installed and the service is enabled for the user session. It is limited to `shivam/tb_mcml_charge_pump/schematic`; another cellview fails clearly instead of producing fabricated waveforms. From a terminal you can check readiness with:

**After a reboot:** log in to the graphical desktop, then use the project launcher. The Docker daemon and the bridge user service are enabled, but the Virtuoso Docker container is started on demand and has no restart policy. The launcher checks the installed model files, Cadence adapter, ngspice, and Docker image, and starts the user bridge service if needed. `--check` does not open Virtuoso.

```sh
cd /home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project
./launch_virtuoso.sh --check
./launch_virtuoso.sh
```

Wait for the Virtuoso CIW, open `shivam/tb_mcml_charge_pump/schematic`, load the testbench's ADE L `step1_final`, and press **Netlist and Run**. The service starts at user login (`systemctl --user is-enabled mcml-ade-bridge.service` currently says `enabled`); `loginctl` reports `Linger=no`, so it is not expected to run before login. The container uses `--rm`, so it disappears at reboot and must be launched again. The project files, saved ADE state, model files, and screenshots remain on disk. Keep the project at its present absolute path: the Cadence library map and bridge scripts contain `/home/shivam/Projects/VLSI/...` paths.

Keep one Cadence container running at a time. The launcher refuses to start a second one because the bridge needs an unambiguous container for ADE results. If Virtuoso is already open, use that session.

**Fresh-run check:** confirm the service is `active`, the netlist and `spectre.out` timestamps advance, and the latest `spectre.out` names ngspice 45.2 and the checked netlist. Re-evaluate one Calculator field with its explicit `?resultsDir` path. A green ADE status or old ViVA window alone does not prove a new run succeeded. The PDF screenshots in Section 4 are fixed evidence from 22 October 2026; they do not update after a reboot or new simulation.

```sh
systemctl --user is-active mcml-ade-bridge.service
/home/shivam/.local/bin/spectre -v
```

The responses should be `active` and `ADE ngspice bridge 1.0 (NOT Cadence Spectre)`. If the service is inactive, run `systemctl --user start mcml-ade-bridge.service`. Keep the Cadence container running. The service runs ngspice on the host because the container has Python 2 and no ngspice; the adapter passes only the checked Virtuoso testbench netlist across a local Unix socket. The `spectre` pathname is used solely because ADE L calls that pathname.

**Prove the bridge with a fresh ADE run:** after **Netlist and Run** finishes, inspect the following from a host terminal. The `spectre` name in ADE is the adapter's entry point; the log and ngspice run log establish which numerical solver actually ran.

```sh
systemctl --user is-active mcml-ade-bridge.service
readlink -f /home/shivam/.local/bin/spectre
/home/shivam/.local/bin/spectre -v
stat -c '%y %n' /home/shivam/simulation/tb_mcml_charge_pump/spectre/schematic/psf/{spectre.out,tran.tran}
head -n 8 /home/shivam/simulation/tb_mcml_charge_pump/spectre/schematic/psf/spectre.out
tail -n 5 /home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/charge_10ns.log
```

The service should say `active`; the link should resolve to `cadence_work/ade_ngspice_spectre_bridge.py`; `-v` should say **NOT Cadence Spectre**. The two PSF file timestamps should advance with the new run. The ADE log should name the current Virtuoso netlist, its SHA-256, **ngspice-45.2**, the run mode, and the measured values. The ngspice log should end with `No. of Data Rows` and `ngspice-45.2 done`. In ViVA, the `Vop`/control traces and result popup should correspond to that run. An `ADE-3070` warning does not establish success or failure by itself; use the fresh files and solver logs above.

For the live demo:

1. Launch or restart Virtuoso from `cadence_work` so its `.cdsinit` arms the result-popup timer. If Virtuoso is already open, enter this once in CIW: `load("/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/cadence_work/ade_ngspice_ui.il")`.
2. In Library Manager open **`shivam/tb_mcml_charge_pump/schematic`**, not `shivam/mcml_charge_pump/schematic`. Confirm `V_BIAS=0.45 V`, the M5 tail-gate connection, the supplies, controls, ground, and one internal `CL`. Choose **File → Check and Save**.
3. From that **testbench** choose **Launch → ADE L**. A corrected `step1_final` ADE state has been placed under **`tb_mcml_charge_pump`** with `tran` stop `10n`, maximum step `0.5p`, and the testbench design identity. Load that state if convenient, then visually confirm those settings and temperature 27 °C. Keep the charging controls as shown in Section 1. The older `step1_final` under the DUT remains the wrong state for this experiment.
4. Press **Netlist and Run** and allow about 20–30 seconds. The adapter numerically runs 10 ns charging and discharging, 0–1 V DC charge/discharge sweeps, and longer settling runs. It writes the requested ADE transient and full charging and discharging waveforms to binary Cadence PSF. A popup and two four-strip ViVA windows appear when the run finishes, one for charging and one for discharging. The trace labels use signal names such as `UP`, `DN`, and `Vop (charge)`; the popup, log, and PSF metadata identify ngspice / FreePDK45 as the source. The native PSF display was verified in an isolated Virtuoso session; the screenshot is `cadence_work/ade_ngspice_popup_verified.png`.
5. If ADE displays `ADE-3070`, inspect `/home/shivam/simulation/tb_mcml_charge_pump/spectre/schematic/psf/spectre.out`: a successful bridge run explicitly says `ADE NGSPICE BRIDGE — NOT CADENCE SPECTRE` and lists the measured metrics. The PSF directory was independently opened by Cadence OCEAN, which read 21,205 transient points, `Vbias=0.45 V`, and VDD current. The popup/ViVA plot is the reliable presentation path here; the Spectre-specific Calculator shortcuts may warn that `ngspice-bridge` is unregistered.

The existing open ADE window titled `shivam mcml_charge_pump schematic` is on the **DUT**, so close it and launch from the testbench. Its `step1_final` state cannot drive the DUT pins. The schematic check and the independent ngspice transient both confirm `V_BIAS (Vbias 0) dc=0.45`; `DUT0` passes `Vbias` into the DUT; transistor `M5` has its gate on `Vbias` and is `W=480n`, `L=45n`. The bridge rejects a missing or changed connection/value.

The following terminal steps are a reproducible fallback if the ADE UI is unavailable. They use the same `run.py` computation as the ADE bridge.

### 3.1 Regenerate the netlist from Virtuoso

Keep the Cadence container running, then find its ID with `docker ps`. From a terminal, replace `<container-id>` below with the running Cadence container ID:

```sh
cd /home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/cadence_work
docker exec -w /home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/cadence_work <container-id> /home/shivam/cadence/env.sh ocean -nographE -restore test_netlist_tb.ocn -log /tmp/netlist_tb.log
```

Read the OCEAN output. `createNetlist` must finish without a netlisting error or warning. The resulting file is `/home/shivam/simulation/tb_mcml_charge_pump/spectre/schematic/netlist/input.scs`; inspect its timestamp after each schematic edit. This step is **Cadence netlisting**, not simulation. If the container is unavailable, launch it using the project's existing Cadence environment, open/check the testbench, and rerun the command. The `test_netlist_tb.ocn` file only netlists the named cell; it does not fabricate simulation results.

### 3.2 Run measured transient and DC analyses

On the host, with `ngspice`, Python 3, `numpy`, and `matplotlib` installed:

```sh
cd /home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow
python3 run.py
```

The program writes four 10 ns and DC sweep decks, plus longer transient runs to check settled swing, under `results/`. It rejects a stale netlist, missing model, unexpected topology or source, ngspice error, or insufficient waveform data. It does not call the fake local `spectre` executable. Check `results/charge_10ns.log`, `results/discharge_10ns.log`, `results/charge_dc.log`, and `results/discharge_dc.log` for `No. of Data Rows` and the `ngspice-45.2 done` line. Do not use any log that contains a solver error or an old result after changing the schematic.

Read the machine-readable results and plot:

```sh
cat results/metrics.json
```

Open `results/verified_results.png` for a charging/discharging transient and power plot plus the DC current plot. The full numeric traces are `results/*.dat`; `results/dc_compliance.csv` contains every swept voltage, the two currents, three error percentages, and its pass flag. `metrics.json` stores the SHA-256 hashes of the Virtuoso netlist and both model files for provenance.

### 3.3 Show the measured PSF waveforms in Virtuoso

After an ADE bridge run, enter this in the **Virtuoso CIW** to reopen the ViVA plots:

```skill
load("/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/cadence_work/show_native_psf_results.il")
```

Enter only the `load(...)` line in the **CIW input field**, not in a Linux `zsh` terminal. It displays waveforms; it does not print the delay, power, or swing measurements. Two `OCN-6152` warnings about the unregistered `ngspice-bridge` simulator are expected here: the viewer uses OCEAN `getData`, which the warning says still works. The line `ViVA plotted separate charge and discharge PSF windows...` followed by `t` means the viewer script completed. Do not copy those CIW output lines back into a shell: quotes in the output can produce `zsh: unmatched "`.

To obtain the numerical results after the ADE run, open **ADE L → Tools → Calculator**, select **Options → Algebraic Mode**, and evaluate the expressions in [`ADE_L_RESULT_COMMANDS.txt`](ADE_L_RESULT_COMMANDS.txt) one at a time. The file includes charge/discharge delay and power plus the settled high, low, and combined output swing. These Calculator expressions read the saved result directories directly; they do not use `load(...)`.

The viewer reads both binary PSF result sets at full transient resolution. One ViVA window shows charging `UP`, `UP_b`, `Vop`, and VDD current; a second shows discharging `DN`, `DN_b`, `Vop`, and VDD current. `Vop (charge)` and `Vop (discharge)` come from separate numerical runs. The result popup reports delay, power, PDP, swing, and dynamic-range validity. Label any screenshot **“Virtuoso ViVA, ngspice 45.2 / FreePDK45 VTG results from Virtuoso netlist”**. The traces are Cadence PSF displays of ngspice data, not Cadence Spectre simulation results. A terminal-only `python3 run.py` run does not create the PSF viewer files; use ADE **Netlist and Run** once to generate them.

### 3.4 Results from the current checked netlist (22 October 2026)

| Quantity | Measured result | Conditions |
|---|---:|---|
| Mean UP delay | 13.811 ps | pulses 11–20, local 50% method |
| Mean DN delay | 15.447 ps | pulses 11–20, local 50% method |
| Reported delay | 15.447 ps | larger directional mean |
| UP-mode VDD power | 22.528 µW | 1–10 ns |
| DN-mode VDD power | 16.097 µW | 1–10 ns |
| PDP | 0.24865 fJ | DN power × DN delay |
| Settled `Vop` high / low | 0.992875 V / −0.000648 V | five quiet samples near 80 ns; each set varies <10 µV |
| Settled output swing | 0.993524 V | high minus low; paper-style dynamic voltage swing |
| 10% current-compliance dynamic range | **No valid interval at 0.5 V** | charge 61.98 µA; discharge 231.31 µA; mismatch 115.47% |

These values use 1.0 V VDD, 0.45 V bias, 27 °C, 100 ps input period, 300 fF internal load, and FreePDK45 nominal VTG models. The DC mismatch is a real measured failure of the stated 10% criterion. Do not present the 0.994 V output swing as if it were a passing current-compliance range. The tiny negative settled low voltage is retained as simulated; do not silently clamp it to zero. Run `python3 run.py` again after any changed Virtuoso netlist or model, and replace this table with the new measured values.

### 3.5 Calculate and present the paper delay comparison

The [research paper](mcml_charge_pump_10ghz_project/A_high-speed_MCML_charge_pump_design_at_10_GHz_fre-1.pdf), **Table 3, proposed charge pump, TT corner**, gives **16.71 ps** at 1.0 V and 27 °C. Table 2 specifies **10 pF** capacitance. The paper calls this its minimum propagation delay but does not give an input/output threshold or pulse-averaging rule sufficient to reproduce that number exactly. Use it as a published reference, with the differing conditions stated beside the result.

For this project, `run.py` measures each active input rising edge at **0.5 V** on pulses **11–20**. It samples `Vop` at `t_in − 10 ps` and `t_in + 40 ps`, finds the midpoint of those local levels, then finds the first `Vop` crossing of that midpoint within 40 ps after the input edge. Linear interpolation between the saved transient samples gives the crossing time. For discharge, the output crossing is falling. Each edge delay is `t_out − t_in`; the ten edge delays are averaged separately for charging and discharging. The larger of the two means is the reported design delay. These rules are implemented in `mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/run.py` and each edge's times and levels are saved in `results/metrics.json`.

One visible example from the discharging ViVA window is pulse 16: the `DN` 0.5 V rising crossing is **1.502500 ns**, and the local midpoint falling crossing of `Vop` is **1.517960 ns**. ViVA time markers at those two points show approximately **15.460 ps**. The ten discharging delays average **15.447 ps**; the ten charging delays average **13.811 ps**. Use the **15.447 ps** discharging mean for the comparison. A single marker pair demonstrates the method, while `metrics.json` provides the ten-edge average.

| Comparison | Calculation | Result |
|---|---|---:|
| Published TT delay | Paper Table 3 | 16.710 ps |
| Measured worst-direction mean | `max(13.811, 15.447)` | 15.447 ps |
| Signed difference | `15.447 − 16.710` | −1.263 ps |
| Absolute percent difference | `100 × abs(15.447 − 16.710) / 16.710` | **7.56%** |
| Illustrative ±10% band around paper value | `16.710 × [0.90, 1.10]` | 15.039–18.381 ps |

The measured delay falls inside that **illustrative ±10% comparison band**. This band is a presentation criterion, **not** a statistical confidence interval or a tolerance stated by the paper. Do not claim a matched-conditions replication: the paper used 10 pF and its own 45 nm process models, while this checked DUT has 300 fF and the available ngspice run substitutes FreePDK45 nominal VTG. Its delay extraction rule is also unavailable. Say: **“Our measured worst-direction delay is 15.447 ps, 7.56% below the paper's 16.71 ps TT figure under different load and models.”** The ADE result popup now calculates the same percentage automatically from the current run.

#### ADE L Calculator demo: exact order and fields

1. Open ADE L **from `shivam/tb_mcml_charge_pump/schematic`** and load the testbench's **`step1_final`** state. Confirm transient stop `10n`, maximum step `0.5p`, temperature 27 °C, and charging controls. Loading the state does not produce waveforms.
2. Click **Netlist and Run** and wait for the measured-result popup and the separate charge/discharge ViVA windows. The ADE-requested PSF contains the charging run.
3. In that ADE L window choose **Tools → Calculator**. Select **Options → Algebraic Mode** if the buffer is in RPN mode. Clear the buffer before each expression below, paste the whole line, and click **Evaluate**. These are Calculator field expressions; no custom function or CIW command is needed.
4. **Verify result access first.** The working expression below supplies `?resultsDir` explicitly. This was confirmed in the live ADE L Calculator. The shorter `getData("UP" ?result 'tran)` returned `nil` in this setup and caused `cross`/`times` errors.

```skill
cross(getData("UP" ?result 'tran ?resultsDir "/home/shivam/simulation/tb_mcml_charge_pump/spectre/schematic/psf") 0.5 16 "rising")*1e9
```

Expected result: **1.5025 ns**. If it returns `nil`, check that **Netlist and Run** finished and `/home/shivam/simulation/tb_mcml_charge_pump/spectre/schematic/psf/tran.tran` exists. Next, **show one charging edge** with this expression (picoseconds; expected **13.8270 ps**):

```skill
let((d a b ti vlo vhi) d="/home/shivam/simulation/tb_mcml_charge_pump/spectre/schematic/psf" a=getData("UP" ?result 'tran ?resultsDir d) b=getData("Vop" ?result 'tran ?resultsDir d) ti=cross(a 0.5 16 "rising") vlo=value(b ti-10e-12) vhi=value(b ti+40e-12) (cross(clip(b ti ti+40e-12) (vlo+vhi)/2 1 "rising")-ti)*1e12)
```

5. **Show the ten-pulse charging mean** with this expression (picoseconds; expected **13.8114 ps**):

```skill
let((d a b sum n ti vlo vhi) d="/home/shivam/simulation/tb_mcml_charge_pump/spectre/schematic/psf" a=getData("UP" ?result 'tran ?resultsDir d) b=getData("Vop" ?result 'tran ?resultsDir d) sum=0.0 for(n 11 20 ti=cross(a 0.5 n "rising") vlo=value(b ti-10e-12) vhi=value(b ti+40e-12) sum=sum+cross(clip(b ti ti+40e-12) (vlo+vhi)/2 1 "rising")-ti) sum/10*1e12)
```

6. **Show discharging delay using the separate discharge PSF.** The charging ADE PSF keeps `DN=0 V`; it cannot produce a `DN` edge delay. The bridge generated `viva_psf_discharge` from the same checked Virtuoso netlist with the control modes swapped. The following expressions give its result directory explicitly, so you can paste them into the *same* Calculator window. If the professor asks how the single edge was measured, evaluate pulse 16 first:

**Pulse 16 discharge delay, in ps** (expected **15.4599**):

```skill
let((d a b t0 vlo vhi) d="/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/viva_psf_discharge" a=getData("DN" ?result 'tran ?resultsDir d) b=getData("Vop" ?result 'tran ?resultsDir d) t0=cross(a 0.5 16 "rising") vlo=value(b t0-10e-12) vhi=value(b t0+40e-12) (cross(clip(b t0 t0+40e-12) (vlo+vhi)/2 1 "falling")-t0)*1e12)
```

Now evaluate the **ten-pulse discharging mean** (picoseconds; expected **15.4473 ps**):

```skill
let((d a b sum n ti vlo vhi) d="/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/viva_psf_discharge" a=getData("DN" ?result 'tran ?resultsDir d) b=getData("Vop" ?result 'tran ?resultsDir d) sum=0.0 for(n 11 20 ti=cross(a 0.5 n "rising") vlo=value(b ti-10e-12) vhi=value(b ti+40e-12) sum=sum+cross(clip(b ti ti+40e-12) (vlo+vhi)/2 1 "falling")-ti) sum/10*1e12)
```

7. Compare the two means. Discharging is larger, so it is the reported delay. **Evaluate the paper percentage difference** directly from the discharge waveform (expected **7.5564%**):

```skill
let((d a b sum n ti vlo vhi measured) d="/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/viva_psf_discharge" a=getData("DN" ?result 'tran ?resultsDir d) b=getData("Vop" ?result 'tran ?resultsDir d) sum=0.0 for(n 11 20 ti=cross(a 0.5 n "rising") vlo=value(b ti-10e-12) vhi=value(b ti+40e-12) sum=sum+cross(clip(b ti ti+40e-12) (vlo+vhi)/2 1 "falling")-ti) measured=sum/10*1e12 100*abs(measured-16.71)/16.71)
```

The percentage is **7.56%**. The expressions use built-in Cadence `getData`, `cross`, `value`, and `clip`; `let` only names intermediate values inside the pasted field and does not define a function. The bridge may print `OCN-6152` because its simulator name is unregistered, while these OCEAN data operations still work. The input-crossing check was confirmed in ADE L Calculator, and the delay/percentage fields were evaluated against the current binary PSF results in Cadence OCEAN, returning **13.8270**, **13.8114**, **15.4599**, **15.4473 ps**, and **7.5564%**. In the discharge ViVA window, put time markers on `DN` at 1.502500 ns and `Vop` at 1.517960 ns beside the Calculator result. The ten-edge mean is the number to compare with the paper.

### 3.6 Calculate the paper's output voltage swing in ADE L Calculator

The paper's reported **0–0.98 V** value is its *output voltage swing*. Measure the settled high and low `Vop` levels, then subtract: `swing = V_HIGH − V_LOW`. The ADE-requested 10 ns PSF contains only the charging run and is still settling. The bridge saves the longer charge and discharge runs separately as `viva_psf_swing_charge` and `viva_psf_swing_discharge`. This checked netlist reaches the settling criterion at **80 ns**.

If your testbench schematic and ADE L `step1_final` are already open after **Netlist and Run**, keep those windows open. The Calculator can read the two 80 ns result directories below from that same ADE session; you do not need to change the testbench controls or run ADE again. Verify that both `viva_psf_swing_charge/tran.tran` and `viva_psf_swing_discharge/tran.tran` exist before evaluating. A `nil` result usually means the bridge run did not finish, a result directory is missing, or the pasted path is wrong. Do not calculate the settled swing from the visible 10 ns charge trace, which has not settled.

**Starting with `tb_mcml_charge_pump` already open after Netlist and Run:**

1. In the same ADE L window choose **Tools → Calculator**, then **Options → Algebraic Mode** if needed.
2. Clear the Calculator buffer, paste the **charging high** field below, and click **Evaluate**. Record the displayed voltage.
3. Clear the buffer, paste the **discharging low** field, and click **Evaluate**. Record that voltage.
4. Clear the buffer and evaluate `0.9928752014-(-0.0006483985)`. This gives the settled output swing, **0.9935235999 V = 993.524 mV**. If the displayed high/low values change after a new run, substitute those new values in the subtraction.

The two fields use explicit `?resultsDir` paths because this ADE bridge does not reliably set the Calculator's current waveform context. They average `Vop` at five quiet times just before the last five control edges: 79.4975, 79.5975, 79.6975, 79.7975, and 79.8975 ns. `let` only names a local value within a pasted expression; it does not define a function.

Charging high level, expected **0.9928752014 V**:

```skill
let((d v) d="/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/viva_psf_swing_charge" v=getData("Vop" ?result 'tran ?resultsDir d) (value(v 79.4975e-9)+value(v 79.5975e-9)+value(v 79.6975e-9)+value(v 79.7975e-9)+value(v 79.8975e-9))/5)
```

Discharging low level, expected **−0.0006483985 V**:

```skill
let((d v) d="/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/viva_psf_swing_discharge" v=getData("Vop" ?result 'tran ?resultsDir d) (value(v 79.4975e-9)+value(v 79.5975e-9)+value(v 79.6975e-9)+value(v 79.7975e-9)+value(v 79.8975e-9))/5)
```

The two fields were checked against the binary PSFs in Cadence OCEAN and return **0.9928752014 V** and **−0.0006483985 V**. For a single field that computes the subtraction directly from both full-precision waveforms, use this optional expression (expected **0.9935235999 V**):

```skill
let((cd dd cv dv cu du high low n) cd="/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/viva_psf_swing_charge" dd="/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/viva_psf_swing_discharge" cv=getData("Vop" ?result 'tran ?resultsDir cd) dv=getData("Vop" ?result 'tran ?resultsDir dd) cu=getData("UP" ?result 'tran ?resultsDir cd) du=getData("DN" ?result 'tran ?resultsDir dd) high=0.0 low=0.0 for(n 796 800 high=high+value(cv cross(cu 0.5 n "rising")-5e-12) low=low+value(dv cross(du 0.5 n "rising")-5e-12)) (high-low)/5)
```

The measured swing is **99.35% of the 1.0 V supply** and **1.38% above the paper's 0.98 V swing**. The negative low level is the numerical result and is retained in the subtraction. These field expressions were evaluated on the binary PSF waveforms in Cadence OCEAN; the ADE L Calculator has not yet been checked interactively for these longer result files. If a future run settles at a different stop time, use its last five input edges instead of fixed pulse numbers 796–800. For a presentation, show the high result, low result, and their subtraction as three Calculator evaluations alongside the two separate ViVA traces. Identify the underlying numerical solver and model set as ngspice 45.2 and FreePDK45 nominal VTG.

### 3.7 Check current-compliance dynamic range

**This is a separate DC measurement.** The paper-style **993.524 mV output swing** above does not establish a usable charge/discharge current range. The existing transient `step1_final` state does not contain a `Vop` forcing source or a DC sweep, so its Calculator cannot derive this range from the 10 ns waveform. The bridge already ran both DC modes and saved the sweep in `mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results/dc_compliance.csv` and the summary in `results/metrics.json`.

Starting from the open ADE session, inspect the CSV column headings: `vop_v`, `i_charge_a`, `i_discharge_a`, `charge_error_pct`, `discharge_error_pct`, `mismatch_pct`, and `passes`. At the **0.5 V** reference point the charge and discharge magnitudes are **61.976 µA** and **231.310 µA**. The mismatch is **115.47%**, using `200*abs(I_charge-I_discharge)/(I_charge+I_discharge)`. Because this already exceeds the chosen 10% limit at the reference point, the contiguous passing interval containing 0.5 V does not exist: report **“No valid current-compliance dynamic range under the 10% criterion.”** A 0 V span or a 993.524 mV span would misstate this test.

For a wholly interactive Cadence DC demonstration, use the separate `tb_mcml_charge_pump_dc` procedure in Section 2.3 on a machine with a licensed solver. Save charge and discharge DC current results, then plot the charge error, discharge error, and mismatch against `Vop`. The present bridge exposes transient PSF data to the ADE Calculator, but it does **not** provide a DC PSF result set for Calculator `getData`; do not paste a fabricated DC Calculator expression into this ADE state. The current-machine DC evidence is the actual ngspice sweep CSV and the current-versus-voltage panel in `results/verified_results.png`, with that provenance stated beside the figure.

## 4. Evidence to show the professor

For a strict **Cadence Spectre simulation** assessment, a licensed Spectre machine is still required. Keep the testbench schematic, CIW Check and Save message, ADE analysis setup, solver log, ViVA waveforms, and DC error curves together. The current machine can launch the numerical run from ADE and show the Virtuoso schematic, Cadence-generated netlist, Cadence-readable transient result, result popup, and measured waveforms in ViVA, but its solver is ngspice with substituted models. State that distinction on every result sheet and spoken explanation.

For screenshots, capture the actual testbench schematic, the ADE `step1_final` analysis setup, the separate charging and discharging ViVA windows, and each Calculator evaluation after it returns a value. Keep the full application title and evaluated number visible. A Calculator field pasted into the window is not evidence of a result until **Evaluate** has completed. For power, capture the VDD-current trace and its 1–10 ns average for each mode. For dynamic range, capture the two settled `Vop` levels and their subtraction; show the separate DC compliance plot and 0.5 V CSV row when discussing current compliance. Put simulator/model provenance in the PDF caption even if a particular application window does not display it. Do not use the older generated `simulation_screenshots` artwork as proof of a Virtuoso run.

The captured evidence set is in [`mcml_charge_pump_10ghz_project/presentation_evidence_2026-10-22/`](mcml_charge_pump_10ghz_project/presentation_evidence_2026-10-22/README.md). Its 17-page [`Virtuoso_ADE_Calculator_Evidence.pdf`](mcml_charge_pump_10ghz_project/presentation_evidence_2026-10-22/Virtuoso_ADE_Calculator_Evidence.pdf) contains 16 actual application-window screenshots: DUT and testbench schematics, the loaded ADE state, separate charging/discharging ViVA *views*, and successful Calculator evaluations for delay, power, settled output swing, and 0.5 V DC current mismatch. The ViVA views are separate tabs in the same ViVA application window, captured one at a time. The DC Calculator page computes the mismatch from the measured `dc_compliance.csv` row; it is not a DC PSF evaluation. The PDF identifies the ngspice/FreePDK45 numerical provenance on every page.

For either route, the result sheet should state the model file/corner, temperature, supply/bias, load, clock period, transient stop and maximum step, initial condition, delay rule, power window and sign, PDP pairing, swing settling test, and the DC dynamic-range tolerance. If a required solver or model is absent, report that blocker and the measured fallback provenance rather than claiming an ADE/Spectre result.
