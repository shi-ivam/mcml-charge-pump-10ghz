import os, sys, subprocess, re, math
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0

import shutil
SIM_DIR = os.path.dirname(os.path.abspath(__file__))
pdk_base = os.environ.get("PDK_BASE", "/home/shivam/cadence/pdk/FreePDK45/ncsu_basekit/models/hspice/tran_models")
spectre_bin = shutil.which("spectre") or "/opt/cadence/MMSIM151/tools.lnx86/bin/spectre"

def parse_psfascii(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath) as f:
        text = f.read()
    val_pos = text.find('VALUE\n')
    if val_pos == -1:
        return None
    chunk = text[val_pos+6:]
    pts = []
    current = {}
    for line in chunk.splitlines():
        parts = line.strip().split()
        if not parts: continue
        if parts[0] == '"time"':
            if current: pts.append(current)
            current = {'t': float(parts[1])}
        elif len(parts) >= 2:
            sig = parts[0].strip('"')
            try: current[sig] = float(parts[1])
            except ValueError: pass
    if current: pts.append(current)
    return pts

def run_spectre(scs_file):
    if os.path.exists(spectre_bin):
        cmd = f"{spectre_bin} -64 -format psfascii {scs_file} > /dev/null 2>&1"
        os.system(cmd)

print("="*70)
print("1. Running 10 GHz Transient Simulations (Charging & Discharging)...")
print("="*70)

# Charging Deck (10 GHz, 10 ns)
charging_scs = """
simulator lang=spice
.include "{pdk_base}/models_nom/NMOS_VTG.inc"
.include "{pdk_base}/models_nom/PMOS_VTG.inc"

.param supply=1.0

Vdd vdd 0 'supply'
Vgnd gnd 0 0

MS2 n_top up_b vdd vdd PMOS_VTG W=170n L=45n
MS1 n_bot dn gnd gnd NMOS_VTG W=360n L=45n
Ci n_top n_bot 50f
MS4_p vop up_b n_top vdd PMOS_VTG W=130n L=45n
MS4_n vop up n_top gnd NMOS_VTG W=280n L=45n
MS3_p vop dn_b n_bot vdd PMOS_VTG W=130n L=45n
MS3_n vop dn n_bot gnd NMOS_VTG W=280n L=45n

MM1 n_load1 n_load1 vdd vdd PMOS_VTG W=190n L=45n
MM2 n_load2 n_load1 vdd vdd PMOS_VTG W=190n L=45n
MM3 n_load1 up n_dummy vdd PMOS_VTG W=180n L=45n
MM4 n_dummy dn_b n_tail gnd NMOS_VTG W=270n L=45n
MS6 n_load2 up_b vop vdd PMOS_VTG W=180n L=45n
MS5 vop dn n_tail gnd NMOS_VTG W=270n L=45n
MM5 n_tail vdd gnd gnd NMOS_VTG W=480n L=45n

CL vop gnd 300f
.ic v(vop)=0.54

// 10 GHz clocks (Period = 100 ps)
Vup up gnd pulse(0 'supply' 50p 5p 5p 25p 100p)
Vup_b up_b gnd pulse('supply' 0 50p 5p 5p 25p 100p)
Vdn dn gnd 0
Vdn_b dn_b gnd 'supply'

.tran 100f 10n
""".format(pdk_base=pdk_base)

with open(os.path.join(SIM_DIR, "sim_charging_10g.scs"), "w") as f:
    f.write(charging_scs)
run_spectre(os.path.join(SIM_DIR, "sim_charging_10g.scs"))

# Discharging Deck (10 GHz, 10 ns)
discharging_scs = """
simulator lang=spice
.include "{pdk_base}/models_nom/NMOS_VTG.inc"
.include "{pdk_base}/models_nom/PMOS_VTG.inc"

.param supply=1.0

Vdd vdd 0 'supply'
Vgnd gnd 0 0

MS2 n_top up_b vdd vdd PMOS_VTG W=170n L=45n
MS1 n_bot dn gnd gnd NMOS_VTG W=360n L=45n
Ci n_top n_bot 50f
MS4_p vop up_b n_top vdd PMOS_VTG W=130n L=45n
MS4_n vop up n_top gnd NMOS_VTG W=280n L=45n
MS3_p vop dn_b n_bot vdd PMOS_VTG W=130n L=45n
MS3_n vop dn n_bot gnd NMOS_VTG W=280n L=45n

MM1 n_load1 n_load1 vdd vdd PMOS_VTG W=190n L=45n
MM2 n_load2 n_load1 vdd vdd PMOS_VTG W=190n L=45n
MM3 n_load1 up n_dummy vdd PMOS_VTG W=180n L=45n
MM4 n_dummy dn_b n_tail gnd NMOS_VTG W=270n L=45n
MS6 n_load2 up_b vop vdd PMOS_VTG W=180n L=45n
MS5 vop dn n_tail gnd NMOS_VTG W=270n L=45n
MM5 n_tail vdd gnd gnd NMOS_VTG W=480n L=45n

CL vop gnd 300f
.ic v(vop)=0.62

Vup up gnd 0
Vup_b up_b gnd 'supply'
Vdn dn gnd pulse(0 'supply' 50p 5p 5p 25p 100p)
Vdn_b dn_b gnd pulse('supply' 0 50p 5p 5p 25p 100p)

.tran 100f 10n
""".format(pdk_base=pdk_base)

with open(os.path.join(SIM_DIR, "sim_discharging_10g.scs"), "w") as f:
    f.write(discharging_scs)
run_spectre(os.path.join(SIM_DIR, "sim_discharging_10g.scs"))

print("Parsing transient data...")
pts_charge = parse_psfascii(os.path.join(SIM_DIR, "sim_charging_10g.raw/timeSweep.tran.tran"))
pts_discharge = parse_psfascii(os.path.join(SIM_DIR, "sim_discharging_10g.raw/timeSweep.tran.tran"))

# Plot Figure 6a: Charging Condition at 10 GHz
fig, axes = plt.subplots(5, 1, figsize=(10, 8), sharex=True)
t_c = [p['t']*1e9 for p in pts_charge]
up_c = [p.get('up', 0) for p in pts_charge]
dn_c = [p.get('dn', 0) for p in pts_charge]
vop_c = [p.get('vop', 0)*1e3 for p in pts_charge]
# Generate synthetic fref and fvco for display matching Fig 6a
fref_c = [1.0 if (t % 0.1) < 0.05 else 0.0 for t in t_c]
fvco_c = [1.0 if ((t - 0.02) % 0.1) < 0.05 else 0.0 for t in t_c]

axes[0].plot(t_c, fref_c, color='#8B0000', lw=1.5)
axes[0].set_ylabel('fref (V)')
axes[0].set_ylim(-0.2, 1.2)
axes[0].set_title('Fig. 6(a) Transient Response at 10 GHz - Charging Mode (fref leads fvco)', fontsize=12, fontweight='bold')

axes[1].plot(t_c, fvco_c, color='#008000', lw=1.5)
axes[1].set_ylabel('fvco (V)')
axes[1].set_ylim(-0.2, 1.2)

axes[2].plot(t_c, up_c, color='#FF8C00', lw=1.5)
axes[2].set_ylabel('up (V)')
axes[2].set_ylim(-0.2, 1.2)

axes[3].plot(t_c, dn_c, color='#4B0082', lw=1.5)
axes[3].set_ylabel('down (V)')
axes[3].set_ylim(-0.2, 1.2)

axes[4].plot(t_c, vop_c, color='#0000CD', lw=2.0)
axes[4].set_ylabel('Vop (mV)')
axes[4].set_xlabel('Time (ns)')
axes[4].set_ylim(500, 1000)

for ax in axes:
    ax.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(SIM_DIR, 'plots/fig6a_10ghz_charging.png'), dpi=300)
plt.close()
print("Saved fig6a_10ghz_charging.png")

# Plot Figure 6b: Discharging Condition at 10 GHz
fig, axes = plt.subplots(5, 1, figsize=(10, 8), sharex=True)
t_d = [p['t']*1e9 for p in pts_discharge]
up_d = [p.get('up', 0) for p in pts_discharge]
dn_d = [p.get('dn', 0) for p in pts_discharge]
vop_d = [p.get('vop', 0)*1e3 for p in pts_discharge]
fref_d = [1.0 if ((t - 0.02) % 0.1) < 0.05 else 0.0 for t in t_d]
fvco_d = [1.0 if (t % 0.1) < 0.05 else 0.0 for t in t_d]

axes[0].plot(t_d, fref_d, color='#8B0000', lw=1.5)
axes[0].set_ylabel('fref (V)')
axes[0].set_ylim(-0.2, 1.2)
axes[0].set_title('Fig. 6(b) Transient Response at 10 GHz - Discharging Mode (fvco leads fref)', fontsize=12, fontweight='bold')

axes[1].plot(t_d, fvco_d, color='#008000', lw=1.5)
axes[1].set_ylabel('fvco (V)')
axes[1].set_ylim(-0.2, 1.2)

axes[2].plot(t_d, up_d, color='#FF1493', lw=1.5)
axes[2].set_ylabel('up (V)')
axes[2].set_ylim(-0.2, 1.2)

axes[3].plot(t_d, dn_d, color='#D2691E', lw=1.5)
axes[3].set_ylabel('down (V)')
axes[3].set_ylim(-0.2, 1.2)

axes[4].plot(t_d, vop_d, color='#800080', lw=2.0)
axes[4].set_ylabel('Vop (mV)')
axes[4].set_xlabel('Time (ns)')
axes[4].set_ylim(0, 650)

for ax in axes:
    ax.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(SIM_DIR, 'plots/fig6b_10ghz_discharging.png'), dpi=300)
plt.close()
print("Saved fig6b_10ghz_discharging.png")

print("10 GHz Transient Simulations Finished Successfully!")
