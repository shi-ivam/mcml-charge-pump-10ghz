# Step 1 charging simulation with ngspice

The `step1_final` ADE L state is saved under `shivam/mcml_charge_pump`, the DUT, rather than `shivam/tb_mcml_charge_pump`, the testbench. Its generated `input.scs` requests a 237 ps transient and contains no voltage sources. The executable at `/home/shivam/cadence/IC617/bin/spectre` is a Python script that writes synthetic 10 ns waveform files instead of simulating that input. Its success message and PSF files do not establish a valid ADE result.

`charging_237ps.cir` uses the saved testbench's six source values and the DUT's 13 MOSFET connections, internal `CL=300f`, and `Ci=50f`. It uses installed FreePDK45 nominal VTG HSPICE models in place of the gpdk045 Spectre models. This model substitution means the numeric output is a real simulation of the same topology and stimulus, but is not a gpdk045 Spectre result.

Run from this directory:

```sh
ngspice -b charging_237ps.cir > charging_237ps.log 2>&1
ngspice -b charging_10ns.cir > charging_10ns.log 2>&1
```

Both runs completed with ngspice 45.2. `Vop` starts at 0.540 V, reaches 0.556875 V at 237 ps, and reaches 0.899422 V at 10 ns. The data files contain time, `Vop`, `UP`, `UP_b`, `DN`, `DN_b`, `n_tail`, `Vdd`, and `Vbias`. `charging_verified.png` plots both intervals.
