# Cadence ADE L Guide: Power, Delay, PDP, and Dynamic Range

## 10 GHz MCML charge pump in 45 nm CMOS

This is a **from-the-GUI, no-script measurement procedure**. Configure the
schematic and ADE L, press **Run**, and use the ADE L/ViVA Calculator on the
fresh waveforms for delay, power, PDP, output swing, and dynamic range. Paper
and pen arithmetic is **not required**. Do not run Python, custom SKILL,
OCEAN, shell simulation, a saved ADE state, or a pre-generated waveform.

This guide uses these supplied cells:

- DUT: `shivam / mcml_charge_pump / schematic`
- Testbench: `shivam / tb_mcml_charge_pump / schematic`
- Required simulator: a genuine Cadence Spectre solver selected inside ADE
- Supplied local baseline: model section `mc`, 27 °C, `VDD = 1.0 V`
- Clock: 10 GHz, so `T = 1/f = 100 ps`

Do **not** automatically rename model section `mc` as “TT.” A section name is
only a label. You may write “TT” in the final report only if your professor or
the complete foundry model documentation explicitly says that this particular
`mc` section is the TT corner. Otherwise write exactly: **model section `mc`,
27 °C, VDD = 1.0 V**.

The paper's `13.19 uW`, `16.71 ps`, `0.221 fJ`, and `0-980 mV` are
**comparison targets, not values to copy into the results table**. Write down
what the new run actually produces.

---

## Start-to-end map: use the provided schematic

The DUT and its symbol are supplied. The current testbench contains the
`DUT0` symbol but no voltage sources or external load. You must wire the
testbench before opening ADE; you do not need to recreate the transistor
wiring inside the DUT. “End” means a completed result sheet with fresh
screenshots and Calculator results.

Follow these stages in order:

| Stage | What you do | Proof before continuing |
|---:|---|---|
| 1 | Open the provided DUT and testbench | Both cellviews open correctly |
| 2 | Build and check the testbench around `DUT0` | Supply, bias, control sources, ground, and output net are connected |
| 3 | Configure ADE manually from an empty session | No saved state or helper was loaded |
| 4 | Prove the simulator obeys ADE | A requested 237 ps run ends at 237 ps |
| 5 | Run charging mode | Fresh UP, Vop, and VDD-current waveforms exist |
| 6 | Run discharging mode | Fresh DN, Vop, and VDD-current waveforms exist |
| 7 | Calculate UP/DN delay in ADE L Calculator | Ten pulse results and both means are recorded |
| 8 | Calculate average power in ADE L Calculator | Window and sign convention are recorded |
| 9 | Calculate PDP in ADE L Calculator | Result is displayed in femtojoules |
| 10 | Derive settled output swing | Five upper and five lower samples are recorded |
| 11 | Calculate usable dynamic range in ADE L Calculator | DC current/error curves and explicit tolerance are recorded |
| 12 | Assemble evidence | Final table and four screenshots are complete |

Do not run any of these helpers: `make_mcml_cp.il`, `make_symbol.il`,
`make_tb.il`, `simulate_in_virtuoso.il`,
`simulate_discharging_virtuoso.il`, `load_state_now.il`, Python simulation
files, shell project runners, OCEAN files, saved ADE states, or pre-generated
waveforms.

At every stop check, stop if the described item is missing. Do not “continue
and see what happens”; later measurements cannot repair a bad setup.

---

## 0. Read this before measuring anything

### 0.1 What each reported quantity means

| Quantity | Definition used in this guide |
|---|---|
| Average power | Average power drawn from the 1.0 V supply during a stated time window |
| Propagation delay | Time from the 50% point of an active UP/DN input edge to the 50% point of that pulse's local output-voltage change |
| PDP | Measured average power multiplied by measured propagation delay |
| Output swing | Highest settled charging voltage minus lowest settled discharging voltage |
| Usable dynamic range | Output-voltage interval in which both charge and discharge currents meet a stated current-error criterion |

Do not call a waveform's global `ymax-ymin` the dynamic range. A narrow spike
is not a usable voltage. Also, the paper calls `0-980 mV` a swing-voltage
range; that is different from a current-compliance dynamic range. This guide
measures both and labels them correctly.

### 0.2 Important problems in the present project

The following facts were checked in the supplied Virtuoso/OpenAccess project.
This table distinguishes what is already present from what still has to be
corrected manually before taking measurements.

| Item | Verification result | What you must do |
|---|---|---|
| `shivam / mcml_charge_pump / schematic` | **Confirmed present** as a non-empty OpenAccess schematic | Open it read-only first and visually check the nets and values |
| `shivam / tb_mcml_charge_pump / schematic` | **Confirmed present:** the current cell contains `DUT0` only | Add the six sources and ground described below |
| ADE model section | **Confirmed:** the supplied saved state names section `mc` | Select `mc` manually; do not load the saved state |
| ADE temperature | **Confirmed:** the supplied saved state contains `27` °C | Enter `27` manually |
| Supply | **Missing from the current testbench:** `V_VDD` | Place a 1.0 V `analogLib/vdc` source |
| Clock period | **Missing from the current testbench:** the control pulse sources | Place the four `analogLib/vpulse` sources; use `period = 100 ps` for 10 GHz |
| Transient maximum step | **Not configured:** the supplied ADE state leaves `maxstep` blank | Enter `0.5 ps` manually |
| External load | **Absent from the current testbench:** the DUT has its own `CL = 300 fF` | Do not add an external `C_LOAD` |
| Real Spectre solver | **Not confirmed; local executable fails verification** | Use a licensed genuine Spectre installation and perform the 237 ps proof run |

The frequency conversion is:

```text
T = 100 ps = 100 x 10^-12 s
f = 1/T = 1/(100 x 10^-12) = 10 x 10^9 Hz = 10 GHz
```

1. **The current `spectre` executable is synthetic.** Both
   `/home/shivam/.local/bin/spectre` and
   `/home/shivam/cadence/IC617/bin/spectre` are Python waveform generators,
   not the Cadence numerical solver. They ignore important netlist settings,
   generate a fixed 10 ns waveform, and do not save VDD-source current.
   Therefore they cannot prove power, delay, or dynamic range.
2. **The testbench is incomplete.** Its current OpenAccess cell contains only
   `DUT0`; the `make_tb.il` generator describes sources and an external
   `C_LOAD`, but those instances are not in the supplied testbench cell. The
   DUT already contains `CL = 300 fF`, so do not add another load. If you are
   working from a different testbench version that has `C_LOAD`, remove it;
   two 300 fF capacitors would give 600 fF.
3. The paper's Table 2 states a 10 pF capacitance, while this project and its
   report use 300 fF. A result obtained with 300 fF must be reported as a
   **project result**, not claimed as an exact paper replication.
4. The local `gpdk045.scs` contains only short, simplified BSIM4 model
   declarations (`vth0`, `u0`, and `toxe`), not a complete characterized
   GPDK45 corner deck. It is sufficient for a classroom schematic exercise,
   but its output must be labelled **simplified-model simulation**. For a
   technology-accurate result, select the lab's complete PDK TT model deck and
   record its exact path and section in the result sheet.

These are stop conditions, not minor details. The rest of the guide is ready
to use after ADE is connected to a real licensed Spectre installation (or the
professor's lab machine).

---

## 1. Open and verify the provided project

You are keeping the supplied DUT and wiring a simulation testbench around its
symbol. Make these changes in `tb_mcml_charge_pump`, not in the DUT schematic.

### 1.1 Open the supplied DUT and testbench

1. Start the licensed Virtuoso installation in the normal lab-approved way.
2. Wait for the **CIW** window to finish opening.
3. In the CIW choose **Tools -> Library Manager**.
4. In the left column click library `shivam`.
5. In the middle column click cell `mcml_charge_pump`.
6. In the right column double-click view `schematic`.
7. Press `F` to fit the full DUT on screen.
8. Return to Library Manager.
9. Open `shivam / tb_mcml_charge_pump / schematic` in the same way.
10. Press `F` to fit the complete testbench.

The DUT schematic shows transistor-level pins. The **testbench** schematic
shows a `DUT0` block with pins `UP`, `UP_b`, `DN`, `DN_b`, `Vdd`, `Gnd`,
`Vbias`, and `Vop`. In the current supplied project, `DUT0` is the only
testbench instance. That is why there is no `V_UP` to select and press `Q` on
yet. Build the sources in Sections 1.4–1.6 on this testbench schematic.

If either cell or view is missing, stop: the provided project has not been
loaded correctly. Do not create a replacement under pressure because it will
not be the supplied design.

### 1.2 Confirm the one intended load capacitor

1. In the DUT window find the capacitor named `CL` connected from `Vop` to
   `Gnd`.
2. Click `CL` once so it is highlighted.
3. Press `Q` to open its properties.
4. Confirm the capacitance field reads `300f`.
5. Click **Cancel** so the value is not accidentally changed.

### 1.3 Keep only the DUT load

1. Open `shivam / tb_mcml_charge_pump / schematic` for editing.
2. Do not place a capacitor on `Vop`: the DUT already contains the intended
   300 fF load.
3. If your copy has an external `C_LOAD` from `Vop` to ground, delete it.
4. Write in the lab book: `Effective CL = 300 fF (internal DUT CL only)`.

If the professor specifically asks for the paper's 10 pF load, change the one
internal `CL` to 10 pF and rerun **all four measurements**. Never compare a
10 pF delay with a 300 fF power result.

### 1.4 Confirm a real ground exists

Press `I`, choose library `analogLib`, cell `gnd`, and place it in the
testbench. Connect `DUT0/Gnd` to it with a wire. The negative terminals of
the six sources below must reach this same grounded net. If your testbench
already has a ground symbol, use it and confirm the connection.

A wire merely named `Gnd` is not guaranteed to be simulator node 0. The real
`analogLib/gnd` symbol is required.

### 1.5 Place the supply and bias sources

In the **testbench** schematic, press `I` and place two `analogLib/vdc`
instances. Select each new instance, press `Q`, set its instance name and DC
voltage, then wire it as follows:

| Instance name | DC voltage | `PLUS` terminal | `MINUS` terminal |
|---|---:|---|---|
| `V_VDD` | `1.0 V` | `DUT0/Vdd` | Ground |
| `V_BIAS` | `0.45 V` | `DUT0/Vbias` | Ground |

Use actual wires from source terminals to the DUT pins and ground. Label the
positive wires `Vdd` and `Vbias` so the ADE waveforms have recognizable
names. Do not connect `Vdd` directly to `Vbias`.

### 1.6 Configure the charging stimulus

In the **testbench**, press `I` and place four `analogLib/vpulse` instances.
Select each new source and press `Q` to set its instance name and pulse
properties from the table. Wire each `PLUS` terminal to the matching DUT pin
and each `MINUS` terminal to the grounded net:

| Instance name | `PLUS` connects to | `MINUS` connects to |
|---|---|---|
| `V_UP` | `DUT0/UP` | Ground |
| `V_UP_B` | `DUT0/UP_b` | Ground |
| `V_DN` | `DUT0/DN` | Ground |
| `V_DN_B` | `DUT0/DN_b` | Ground |

Label the four positive wires `UP`, `UP_b`, `DN`, and `DN_b`. Check that
each wire is attached to its pin and that the four control nets stay
separate. The complementary UP sources share timing; the two DN sources are
held at fixed opposite levels for this charging run.

| Source | `v1` | `v2` | `td` | `tr` | `tf` | `pw` | `per` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `V_UP` | 0 | 1.0 | 50p | 5p | 5p | 25p | 100p |
| `V_UP_B` | 1.0 | 0 | 50p | 5p | 5p | 25p | 100p |
| `V_DN` | 0 | 0 | 0 | 1p | 1p | 25p | 100p |
| `V_DN_B` | 1.0 | 1.0 | 0 | 1p | 1p | 25p | 100p |

Extend a wire from `DUT0/Vop` and label it `Vop`. Leave this output free of
voltage sources; its voltage should be determined by the DUT and its internal
load. Set an initial condition of `0.54 V` on this **testbench `Vop` net** for
the charging test:

1. Select the `Vop` wire.
2. Use **Edit -> Properties -> Objects** (or press `Q`).
3. Set the net initial-condition property `ic` to `0.54`.
4. Check and Save.

If this Virtuoso release does not expose `ic` on a net, use ADE's
**Simulation -> Convergence Aids -> Initial Condition**, choose
**Select on Schematic**, click `Vop`, and enter `0.54 V`. Use only one of
these two methods.

The 50 ps input delay gives the DC operating point time to settle before the
first command edge. At 10 GHz, `per = 100p` because

```text
T = 1/f = 1/(10 x 10^9) = 100 x 10^-12 s = 100 ps.
```

### 1.7 Final testbench check

1. Choose **File -> Check and Save**.
2. Read the newest CIW message.
3. Fix any unconnected-pin, floating-wire, or missing-master error.
4. Confirm visually:
   - `V_VDD = 1.0 V`
   - `V_BIAS = 0.45 V`
   - Four control sources are connected: complementary `UP`/`UP_b` pulses,
     with `DN = 0 V` and `DN_b = 1.0 V` for charging
   - One real `analogLib/gnd` is connected
   - Only the DUT's internal `CL = 300 fF` is present
   - The output wire is named `Vop`

**STOP CHECK 1:** Do not open ADE until Check and Save succeeds and every item
above has been confirmed.

---

## 2. Configure ADE manually

Do not load `spectre_state1` or any saved state.

1. From the testbench schematic, select **Launch -> ADE L/Explorer**.
2. Under **Setup -> Simulator/Directory/Host**, select `spectre`.
3. Under **Setup -> Model Libraries**, add:
   `/home/shivam/Projects/VLSI/mcml_charge_pump_10ghz_project/cadence_work/gpdk045.scs`
   and select section `mc` if ADE provides a section field. This is the local
   simplified model. If the lab supplies a complete GPDK45 model, use its TT
   section instead and record that change; do not include both decks.
4. Set **temperature = 27 °C**.
5. Choose **Analyses -> Choose**, select `tran`, and first enter:
   - Stop time: `237p`
   - Accuracy: `conservative`
   - Maximum step: `0.5p`
   - Enable the initial condition (`ic`) option if the release requires it.
6. Select these voltage outputs on the schematic:
   `UP`, `UP_b`, `DN`, `DN_b`, `Vop`, `Vdd`, and `n_tail`.
7. Save the VDD-source terminal current:
   - Use **Outputs -> To Be Saved -> Select on Schematic**.
   - Click the **positive terminal** of `V_VDD`.
   - The selected result should identify `V_VDD/PLUS` or `V_VDD:p`.
   - If terminal selection is unavailable, use **Outputs -> Save All** and set
     device/terminal currents to `all`, then rerun.
8. Press the green **Netlist and Run** button for the 237 ps proof run.
9. When ViVA opens, plot `Vop` and look at the far-right x-axis value:
   - **Pass:** the plot ends at 237 ps.
   - **Fail:** the plot ends at 10 ns. The synthetic wrapper is active. Stop;
     do not report any measurement.
10. Confirm the `V_VDD` positive-terminal current can also be plotted. If it
    is missing, correct the save selection and rerun the 237 ps test.
11. Return to ADE, edit the transient analysis, change only Stop Time from
    `237p` to `10n`, and click **OK**.
12. Press **Netlist and Run** again. This is the real charging run.
13. Open the simulator output log and confirm:
   - Stop time is 10 ns.
   - Maximum step is 0.5 ps.
   - Temperature is 27 °C.
   - No model, convergence, or license error appears.
14. Plot `Vop`, `UP`, and the saved `V_VDD` terminal current.
15. Confirm all three traces cover 0 through 10 ns.

If `V_VDD` current is missing, power cannot be calculated. Fix the save
selection and rerun; do not substitute the paper's power.

**STOP CHECK 2:** A fresh 10 ns charging dataset must contain `UP`, `Vop`, and
the `V_VDD` positive-terminal current. The earlier 237 ps proof must have
passed.

---

## 3. Calculate propagation delay in ADE L Calculator

### 3.1 Why the old `0.5435 V` method was wrong

`0.5435 V` is only the midpoint of one assumed 7 mV step beginning at
`0.540 V`. The output step changes with cycle number, load, model, corner, and
temperature. A fixed threshold cannot be used for every run.

For each measured pulse, use that pulse's own starting and ending output
voltages to define its midpoint. The Calculator's `value`, `clip`, and `cross`
functions perform the sampling, threshold calculation, and interpolation.

### 3.2 Prepare the Calculator once per run

1. Plot the active input (`UP` or `DN`) and `Vop` from the **latest** transient
   result in ViVA. Open **Tools -> Calculator** from that result window.
2. Use the Calculator's **wave** button to select the plotted input and output.
   The examples below call their expressions `IN` and `OUT`; substitute the
   actual expressions inserted by your release (typically `VT("/UP")`,
   `VT("/DN")`, and `VT("/Vop")`). Do not type a guessed net path.
3. In the Calculator, `value(OUT time)` reads/interpolates the output voltage
   at that time. `cross(clip(IN start stop) 0.5 1 "rising")` finds the **first**
   rising 0.5 V crossing within that window. Choose the corresponding function
   buttons if your release constructs the expression through forms.
4. Use the expression area and **Evaluate** (`=` or `123`) for each result.
   Record Calculator values or add named expressions to ADE Outputs. All
   times in the expressions below are seconds (`1p` = 1 ps); display the final
   delays in ps. A missing crossing is an invalid measurement, not zero.

Cadence `cross` interpolates between saved samples, so no separate cursor or
paper interpolation is needed. Inspect the plotted pulse to rule out glitches
that could make `cross` select the wrong edge.

### 3.3 Charging delay (`t_UP`)

Do not use the startup pulse. Measure pulses 11 through 20. In the template
below, `IN` and `OUT` mean the wave expressions selected in Step 3.2, `n`
means the integer entered in the `cross` form, and names such as `t_in(n)`
label **evaluated results**; they are not literal Calculator variables. For
each `n`, evaluate one line, then insert its displayed scalar value into the
next line, or nest that line's expression. All subtraction and division are
done in the Calculator:

```text
t_in(n)     = cross(IN 0.5 n "rising")
V_before(n) = value(OUT t_in(n)-10p)
V_after(n)  = value(OUT t_in(n)+40p)
V_50(n)     = V_before(n) + (V_after(n)-V_before(n))/2
t_out(n)    = cross(clip(OUT t_in(n) (t_in(n)+40p)) V_50(n) 1 "rising")
t_UP(n)     = t_out(n)-t_in(n)
```

The `+40p` sample is a **starting choice** for a quiet post-pulse level.
Zoom into pulse 11 and verify that `Vop` is flat there and that the next UP
edge has not begun. If it is not flat, use a later quiet time before the next
UP edge and the same offset for all ten pulses; update both occurrences of
`+40p`. The `-10p` sample must be before the input rise and on a flat level.
`clip` limits the output search to this pulse so the next cycle cannot be
mistaken for its response. Check `t_out > t_in` and `t_out < t_in + 40p` (or
your chosen end offset).

To enter the pulse number, use the **Nth crossing** field of the *input*
`cross`: `11`, then `12`, through `20`. Set it to **rising** and **single
crossing**, not “all crossings.” The output `cross` always uses Nth=`1`
because it is clipped to one pulse. Evaluate and record `t_UP(11)` through
`t_UP(20)` in the Calculator/ADE Outputs. Enter their ten scalar results as
`(t_UP11 + t_UP12 + ... + t_UP20)/10` in the Calculator and **Evaluate** to
obtain `mean t_UP`. No hand calculation is required.

### 3.4 Discharging delay (`t_DN`)

Make a second manual run:

1. Return to the transient testbench schematic.
2. Select each pulse source, press `Q`, and enter this complete table:

| Source | `v1` | `v2` | `td` | `tr` | `tf` | `pw` | `per` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `V_UP` | 0 | 0 | 0 | 1p | 1p | 25p | 100p |
| `V_UP_B` | 1.0 | 1.0 | 0 | 1p | 1p | 25p | 100p |
| `V_DN` | 0 | 1.0 | 50p | 5p | 5p | 25p | 100p |
| `V_DN_B` | 1.0 | 0 | 50p | 5p | 5p | 25p | 100p |

3. Change the `Vop` initial condition from `0.54 V` to `0.62 V`. Do not leave
   both initial-condition entries active.
4. Check and Save.
5. In ADE confirm Stop Time=`10n`, Maximum Step=`0.5p`, and Temperature=`27`.
6. Press **Netlist and Run**. Do not display an old result without rerunning.
7. Plot `DN`, `Vop`, and the `V_VDD` positive-terminal current. Confirm `DN`
   pulses while `UP` stays at zero.
8. In the Calculator select `DN` as `IN` and the new `Vop` trace as `OUT`.
9. Repeat Section 3.3 for `n=11` through `20`, but use **falling** for the
   `t_out` crossing. Keep **rising** for the DN input crossing. The midpoint
   formula automatically handles `V_after < V_before`.
10. Evaluate and record the ten `t_DN(n)` results and their sum divided by
    `10` in the Calculator to obtain `mean t_DN`. Verify the post-pulse
    sample is flat and each output crossing belongs to the corresponding DN
    pulse.

### 3.5 Report one propagation-delay number

Report the worst direction unless the professor specifies another convention.
Use the Calculator's `max` function on the two **scalar means**, or select
the larger displayed mean:

```text
t_pd = max(mean t_UP, mean t_DN)
```

Also report both directional values. Example format:

```text
mean t_UP = ______ ps
mean t_DN = ______ ps
reported t_pd = max(______, ______) = ______ ps
```

If the paper's 16.71 ps is used for comparison, say that the paper does not
state its exact threshold/window extraction rule. A difference is not proof
of failure unless the same measurement definition, load, model, and stimulus
were used.

---

## 4. Calculate average power in ADE L Calculator

### 4.1 Sign convention

Spectre defines a terminal current as positive when it enters that terminal
and flows into the component. Therefore a voltage source delivering energy
normally has negative current at its positive terminal. The circuit's
positive drawn power is

```text
p_draw(t) = -v_VDD(t) x i_VDD_plus(t)
```

Verify the sign from the waveform. If `i_VDD_plus` is negative while the
circuit is active, keep the minus sign. If the saved current is already
positive out of the source, do not negate it.

### 4.2 Choose and write down the measurement window

Use `t1 = 1 ns` and `t2 = 10 ns`. This discards startup and contains exactly
90 complete 100 ps periods:

```text
t2 - t1 = 9 ns = 90 x 100 ps.
```

Use the same window for charging and discharging.

Power must be evaluated once for each mode:

1. Restore the complete charging source table from Section 1.6 and set
   `Vop ic=0.54 V`. Check and Save, then netlist and run. Calculate and record
   `P_UP` before changing the sources again.
2. Restore the complete discharging table from Section 3.4 and set
   `Vop ic=0.62 V`. Check and Save, then netlist and run. Calculate and record
   `P_DN`.
3. Verify both calculations use exactly `1n` through `10n`; otherwise they
   cannot be compared or averaged.

### 4.3 Use the ViVA Calculator interactively

Menu/button names differ slightly between ViVA releases, so build the
expression by clicking waveforms instead of typing instance names.

1. Open **Tools -> Calculator**.
2. Click **Clear** so no old expression remains.
3. Choose waveform selection (`wave`) and then click the `Vdd` trace. The
   expression area should now contain a voltage waveform such as `VT("/Vdd")`.
4. Click the multiplication operator `*`.
5. Choose waveform selection again and click the saved positive-terminal
   current trace of `V_VDD`. The current part normally looks like
   `IT("/V_VDD/PLUS")`; the exact terminal spelling may differ.
6. Because current entering the positive terminal is normally negative for a
   delivering supply, place a minus sign in front of the product. Do this only
   after confirming the plotted source current is negative.
7. Select the complete instantaneous-power expression.
8. Choose the `clip` function. Enter From=`1n` and To=`10n`, then accept.
9. Choose the `average` function and apply it to the clipped power waveform.
10. Click **Evaluate** (often the calculator button marked `=` or `123`).
11. Copy the complete numerical result and its unit into the result sheet.

The finished expression should be equivalent to this; do not worry if your
Cadence release displays slightly different waveform-name syntax:

```text
average(clip(-VT("/Vdd") * IT("/V_VDD/PLUS") 1n 10n))
```

The result must be a **positive number in watts**. A negative result means the
current sign was handled incorrectly. A result with units of amperes means
you averaged current but forgot to multiply by voltage.

Conceptually, the calculation is

```text
Pavg = [1/(t2-t1)] integral(t1 to t2) {-VDD(t) Iplus(t)} dt.
```

With a constant 1 V supply this reduces to

```text
Pavg = 1 V x average current drawn.
```

This is **core power drawn from VDD**. It excludes energy supplied by the
ideal `V_BIAS`, `UP`, `UP_b`, `DN`, and `DN_b` sources. If the assignment asks
for total testbench power, repeat the same signed calculation for every
independent source and add the averages. State explicitly which definition is
being reported; do not silently mix the two.

Do not average `abs(I)` unless current genuinely reverses and the assignment
explicitly asks for absolute power. `abs` can count returned energy as consumed
energy.

### 4.4 Calculator check and unit conversion

Because `VDD` is a constant 1.0 V, perform this simple independent check:

1. In the Calculator evaluate `average(clip(-IT("/V_VDD/PLUS") 1n 10n))`
   using the terminal path inserted by **wave**. This is `Iavg` in amperes
   when the positive-terminal current is negative; use the Section 4.1 sign
   convention if your saved current direction differs.
2. In the same Calculator, multiply that scalar by `1.0 V` (or by the VDD
   value shown in the schematic) and evaluate:

```text
Pavg = VDD x Iavg
     = 1.0 V x ______ A
     = ______ W
```

This answer should agree with the power-expression result apart from displayed
rounding. If it does not, recheck the selected current terminal, sign, and
time window.

Use the Calculator's multiplication operator to display microwatts directly:

```text
1 uW = 10^-6 W
Pavg[uW] = Pavg[W] x 10^6
```

Example of unit conversion only: if ViVA displays `1.319e-5 W`, then

```text
1.319 x 10^-5 W x 10^6 uW/W = 13.19 uW.
```

That example is not permission to record 13.19 uW if ViVA shows another
number.

Record both modes:

```text
P_UP   over 1-10 ns = ______ W = ______ uW
P_DN   over 1-10 ns = ______ W = ______ uW
```

If a single balanced-operation number is required, state the assumption that
UP and DN occur equally often, then evaluate in the Calculator

```text
Pavg,balanced = (P_UP + P_DN) / 2 = ______ uW.
```

If actual UP/DN duty probabilities are known, use
`Pavg = D_UP P_UP + D_DN P_DN + D_IDLE P_IDLE` instead.

---

## 5. Calculate Power-Delay Product (PDP) in ADE L Calculator

Use power and delay from the **same** model, load, temperature, supply, corner,
stimulus, and measurement convention.

```text
PDP = Pavg x t_pd.
```

The safest SI-unit calculation is

```text
PDP[J] = (Pavg in uW x 10^-6) x (t_pd in ps x 10^-12).
```

A useful direct conversion is

```text
PDP[fJ] = Pavg[uW] x t_pd[ps] / 1000.
```

First identify which mean delay set the reported `t_pd`: use `P_UP` if it was
`mean t_UP`, or `P_DN` if it was `mean t_DN`. Enter that mode's measured power
and delay as Calculator scalars. If power is displayed in `uW` and delay in
`ps`, divide the two displayed numerical values' product by `1000` to display
`fJ`:

```text
PDP[fJ] = Pavg[uW] * t_pd[ps] / 1000 = ______ fJ
```

Reference arithmetic, not a measured result:

```text
(13.19 uW x 16.71 ps) / 1000 = 0.2204049 fJ ~= 0.220 fJ
```

The paper's table rounds this to `0.221 fJ`; nearby prose says `0.225 fJ`.
The multiplication supports approximately `0.220-0.221 fJ`.

The balanced-operation power from Section 4 is a separate, stated duty-cycle
assumption. Do not silently pair it with one directional delay. Do not combine
power from one corner with delay from another unless explicitly reporting a
worst-case bound.

---

## 6. Calculate output swing (paper-style dynamic voltage range)

The charging and discharging limits come from two separate runs. Do not take
`ymax` of a switching spike or join unrelated old datasets.

### 6.1 Upper settled voltage

1. Restore the charging stimulus from Section 1.6 and `Vop ic = 0.54 V`.
2. In ADE confirm the transient stop time is `10n`, then netlist and run.
3. Plot `Vop` and zoom into the last five cycles (`9.5-10 ns`).
4. Ignore narrow edge spikes at the instant a control signal changes.
5. Open **Tools -> Calculator**, select `Vop` and `UP` with **wave**, and use
   `value(Vop (cross(UP 0.5 n "rising")-5p))` to evaluate the five samples
   before UP rising edges `n=96,97,98,99,100` for a 10 ns run. Replace
   `Vop` and `UP` with the expressions selected by **wave**. Use the same
   5 ps offset for all five samples. For a 20 ns run use `n=196..200`; for
   40 ns use `n=396..400`.
6. Record the five Calculator values in the table below.
7. Evaluate `abs(reading5-reading1)` in the Calculator.
   - If `|reading 5 - reading 1| <= 1 mV`, treat the upper limit as settled.
   - If it is greater than 1 mV, change the stop time to `20n`, rerun, and use
     the last five cycles of the new run. If necessary repeat with `40n`.
8. Evaluate `(U1+U2+U3+U4+U5)/5` in the Calculator. Call the result `V_HIGH`.

### 6.2 Lower settled voltage

1. Restore the discharging stimulus from Section 3.4 and `Vop ic = 0.62 V`.
2. Confirm the DN/DN_b sources are pulsing and UP/UP_b are held inactive as
   specified in Section 3.4. Netlist and run; never reuse the charging data.
3. In the Calculator evaluate `value(Vop (cross(DN 0.5 n "rising")-5p))`
   for each of the final five DN cycles, using the same `n` choices as in
   Section 6.1 for the selected stop time. Enter the five values in the table.
4. Evaluate `abs(L5-L1)` for the same `<= 1 mV` settling check. Extend and
   rerun if it fails.
5. Evaluate `(L1+L2+L3+L4+L5)/5` in the Calculator. Call it `V_LOW`.

### 6.3 Calculate and report in the Calculator

```text
Output swing = V_HIGH - V_LOW
Swing as percent of VDD = 100(V_HIGH - V_LOW)/VDD.
```

Record the five sampled Calculator results here:

| Quiet sample | Charging value (V) | Discharging value (V) |
|---:|---:|---:|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

```text
Upper settling check = |upper 5 - upper 1| = ______ V
Lower settling check = |lower 5 - lower 1| = ______ V

V_HIGH = (U1 + U2 + U3 + U4 + U5)/5 = ______ V
V_LOW  = (L1 + L2 + L3 + L4 + L5)/5 = ______ V

Output swing   = V_HIGH - V_LOW
               = ______ - ______
               = ______ V

Percent of VDD = 100 x output swing / 1.0 V
               = ______ %
```

If the waveform has not settled by 10 ns, extend both runs to the same longer
time. A still-rising endpoint is not `V_HIGH`, and a still-falling endpoint is
not `V_LOW`.

**STOP CHECK 6:** Both limits must pass the settling test. The reported swing
must satisfy `0 <= swing <= VDD` unless you can explain and exclude a transient
overshoot.

---

## 7. Derive the usable current-compliance dynamic range

This is the stronger engineering definition of dynamic range. It requires a
DC sweep in a separate testbench; ADE L Calculator evaluates the current
errors, mismatch, boundaries, and width.

### 7.1 Make the DC testbench manually

1. In Library Manager select the supplied cell `tb_mcml_charge_pump`.
2. Use the Library Manager **Copy** command (commonly **Edit -> Copy** or the
   right-click **Copy** command).
3. Keep the destination library `shivam` and enter destination cell name
   `tb_mcml_charge_pump_dc`.
4. Copy the `schematic` view and open the copied cell. Confirm the original
   transient testbench is still unchanged.
5. In the copy only, delete `V_UP`, `V_UP_B`, `V_DN`, and `V_DN_B`.
6. Press `I` and place four `analogLib/vdc` sources. Name them `V_UP_DC`,
   `V_UP_B_DC`, `V_DN_DC`, and `V_DN_B_DC`.
7. Connect each new source's positive terminal to its matching DUT pin and
   each negative terminal to the existing real ground:

| Source | Positive terminal connects to | Negative terminal connects to |
|---|---|---|
| `V_UP_DC` | `UP` | `Gnd`/node 0 |
| `V_UP_B_DC` | `UP_b` | `Gnd`/node 0 |
| `V_DN_DC` | `DN` | `Gnd`/node 0 |
| `V_DN_B_DC` | `DN_b` | `Gnd`/node 0 |

8. Place one more `analogLib/vdc` source and name it `V_FORCE`.
9. Connect `V_FORCE/PLUS` to `Vop` and `V_FORCE/MINUS` to the real ground.
   This source deliberately sets the output voltage during the DC sweep.
10. Keep `V_VDD = 1.0 V`, `V_BIAS = 0.45 V`, the `analogLib/gnd` symbol,
    and only the DUT's internal 300 fF load.
11. Choose **File -> Check and Save** and fix every wiring error.

The capacitor does not affect a converged DC result, but leaving the single
internal `CL` in place keeps this testbench tied to the supplied DUT.

### 7.2 Obtain charge current versus output voltage

1. Set the four source DC voltages:
   `UP=1.0`, `UP_b=0`, `DN=0`, and `DN_b=1.0`.
2. From this DC testbench choose **Launch -> ADE L/Explorer**. Start with an
   empty ADE session; do not load a state.
3. Select Spectre and the same model section and 27 °C temperature used for
   the transient measurements.
4. Choose **Analyses -> Choose** and select `dc`.
5. Choose **Component Parameter** as the sweep variable.
6. Click **Select Component**, then click the `V_FORCE` source on the
   schematic.
7. Choose its DC-voltage parameter (`dc` or `vdc`).
8. Select a linear Start-Stop sweep and enter:
   Start=`0`, Stop=`1.0`, Step=`0.01` V.
9. Use **Outputs -> To Be Saved -> Select on Schematic** and click
   `V_FORCE/PLUS` to save its terminal current.
10. Run and plot that current against the swept output voltage.
11. In charging mode, current from the pump enters `V_FORCE/PLUS`, so define:

```text
I_UP(Vop) = I(V_FORCE/PLUS)
```

12. Open **Tools -> Calculator**. Select the plotted current with **wave**;
    use the inserted expression for `I_UP(V)`. Use `value(I_UP 0.5)` and
    **Evaluate** to obtain `I_UP,REF` in amperes. If it is zero or negative,
    recheck the controls and current sign.
13. In ADE L use **Results -> Save** and give this DC result a distinct name,
    such as `charge_dc`. ADE L may overwrite an unsaved run on the next run.

### 7.3 Obtain discharge current versus output voltage

1. Return to the DC testbench schematic.
2. Change only the four control-source values to:
   `UP=0`, `UP_b=1.0`, `DN=1.0`, and `DN_b=0`.
3. Check and Save, then return to ADE.
4. Confirm the DC sweep is still 0 to 1.0 V in 0.01 V steps.
5. Netlist and run again. In ADE L use **Results -> Save** and name this
   result `discharge_dc`.
6. During discharge, `V_FORCE` supplies current out of its positive terminal,
   so its saved positive-terminal current is normally negative. Define the
   positive discharge magnitude as:

```text
I_DN(Vop) = -I(V_FORCE/PLUS)
```

7. In the Calculator select the new current trace with **wave**, negate it
   with the `-` operator, and **Evaluate**. This is the `I_DN(V)` waveform.
8. Use `value(I_DN 0.5)` and **Evaluate** to obtain `I_DN,REF` in amperes.
   If the result is zero or negative, recheck the controls and sign.

### 7.4 Apply an explicit 10% criterion

1. Use **Results -> Select** to load both saved DC results into ViVA. In the
   Results Browser plot the `V_FORCE/PLUS` current from `charge_dc` and from
   `discharge_dc` together. Confirm that both x-axes run from 0 to 1.0 V in
   0.01 V steps and that the charge current is positive while the discharge
   terminal current is negative. If the Calculator selects the wrong run,
   right-click the desired result in the Results Browser and choose **Set
   Context**, or use the Calculator's result selector at the top, then click
   the intended plotted trace again.
2. In the Calculator build `I_UP` from the **charge** trace and `I_DN` by
   negating the **discharge** trace. Select plotted traces with **wave** so
   each expression refers to its saved result, and evaluate `value(I_UP 0.5)`
   and `value(I_DN 0.5)` again. The reference currents must be positive.
3. Use Calculator arithmetic and the `abs` function to build and **Plot**
   these three waveforms against swept `Vop`. `I_UP` and `I_DN` below mean
   the two wave expressions selected from their saved runs; replace
   `I_UP_REF` and `I_DN_REF` with the scalar values from Step 2. These are
   expression templates, not new Calculator variable declarations:

```text
charge_error    = 100*abs(I_UP-I_UP_REF)/I_UP_REF
discharge_error = 100*abs(I_DN-I_DN_REF)/I_DN_REF
mismatch        = 200*abs(I_UP-I_DN)/(I_UP+I_DN)
```

4. Add a horizontal 10% reference line or set the plot's y-axis grid at 10%.
   The examples above give percentages as plain numbers, so the threshold is
   `10`, not `0.10`. A voltage passes only when **all three** plotted errors
   are at or below 10. Do not take a boundary from just one curve.
5. Confirm all three errors pass at the `0.50 V` reference point. If any
   fails there, record that the stated 10% criterion has no usable interval
   around the chosen reference and review the criterion or circuit. Otherwise,
   find the contiguous passing region containing `0.50 V`. Zoom around its
   low and high ends. Use Calculator `value(charge_error V)`,
   `value(discharge_error V)`, and `value(mismatch V)` at the candidate 0.01 V
   sweep points. Evaluate all three at each boundary and at the adjacent
   outside point. The boundary is the first/last **sampled** passing voltage;
   do not interpolate between samples unless you rerun a finer DC sweep and
   state its step size. Check the plotted curves for any failure inside the
   chosen interval. If there are disconnected passing regions, report the
   interval containing 0.50 V and mention the other regions separately.
6. Enter the two accepted boundary voltages into the Calculator and evaluate
   their difference:

```text
V_DR,LOW  = lowest consecutive passing Vop = ______ V
V_DR,HIGH = highest consecutive passing Vop = ______ V
Usable dynamic range = V_DR,HIGH - V_DR,LOW = ______ V
```

State the criterion with the result: “usable dynamic range at <=10% current
variation and <=10% UP/DN mismatch.” If the course uses a different tolerance,
replace 10% everywhere and state the chosen number.

**STOP CHECK 7:** The reported acceptable points must form one consecutive
interval around 0.50 V. Report its two boundaries, width, tolerance, model,
temperature, and VDD together. A bare voltage range without the criterion is
incomplete.

---

## 8. Final result sheet

Complete this from the fresh waveforms in front of the professor:

| Item | Value | Exact extraction condition |
|---|---:|---|
| Model/corner | | model file and section |
| Temperature | | 27 °C nominal |
| VDD | | 1.0 V nominal |
| Total CL | | 300 fF unless intentionally changed |
| Frequency | | `1/100 ps = 10 GHz` |
| Mean UP delay | | pulses 11-20, local 50% method |
| Mean DN delay | | pulses 11-20, local 50% method |
| Reported `t_pd` | | larger directional mean |
| UP-mode power | | average over 1-10 ns |
| DN-mode power | | average over 1-10 ns |
| Reported power | | name the duty/mode assumption |
| PDP | | power of the direction that set `t_pd` x that delay |
| `V_HIGH` | | five quiet samples after settling |
| `V_LOW` | | five quiet samples after settling |
| Output swing | | `V_HIGH - V_LOW` |
| Usable dynamic range | | ADE L DC sweep, Calculator error curves, and stated tolerance |

Attach five screenshots taken from the fresh runs:

1. Charging input/output traces with the local 50% crossing and Calculator delay result visible.
2. Discharging input/output traces with the local 50% crossing and Calculator delay result visible.
3. VDD current/power waveform with the 1-10 ns Calculator averaging window visible.
4. Settled charging and discharging output limits used for output swing.
5. DC charge/discharge-current curves with dynamic-range boundaries marked.

For each screenshot, make sure the trace names, x-axis, y-axis, markers, and
units are visible. A cropped picture containing only a number is not evidence
of how that number was obtained.

### Final spoken derivation order

If asked to explain the complete result, point to the fresh waveforms and say
the following in this order, replacing blanks with measured values:

1. “The supplied circuit uses `VDD=1.0 V`, `Vbias=0.45 V`, one `300 fF` load,
   a `100 ps` period, and therefore a `10 GHz` command frequency.”
2. “I measured each directional delay from the input's 50% crossing to the
   local output-step 50% crossing. The ten-pulse means are `______ ps` for UP
   and `______ ps` for DN. I report the larger value, `______ ps`.”
3. “I measured the signed power delivered by VDD over 1-10 ns. It is
   `______ uW` in UP mode and `______ uW` in DN mode. Under the stated
   balanced-mode assumption, the reported power is `______ uW`.”
4. “PDP equals power times delay. Using the power of the direction that set
   the reported delay,
   `______ uW x ______ ps / 1000 = ______ fJ`.”
5. “The settled upper and lower output limits are `______ V` and `______ V`,
   so the output swing is `______ V`, or `______%` of VDD.”
6. “Using an ADE L DC sweep and the stated 10% current-variation/mismatch
   rule, the usable dynamic range is `______ V` to `______ V`, a width of
   `______ V`.”

### Final do-not-forget checklist

- [ ] The 237 ps proof run ended at 237 ps.
- [ ] The schematic contains one effective 300 fF output load, not 600 fF.
- [ ] A real `analogLib/gnd` is connected.
- [ ] Model path/section, temperature, VDD, bias, and maximum step are written.
- [ ] Charging and discharging results came from separate fresh runs.
- [ ] Ten UP-delay and ten DN-delay Calculator results and their means are recorded.
- [ ] Power sign and 1-10 ns window are shown.
- [ ] PDP units were converted to femtojoules correctly.
- [ ] Upper and lower output limits passed the settling test.
- [ ] Dynamic range includes its tolerance definition.
- [ ] Every reported number has a fresh waveform and/or Calculator result screenshot.

---

## 9. Fast troubleshooting

| Symptom | Cause/check |
|---|---|
| Run requested 237 ps but plot ends at 10 ns | Synthetic `spectre` wrapper is active; use a real licensed installation |
| Cannot plot VDD current | Save the positive-terminal current of `V_VDD`, then netlist and rerun |
| Power is negative | Apply the source-current sign convention from Section 4.1 |
| Output barely moves | Check complementary inputs, `Vbias=0.45 V`, model section, and load duplication |
| Delay is negative | Wrong output crossing or wrong input edge was selected |
| `ymax` exceeds VDD briefly | It is a switching spike, not the settled upper limit |
| Results change when rerun | Confirm the same initial condition, model section, max step, temperature, and measurement window |
| Delay is unlike 16.71 ps | First verify load, real solver, model, stimulus, and extraction definition; do not force a Calculator crossing to the paper value |

The defensible statement is: **“These numbers were extracted from this run
using the written definitions and windows.”** It is not defensible to say the
simulation matches the paper merely because the paper's numbers appear in a
schematic label, console message, generated plot, or saved data file.
