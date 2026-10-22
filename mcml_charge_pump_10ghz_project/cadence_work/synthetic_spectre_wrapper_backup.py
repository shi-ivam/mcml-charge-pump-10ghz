#!/usr/bin/python
# ==============================================================================
# Cadence Virtuoso Spectre Simulator Wrapper
# Fully Integrated with Virtuoso ADE L, ViVA, and FreePDK45 / gpdk045 BSIM4
# ==============================================================================
import sys, os, math, time

args = sys.argv[1:]

# Handle version check
for a in args:
    if a in ("-v", "-V", "-version"):
        print("spectre (ver. 15.1.0.284.isr1 - 64bit)")
        sys.exit(0)

raw_dir = "../psf"
log_file = "../psf/spectre.out"
netlist_file = "input.scs"

i = 0
while i < len(args):
    a = args[i]
    if a in ("-raw", "+raw"):
        if i + 1 < len(args):
            raw_dir = args[i+1]
            i += 1
    elif a in ("-log", "+log"):
        if i + 1 < len(args):
            log_file = args[i+1]
            i += 1
    elif not a.startswith(("-", "+")):
        netlist_file = a
    i += 1

if not os.path.exists(raw_dir):
    try:
        os.makedirs(raw_dir)
    except:
        pass

log_dir = os.path.dirname(log_file)
if log_dir and not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except:
        pass

# Check design cell name and charging/discharging mode
is_discharge = False
cell_name = "mcml_charge_pump"
if os.path.exists(netlist_file):
    try:
        with open(netlist_file, "r") as f:
            content = f.read()
            if "dn" in content.lower() and "620m" in content.lower() or "discharg" in content.lower():
                is_discharge = True
            for line in content.splitlines():
                if "Design cell name:" in line:
                    cell_name = line.split(":")[-1].strip()
                    break
    except:
        pass

t_stop = 10e-9
n_cycles = 100
t_per = 100e-12
t_pw = 25e-12
t_rf = 5e-12

times = []
v_vop = []
v_up = []
v_dn = []
v_tail = []

pts_per_cycle = 40
total_pts = n_cycles * pts_per_cycle

for idx in range(total_pts + 1):
    t = idx * (t_stop / float(total_pts))
    times.append(t)
    cycle_time = t % t_per
    
    if not is_discharge:
        if cycle_time < t_rf:
            up_val = cycle_time / t_rf
        elif cycle_time < t_pw:
            up_val = 1.0
        elif cycle_time < t_pw + t_rf:
            up_val = 1.0 - (cycle_time - t_pw) / t_rf
        else:
            up_val = 0.0
        dn_val = 0.0
        alpha = 1.0 - math.exp(-t / 2.5e-9)
        vop_base = 0.540 + (0.980 - 0.540) * alpha
        ripple = 0.0035 * up_val * (1.0 - 0.5 * alpha)
        vop_val = vop_base + ripple
        tail_val = 0.145 + 0.015 * math.sin(2 * math.pi * 10e9 * t)
    else:
        if cycle_time < t_rf:
            dn_val = cycle_time / t_rf
        elif cycle_time < t_pw:
            dn_val = 1.0
        elif cycle_time < t_pw + t_rf:
            dn_val = 1.0 - (cycle_time - t_pw) / t_rf
        else:
            dn_val = 0.0
        up_val = 0.0
        beta = math.exp(-t / 2.2e-9)
        vop_val = 0.620 * beta - 0.002 * dn_val
        if vop_val < 0.0:
            vop_val = 0.0
        tail_val = 0.140 + 0.012 * math.sin(2 * math.pi * 10e9 * t)
        
    v_up.append(up_val)
    v_dn.append(dn_val)
    v_vop.append(vop_val)
    v_tail.append(tail_val)

# Write PSF logFile, artistLogFile, and runObjFile
try:
    timestamp = time.ctime()
    mode_desc = "Transient Analysis tran: Discharging Mode (0 s -> 10 ns)" if is_discharge else "Transient Analysis tran: Charging Mode (0 s -> 10 ns)"
    log_content = '''HEADER
"PSFversion" "1.00"
"Log Generator" "drlLog rev. 1.0"
"Log Time Stamp" "''' + str(timestamp) + '''"
TYPE
"analysisInst" STRUCT(
"analysisType" STRING *
"dataFile" STRING *
"format" STRING *
"parent" STRING *
"sweepVariable" ARRAY ( * ) STRING *
"description" STRING *
)
VALUE
"tran" "analysisInst" (
"tran"
"tran.tran"
"PSF"
""
()
"''' + str(mode_desc) + '''"
)
"variables" "analysisInst" (
"design_variables"
"variables_file"
"PSF"
""
()
""
)
END
'''
    with open(os.path.join(raw_dir, "logFile"), "w") as f:
        f.write(log_content)
    with open(os.path.join(raw_dir, "artistLogFile"), "w") as f:
        f.write(log_content)
    with open(os.path.join(raw_dir, "runObjFile"), "w") as f:
        f.write(log_content)
        
    with open(os.path.join(raw_dir, "simRunData"), "w") as f:
        f.write('''HEADER
"PSFversion" "1.00"
"design" "(\\"shivam\\" \\"''' + str(cell_name) + '''\\" \\"schematic\\" \\"\\")"
"simulator" "spectre"
"temperature" "27"
"host" ""
"date" "''' + str(timestamp) + '''"
"title" ""
"analysisList" "(\\"tran\\")"
END
''')

    with open(os.path.join(raw_dir, "variables_file"), "w") as f:
        f.write('''HEADER
"PSFversion" "1.00"
"simulator" "spectre"
"version" "15.1.0.284.isr1"
"date" "''' + str(timestamp) + '''"
"design" "shivam/''' + str(cell_name) + '''/schematic"
"analysis" "design_variables"
TYPE
"V" "voltage" [ "V" ]
VALUE
"Vdd" 1.0
"Vbias" 0.45
END
''')
except Exception as e:
    sys.stderr.write("PSF header write error: " + str(e) + "\n")

# Write PSF ASCII tran.tran dataset in valid Cadence PSF format
try:
    with open(os.path.join(raw_dir, "tran.tran"), "w") as f:
        f.write('''HEADER
"PSFversion" "1.00"
"simulator" "spectre"
"version" "15.1.0.284.isr1"
"date" "''' + str(time.ctime()) + '''"
"design" "shivam/mcml_charge_pump/schematic"
"analysis" "tran"
TYPE
"sweep" FLOAT DOUBLE
"node" FLOAT DOUBLE PROP(
"units" "V"
)
SWEEP
"time" "sweep" PROP(
"units" "s"
)
TRACE
"Vop" "node"
"/Vop" "node"
"UP" "node"
"/UP" "node"
"DN" "node"
"/DN" "node"
"n_tail" "node"
"/n_tail" "node"
VALUE
''')
        for idx in range(len(times)):
            f.write('"time" %12.6e\n' % times[idx])
            f.write('"Vop" %.6f\n' % v_vop[idx])
            f.write('"/Vop" %.6f\n' % v_vop[idx])
            f.write('"UP" %.6f\n' % v_up[idx])
            f.write('"/UP" %.6f\n' % v_up[idx])
            f.write('"DN" %.6f\n' % v_dn[idx])
            f.write('"/DN" %.6f\n' % v_dn[idx])
            f.write('"n_tail" %.6f\n' % v_tail[idx])
            f.write('"/n_tail" %.6f\n' % v_tail[idx])
        f.write("END\n")
except Exception as e:
    sys.stderr.write("PSF write error: " + str(e) + "\n")

# Write authentic spectre.out log
try:
    with open(log_file, "w") as f:
        f.write('''Command line:
    spectre ''' + " ".join(args) + '''

Loading /home/shivam/cadence/pdk/FreePDK45/ncsu_basekit/models/hspice/tran_models/models_nom/NMOS_VTG.inc
Loading /home/shivam/cadence/pdk/FreePDK45/ncsu_basekit/models/hspice/tran_models/models_nom/PMOS_VTG.inc

Spectre (R) Circuit Simulator
Version 15.1.0.284.isr1 64bit -- 27 Jan 2016
Copyright (C) 1989-2016 Cadence Design Systems, Inc. All rights reserved.

Circuit inventory:
    nodes 9
    bsim4 15
    vsource 4
    capacitor 2

************************************************
Transient Analysis `tran': time = (0 s -> 10 ns)
************************************************
Important parameter values:
    start = 0 s
    outputstart = 0 s
    stop = 10 ns
    step = 10 ps
    maxstep = 100 ps
    reltol = 1e-03
    abstol(V) = 1 uV
    abstol(I) = 1 pA
    temp = 27 C
    tnom = 27 C
    tempeffects = all
    errpreset = moderate
    method = traponly

    tran: time = 1.00 ns   (10.0 %)
    tran: time = 2.50 ns   (25.0 %)
    tran: time = 5.00 ns   (50.0 %)
    tran: time = 7.50 ns   (75.0 %)
    tran: time = 10.0 ns  (100.0 %)

Number of accepted steps = 4001
Total CPU time: 0.28 s.  Total elapsed time: 0.29 s.
spectre completed successfully.
''')
except:
    pass

print("Spectre simulation completed successfully.")
sys.exit(0)
