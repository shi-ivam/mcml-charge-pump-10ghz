# Design and Simulation of a 10 GHz MCML Charge Pump in 45nm CMOS

This repository contains the schematic design, simulation testbenches, verification workflows, and documentation for a high-speed Two-Stage Hybrid MOS Current Mode Logic (MCML) Charge Pump operating at 10 GHz in 45nm bulk CMOS.

The design is based on the reference architecture by M. Sivasakthi & P. Radhika, "A high-speed MCML charge pump design at 10 GHz frequency", Analog Integrated Circuits and Signal Processing (Springer, 2024).

## Key Performance Metrics

| Parameter | Value |
| :--- | :--- |
| Technology | 45nm Bulk CMOS (FreePDK45 / GPDK045) |
| Operating Frequency | 10.0 GHz (Clock Period T = 100 ps, Pulse Width = 25 ps) |
| Supply Voltage | 1.0 V |
| Propagation Delay (t_pd) | 16.71 ps |
| Average Power Dissipation | 13.19 uW |
| Power-Delay Product (PDP) | 0.221 fJ (221 aJ) |
| Output Dynamic Range | 0.0 V to 0.98 V |
| Phase Noise @ 10 GHz | -247.2 dBc/Hz |
| PVT Robustness | Operational across TT, FF, SS, FS, SF corners (-40 deg C to +90 deg C, 0.8 V to 1.2 V) |

## Circuit Schematic

![Cadence Virtuoso Schematic](simulation_screenshots/screenshot_01_cadence_virtuoso_schematic.png)

## Simulation Waveforms

### 10 GHz Charging Transient
![10 GHz Charging Transient](simulation_screenshots/screenshot_02_viva_10ghz_charging_transient.png)

### 10 GHz Discharging Transient
![10 GHz Discharging Transient](simulation_screenshots/screenshot_03_viva_10ghz_discharging_transient.png)

### PVT Process Corners & Temperature Variations
![Process Corner and Temperature Variations](simulation_screenshots/screenshot_06_corner_pvt_variations.png)

## Reports and Documentation

- [Final MCML Charge Pump Mini Project Report (PDF)](Final_MCML_Charge_Pump_Mini_Project_Report.pdf)
- [Final Project Report (PDF)](FINAL_PROJECT_REPORT.pdf)
- [10 GHz MCML Charge Pump Simulation Guide (PDF)](10GHz_MCML_Charge_Pump_Simulation_Guide.pdf)
- [Professor Review Walkthrough (PDF)](PROFESSOR_REVIEW_WALKTHROUGH.pdf)
- [Presentation Evidence and Artifacts](mcml_charge_pump_10ghz_project/presentation_evidence_2026-10-22/Virtuoso_ADE_Calculator_Evidence.pdf)

## Repository Structure

- `mcml_charge_pump_10ghz_project/`: Cadence Virtuoso project directory, schematic views, testbenches, and verification scripts.
- `simulation_screenshots/`: High-resolution captures of Virtuoso schematics and ViVA simulation waveforms.
- `virtuoso_simulation_graphs/`: Output graphs covering transient, corner, Monte Carlo, and noise analysis.
- `Presentation/`: Interactive HTML presentation slides and exports.
- `GUIDE.md`: Reproduction and verification instructions.
