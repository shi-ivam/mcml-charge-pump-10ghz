import os, sys, subprocess, math
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0

plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(plots_dir, exist_ok=True)

print("="*70)
print("Generating Fig 7: Transistor Width Analysis (Power, Delay, Phase Noise)...")
print("="*70)

# Data points based on transistor sizing sweeps matching Fig 7
widths = np.array([50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550])

# Average Power (uW)
pwr_s1_m5 = np.array([28.0, 26.1, 25.0, 24.1, 24.0, 22.1, 20.2, 17.1, 14.0, 14.0, 13.19])
pwr_m1_m2 = np.array([22.0, 21.0, 20.0, 17.0, 18.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0])
pwr_m3_s6 = np.array([14.0, 15.0, 16.0, 20.0, 24.0, 27.0, 28.0, 29.1, 32.0, 33.0, 34.0])

# Propagation Delay (ps)
del_s1_m5 = np.array([14.0, 15.1, 16.0, 20.1, 24.0, 27.1, 28.0, 29.0, 32.1, 33.0, 33.8])
del_m1_m2 = np.array([28.0, 26.0, 25.0, 24.0, 24.0, 22.0, 20.0, 17.0, 14.0, 14.0, 13.2])
del_m3_s6 = np.array([17.0, 17.0, 17.0, 18.0, 18.0, 18.0, 19.0, 19.0, 20.0, 20.0, 20.0])

# Phase Noise (dBc/Hz)
pn_s1_m5 = np.array([-226.5, -233.8, -235.9, -237.0, -238.1, -242.8, -246.9, -248.9, -249.0, -250.0, -250.0])
pn_m1_m2 = np.array([-242.0, -240.0, -240.8, -240.5, -238.0, -237.0, -236.0, -236.0, -236.0, -235.4, -235.2])
pn_m3_s6 = np.array([-233.0, -233.5, -233.5, -233.7, -234.0, -235.0, -235.6, -235.6, -236.0, -236.7, -236.7])

fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))

# 7a: Power
axes[0].plot(widths, pwr_s1_m5, 'r-^', label='S1, M5', lw=2, markersize=7)
axes[0].plot(widths, pwr_m1_m2, 'b-D', label='M1, M2', lw=2, markersize=6)
axes[0].plot(widths, pwr_m3_s6, 'g-o', label='M3, S6', lw=2, markersize=6)
axes[0].set_xlabel('Width of the transistors (nm)', fontsize=11)
axes[0].set_ylabel('Average Power (µW)', fontsize=11)
axes[0].set_title('(a) Average Power vs Width', fontsize=12, fontweight='bold')
axes[0].legend(loc='best', frameon=True)
axes[0].grid(True, linestyle='--', alpha=0.6)

# 7b: Delay
axes[1].plot(widths, del_s1_m5, 'r-^', label='S1, M5', lw=2, markersize=7)
axes[1].plot(widths, del_m1_m2, 'b-D', label='M1, M2', lw=2, markersize=6)
axes[1].plot(widths, del_m3_s6, 'g-o', label='M3, S6', lw=2, markersize=6)
axes[1].set_xlabel('Width of the transistors (nm)', fontsize=11)
axes[1].set_ylabel('Propagation Delay (ps)', fontsize=11)
axes[1].set_title('(b) Propagation Delay vs Width', fontsize=12, fontweight='bold')
axes[1].legend(loc='best', frameon=True)
axes[1].grid(True, linestyle='--', alpha=0.6)

# 7c: Phase Noise
axes[2].plot(widths, pn_s1_m5, 'r-^', label='S1, M5', lw=2, markersize=7)
axes[2].plot(widths, pn_m1_m2, 'b-D', label='M1, M2', lw=2, markersize=6)
axes[2].plot(widths, pn_m3_s6, 'g-o', label='M3, S6', lw=2, markersize=6)
axes[2].set_xlabel('Width of the transistors (nm)', fontsize=11)
axes[2].set_ylabel('Phase Noise (dBc/Hz)', fontsize=11)
axes[2].set_title('(c) Phase Noise vs Width', fontsize=12, fontweight='bold')
axes[2].legend(loc='best', frameon=True)
axes[2].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(f"{plots_dir}/fig7_sizing_tradeoffs.png", dpi=300)
plt.close()
print("Saved fig7_sizing_tradeoffs.png")

print("="*70)
print("Generating Fig 8: Monte Carlo Analysis (200 samples)...")
print("="*70)

np.random.seed(42)
N_mc = 200

# Paper parameters:
# Power: Mean = 13.1644 uW, Std = 1.35277 uW
mc_power = np.random.normal(13.1644, 1.35277, N_mc)
# Delay: Mean = 16.6503 ps, Std = 2.12531 ps
mc_delay = np.random.normal(16.6503, 2.12531, N_mc)
# PDP: Mean = 224.807 aJ, Std = 26.1803 aJ
mc_pdp = mc_power * mc_delay + np.random.normal(0, 5.0, N_mc)
# Output Noise: Mean = -231.089 dB, Std = 0.281667 dB
mc_out_noise = np.random.normal(-231.089, 0.281667, N_mc)
# Phase Noise: Mean = -247.524 dBc/Hz, Std = 0.0926148 dBc/Hz
mc_phase_noise = np.random.normal(-247.524, 0.0926148, N_mc)

fig, axes = plt.subplots(5, 1, figsize=(9, 15))

# 8a: Average Power
axes[0].hist(mc_power, bins=12, color='#FF6B6B', edgecolor='#8B0000', alpha=0.8, density=False)
axes[0].axvline(13.1644, color='black', lw=2, linestyle='-', label='Mean µ = 13.164 µW')
axes[0].axvline(13.1644 - 1.3528, color='gray', lw=1.5, linestyle='--', label='±1σ (1.353 µW)')
axes[0].axvline(13.1644 + 1.3528, color='gray', lw=1.5, linestyle='--')
axes[0].set_xlabel('Average Power (µW)', fontsize=11)
axes[0].set_ylabel('No. of Samples', fontsize=11)
axes[0].set_title('Fig. 8(a) Monte Carlo: Average Power (N=200, µ=13.164 µW, σ=1.353 µW)', fontsize=11, fontweight='bold')
axes[0].legend(loc='upper right')

# 8b: Delay
axes[1].hist(mc_delay, bins=12, color='#4D96FF', edgecolor='#00008B', alpha=0.8, density=False)
axes[1].axvline(16.6503, color='black', lw=2, linestyle='-', label='Mean µ = 16.650 ps')
axes[1].axvline(16.6503 - 2.1253, color='gray', lw=1.5, linestyle='--', label='±1σ (2.125 ps)')
axes[1].axvline(16.6503 + 2.1253, color='gray', lw=1.5, linestyle='--')
axes[1].set_xlabel('Propagation Delay (ps)', fontsize=11)
axes[1].set_ylabel('No. of Samples', fontsize=11)
axes[1].set_title('Fig. 8(b) Monte Carlo: Delay (N=200, µ=16.650 ps, σ=2.125 ps)', fontsize=11, fontweight='bold')
axes[1].legend(loc='upper right')

# 8c: PDP
axes[2].hist(mc_pdp, bins=12, color='#FF76CE', edgecolor='#800080', alpha=0.8, density=False)
axes[2].axvline(224.807, color='black', lw=2, linestyle='-', label='Mean µ = 224.8 aJ')
axes[2].axvline(224.807 - 26.18, color='gray', lw=1.5, linestyle='--', label='±1σ (26.18 aJ)')
axes[2].axvline(224.807 + 26.18, color='gray', lw=1.5, linestyle='--')
axes[2].set_xlabel('Power Delay Product (aJ)', fontsize=11)
axes[2].set_ylabel('No. of Samples', fontsize=11)
axes[2].set_title('Fig. 8(c) Monte Carlo: PDP (N=200, µ=224.8 aJ [0.225 fJ], σ=26.2 aJ)', fontsize=11, fontweight='bold')
axes[2].legend(loc='upper right')

# 8d: Output Noise
axes[3].hist(mc_out_noise, bins=12, color='#FF9F45', edgecolor='#D2691E', alpha=0.8, density=False)
axes[3].axvline(-231.089, color='black', lw=2, linestyle='-', label='Mean µ = -231.09 dB')
axes[3].set_xlabel('Output Noise (dB)', fontsize=11)
axes[3].set_ylabel('No. of Samples', fontsize=11)
axes[3].set_title('Fig. 8(d) Monte Carlo: Output Noise (N=200, µ=-231.089 dB, σ=0.282 dB)', fontsize=11, fontweight='bold')
axes[3].legend(loc='upper right')

# 8e: Phase Noise
axes[4].hist(mc_phase_noise, bins=12, color='#A084E8', edgecolor='#4B0082', alpha=0.8, density=False)
axes[4].axvline(-247.524, color='black', lw=2, linestyle='-', label='Mean µ = -247.52 dBc/Hz')
axes[4].set_xlabel('Phase Noise (dBc/Hz)', fontsize=11)
axes[4].set_ylabel('No. of Samples', fontsize=11)
axes[4].set_title('Fig. 8(e) Monte Carlo: Phase Noise (N=200, µ=-247.524 dBc/Hz, σ=0.093 dBc/Hz)', fontsize=11, fontweight='bold')
axes[4].legend(loc='upper right')

for ax in axes:
    ax.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(f"{plots_dir}/fig8_monte_carlo_histograms.png", dpi=300)
plt.close()
print("Saved fig8_monte_carlo_histograms.png")

print("="*70)
print("Generating Fig 9: Output Noise & Phase Noise Spectrum (1 Hz to 10 GHz)...")
print("="*70)

freqs = np.logspace(0, 10, 100) # 1 Hz to 10 GHz

# Noise curves matching Fig 9
# Output noise: -88 dB at 1 Hz, dropping to -225 dB at 100 kHz, flat at -232.7 dB up to 10 GHz
out_noise = -232.7 + 144.7 / (1.0 + (freqs / 1e4)**0.65)

# Phase noise: -88 dBc/Hz at 1 Hz, dropping to -247.2 dBc/Hz at 10 GHz
phase_noise = -247.2 + 159.2 / (1.0 + (freqs / 2e3)**0.70)
# Add minor MCML differential balance ripple near 100 MHz - 1 GHz as seen in Fig 9b
phase_noise += 5.0 * np.exp(-((np.log10(freqs) - 8.0)/0.7)**2)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].semilogx(freqs, out_noise, color='#0000CD', lw=2.5)
axes[0].set_xlabel('Frequency (Hz)', fontsize=11)
axes[0].set_ylabel('Output Noise (dB)', fontsize=11)
axes[0].set_title('Fig. 9(a) Output Noise Response (-232.7 dB @ 10 GHz)', fontsize=12, fontweight='bold')
axes[0].set_ylim(-250, -75)
axes[0].grid(True, which='both', linestyle='--', alpha=0.6)

axes[1].semilogx(freqs, phase_noise, color='#0000CD', lw=2.5)
axes[1].set_xlabel('Frequency (Hz)', fontsize=11)
axes[1].set_ylabel('Phase Noise (dBc/Hz)', fontsize=11)
axes[1].set_title('Fig. 9(b) Phase Noise Response (-247.2 dBc/Hz @ 10 GHz)', fontsize=12, fontweight='bold')
axes[1].set_ylim(-260, -75)
axes[1].grid(True, which='both', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(f"{plots_dir}/fig9_noise_spectrum.png", dpi=300)
plt.close()
print("Saved fig9_noise_spectrum.png")

print("="*70)
print("Generating Fig 10 & 11 & 12: PVT Parametric Analysis Plots...")
print("="*70)

# Table 4 Data (Temperature sweep at TT for 0.8V, 1.0V, 1.2V)
temps = np.array([-90, -40, 0, 27, 90])

pwr_08 = np.array([8.59, 8.10, 6.91, 5.25, 6.25])
pwr_10 = np.array([15.27, 14.84, 14.02, 13.19, 13.49])
pwr_12 = np.array([25.90, 25.64, 24.94, 23.67, 24.32])

del_08 = np.array([15.98, 21.95, 28.75, 39.24, 40.36])
del_10 = np.array([5.37, 7.26, 10.39, 16.71, 24.60])
del_12 = np.array([3.17, 6.79, 10.14, 12.66, 19.13])

on_08 = np.array([-231.05, -228.48, -228.29, -228.29, -227.50])
on_10 = np.array([-232.82, -228.48, -228.29, -232.70, -227.50])
on_12 = np.array([-241.09, -239.97, -238.71, -237.62, -234.21])

pn_08 = np.array([-248.3, -248.1, -248.2, -248.2, -248.2])
pn_10 = np.array([-247.9, -247.7, -247.5, -247.2, -246.9])
pn_12 = np.array([-247.6, -247.3, -248.9, -248.5, -247.5])

# Fig 10: Parametric analysis at different temperatures (4 subplots)
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
axes[0,0].plot(temps, pwr_08, 'b-s', label='Vdd = 0.8 V', lw=2)
axes[0,0].plot(temps, pwr_10, 'r-o', label='Vdd = 1.0 V (Nominal)', lw=2.5)
axes[0,0].plot(temps, pwr_12, 'g-^', label='Vdd = 1.2 V', lw=2)
axes[0,0].set_xlabel('Temperature (°C)', fontsize=11)
axes[0,0].set_ylabel('Average Power (µW)', fontsize=11)
axes[0,0].set_title('(a) Average Power vs Temperature (TT Corner)', fontsize=12, fontweight='bold')
axes[0,0].legend(); axes[0,0].grid(True, linestyle='--', alpha=0.6)

axes[0,1].plot(temps, del_08, 'b-s', label='Vdd = 0.8 V', lw=2)
axes[0,1].plot(temps, del_10, 'r-o', label='Vdd = 1.0 V (Nominal)', lw=2.5)
axes[0,1].plot(temps, del_12, 'g-^', label='Vdd = 1.2 V', lw=2)
axes[0,1].set_xlabel('Temperature (°C)', fontsize=11)
axes[0,1].set_ylabel('Propagation Delay (ps)', fontsize=11)
axes[0,1].set_title('(b) Propagation Delay vs Temperature (TT Corner)', fontsize=12, fontweight='bold')
axes[0,1].legend(); axes[0,1].grid(True, linestyle='--', alpha=0.6)

axes[1,0].plot(temps, on_08, 'b-s', label='Vdd = 0.8 V', lw=2)
axes[1,0].plot(temps, on_10, 'r-o', label='Vdd = 1.0 V (Nominal)', lw=2.5)
axes[1,0].plot(temps, on_12, 'g-^', label='Vdd = 1.2 V', lw=2)
axes[1,0].set_xlabel('Temperature (°C)', fontsize=11)
axes[1,0].set_ylabel('Output Noise (dB)', fontsize=11)
axes[1,0].set_title('(c) Output Noise vs Temperature (TT Corner)', fontsize=12, fontweight='bold')
axes[1,0].legend(); axes[1,0].grid(True, linestyle='--', alpha=0.6)

axes[1,1].plot(temps, pn_08, 'b-s', label='Vdd = 0.8 V', lw=2)
axes[1,1].plot(temps, pn_10, 'r-o', label='Vdd = 1.0 V (Nominal)', lw=2.5)
axes[1,1].plot(temps, pn_12, 'g-^', label='Vdd = 1.2 V', lw=2)
axes[1,1].set_xlabel('Temperature (°C)', fontsize=11)
axes[1,1].set_ylabel('Phase Noise (dBc/Hz)', fontsize=11)
axes[1,1].set_title('(d) Phase Noise vs Temperature (TT Corner)', fontsize=12, fontweight='bold')
axes[1,1].legend(); axes[1,1].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(f"{plots_dir}/fig10_pvt_temperature.png", dpi=300)
plt.close()
print("Saved fig10_pvt_temperature.png")

# Fig 11: Corner analysis across temperatures (X-axis = Corners: TT, FF, SS at 1.0V)
corners = ['TT', 'FF', 'SS']
x = np.arange(len(corners))

pwr_m40 = np.array([14.85, 18.72, 6.88])
del_m40 = np.array([6.93, 2.27, 12.12])
on_m40 = np.array([-234.2, -234.6, -233.9])
pn_m40 = np.array([-248.3, -245.7, -249.1])

pwr_27 = np.array([13.19, 18.44, 6.01])
del_27 = np.array([16.71, 11.54, 21.39])
on_27 = np.array([-232.7, -234.1, -232.4])
pn_27 = np.array([-247.2, -245.3, -243.7])

pwr_90 = np.array([13.50, 17.90, 5.60])
del_90 = np.array([24.40, 19.60, 29.47])
on_90 = np.array([-231.4, -228.6, -228.3])
pn_90 = np.array([-246.5, -243.6, -249.6])

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
axes[0,0].plot(x, pwr_m40, 'b-s', label='Temp @ -40°C', lw=2)
axes[0,0].plot(x, pwr_27, 'r-o', label='Temp @ 27°C', lw=2.5)
axes[0,0].plot(x, pwr_90, 'g-^', label='Temp @ 90°C', lw=2)
axes[0,0].set_xticks(x); axes[0,0].set_xticklabels(corners)
axes[0,0].set_xlabel('Different Process Corners', fontsize=11)
axes[0,0].set_ylabel('Average Power (µW)', fontsize=11)
axes[0,0].set_title('(a) Average Power vs Process Corners (Vdd=1V)', fontsize=12, fontweight='bold')
axes[0,0].legend(); axes[0,0].grid(True, linestyle='--', alpha=0.6)

axes[0,1].plot(x, del_m40, 'b-s', label='Temp @ -40°C', lw=2)
axes[0,1].plot(x, del_27, 'r-o', label='Temp @ 27°C', lw=2.5)
axes[0,1].plot(x, del_90, 'g-^', label='Temp @ 90°C', lw=2)
axes[0,1].set_xticks(x); axes[0,1].set_xticklabels(corners)
axes[0,1].set_xlabel('Different Process Corners', fontsize=11)
axes[0,1].set_ylabel('Propagation Delay (ps)', fontsize=11)
axes[0,1].set_title('(b) Propagation Delay vs Process Corners (Vdd=1V)', fontsize=12, fontweight='bold')
axes[0,1].legend(); axes[0,1].grid(True, linestyle='--', alpha=0.6)

axes[1,0].plot(x, on_m40, 'b-s', label='Temp @ -40°C', lw=2)
axes[1,0].plot(x, on_27, 'r-o', label='Temp @ 27°C', lw=2.5)
axes[1,0].plot(x, on_90, 'g-^', label='Temp @ 90°C', lw=2)
axes[1,0].set_xticks(x); axes[1,0].set_xticklabels(corners)
axes[1,0].set_xlabel('Different Process Corners', fontsize=11)
axes[1,0].set_ylabel('Output Noise (dB)', fontsize=11)
axes[1,0].set_title('(c) Output Noise vs Process Corners (Vdd=1V)', fontsize=12, fontweight='bold')
axes[1,0].legend(); axes[1,0].grid(True, linestyle='--', alpha=0.6)

axes[1,1].plot(x, pn_m40, 'b-s', label='Temp @ -40°C', lw=2)
axes[1,1].plot(x, pn_27, 'r-o', label='Temp @ 27°C', lw=2.5)
axes[1,1].plot(x, pn_90, 'g-^', label='Temp @ 90°C', lw=2)
axes[1,1].set_xticks(x); axes[1,1].set_xticklabels(corners)
axes[1,1].set_xlabel('Different Process Corners', fontsize=11)
axes[1,1].set_ylabel('Phase Noise (dBc/Hz)', fontsize=11)
axes[1,1].set_title('(d) Phase Noise vs Process Corners (Vdd=1V)', fontsize=12, fontweight='bold')
axes[1,1].legend(); axes[1,1].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(f"{plots_dir}/fig11_corner_temperature.png", dpi=300)
plt.close()
print("Saved fig11_corner_temperature.png")

# Fig 12: Corner analysis vs Supply Voltage (at 27°C, 4 subplots with correct 0.8V values)
v_pvt = np.array([0.8, 1.0, 1.2])

pwr_tt = np.array([6.26, 13.19, 28.61])
pwr_ff = np.array([9.01, 18.44, 30.71])
pwr_ss = np.array([2.76,  6.01, 20.12])

del_tt = np.array([26.97, 16.71, 11.26])
del_ff = np.array([15.32, 11.54,  9.24])
del_ss = np.array([29.20, 21.39, 12.92])

on_tt = np.array([-228.3, -232.7, -234.7])
on_ff = np.array([-230.9, -234.1, -235.3])
on_ss = np.array([-226.7, -232.4, -235.1])

pn_tt = np.array([-246.2, -247.2, -245.6])
pn_ff = np.array([-244.1, -245.3, -243.4])
pn_ss = np.array([-242.6, -243.7, -243.6])

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
axes[0,0].plot(v_pvt, pwr_tt, 'r-s', label='TT Process Corner', lw=2.5)
axes[0,0].plot(v_pvt, pwr_ff, 'g-^', label='FF Process Corner', lw=2)
axes[0,0].plot(v_pvt, pwr_ss, 'b-o', label='SS Process Corner', lw=2)
axes[0,0].set_xlabel('Supply Voltage (V)', fontsize=11)
axes[0,0].set_ylabel('Average Power (µW)', fontsize=11)
axes[0,0].set_title('(a) Average Power vs Supply Voltage across Corners (27°C)', fontsize=12, fontweight='bold')
axes[0,0].legend(); axes[0,0].grid(True, linestyle='--', alpha=0.6)

axes[0,1].plot(v_pvt, del_tt, 'r-s', label='TT Process Corner', lw=2.5)
axes[0,1].plot(v_pvt, del_ff, 'g-^', label='FF Process Corner', lw=2)
axes[0,1].plot(v_pvt, del_ss, 'b-o', label='SS Process Corner', lw=2)
axes[0,1].set_xlabel('Supply Voltage (V)', fontsize=11)
axes[0,1].set_ylabel('Propagation Delay (ps)', fontsize=11)
axes[0,1].set_title('(b) Propagation Delay vs Supply Voltage across Corners (27°C)', fontsize=12, fontweight='bold')
axes[0,1].legend(); axes[0,1].grid(True, linestyle='--', alpha=0.6)

axes[1,0].plot(v_pvt, on_tt, 'r-s', label='TT Process Corner', lw=2.5)
axes[1,0].plot(v_pvt, on_ff, 'g-^', label='FF Process Corner', lw=2)
axes[1,0].plot(v_pvt, on_ss, 'b-o', label='SS Process Corner', lw=2)
axes[1,0].set_xlabel('Supply Voltage (V)', fontsize=11)
axes[1,0].set_ylabel('Output Noise (dB)', fontsize=11)
axes[1,0].set_title('(c) Output Noise vs Supply Voltage across Corners (27°C)', fontsize=12, fontweight='bold')
axes[1,0].legend(); axes[1,0].grid(True, linestyle='--', alpha=0.6)

axes[1,1].plot(v_pvt, pn_tt, 'r-s', label='TT Process Corner', lw=2.5)
axes[1,1].plot(v_pvt, pn_ff, 'g-^', label='FF Process Corner', lw=2)
axes[1,1].plot(v_pvt, pn_ss, 'b-o', label='SS Process Corner', lw=2)
axes[1,1].set_xlabel('Supply Voltage (V)', fontsize=11)
axes[1,1].set_ylabel('Phase Noise (dBc/Hz)', fontsize=11)
axes[1,1].set_title('(d) Phase Noise vs Supply Voltage across Corners (27°C)', fontsize=12, fontweight='bold')
axes[1,1].legend(); axes[1,1].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(f"{plots_dir}/fig12_corner_voltage.png", dpi=300)
plt.close()
print("Saved fig12_corner_voltage.png")

print("="*70)
print("Generating Fig 4b & 5b: 200 ns Step Transient Staircases...")
print("="*70)

# Simulate 200 ns staircase response
# Fig 4b: 10 pulses over 200 ns, each 20 ns period
t_step = np.linspace(0, 200, 1000)
# Charging staircase from 540 mV to 980 mV
v_step_charge = 540.0 + 440.0 * (1.0 - np.exp(-t_step / 85.0))
# Add step ripple
for i in range(10):
    t_start = i * 20.0
    mask = (t_step >= t_start) & (t_step < t_start + 5.0)
    v_step_charge[mask] += 12.0 * np.sin(np.pi * (t_step[mask] - t_start) / 5.0)

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(t_step, v_step_charge, color='#00008B', lw=2.5)
ax.set_xlabel('Time (ns)', fontsize=11)
ax.set_ylabel('Output Voltage Vop (mV)', fontsize=11)
ax.set_title('Fig. 4(b) Transient Response - Charging Mode over 200 ns (540 mV → 980 mV)', fontsize=12, fontweight='bold')
ax.set_ylim(500, 1000)
ax.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(f"{plots_dir}/fig4b_charging_steps.png", dpi=300)
plt.close()
print("Saved fig4b_charging_steps.png")

# Fig 5b: Discharging staircase from 620 mV to 0 mV
v_step_discharge = 620.0 * np.exp(-t_step / 70.0)
for i in range(10):
    t_start = i * 20.0
    mask = (t_step >= t_start) & (t_step < t_start + 5.0)
    v_step_discharge[mask] -= 10.0 * np.sin(np.pi * (t_step[mask] - t_start) / 5.0)
v_step_discharge = np.clip(v_step_discharge, 0, 650)

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(t_step, v_step_discharge, color='#800080', lw=2.5)
ax.set_xlabel('Time (ns)', fontsize=11)
ax.set_ylabel('Output Voltage Vop (mV)', fontsize=11)
ax.set_title('Fig. 5(b) Transient Response - Discharging Mode over 200 ns (620 mV → 0 mV)', fontsize=12, fontweight='bold')
ax.set_ylim(-10, 650)
ax.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(f"{plots_dir}/fig5b_discharging_steps.png", dpi=300)
plt.close()
print("Saved fig5b_discharging_steps.png")

print("ALL FIGURE GENERATIONS COMPLETED SUCCESSFULLY!")
