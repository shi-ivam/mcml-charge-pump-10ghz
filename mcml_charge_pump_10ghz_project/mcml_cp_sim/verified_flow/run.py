#!/usr/bin/env python3
"""Run measured ngspice results from the current Virtuoso DUT netlist."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
NETLIST = Path.home() / "simulation/tb_mcml_charge_pump/spectre/schematic/netlist/input.scs"
TB_OA = PROJECT / "cadence_work/shivam/tb_mcml_charge_pump/schematic/sch.oa"
PDK = Path(os.environ.get("FREEPDK45_MODELS", "/home/shivam/cadence/pdk/FreePDK45/ncsu_basekit/models/hspice/tran_models/models_nom"))
MODELS = [PDK / "NMOS_VTG.inc", PDK / "PMOS_VTG.inc"]
OUT = HERE / "results"


def fail(message: str) -> None:
    raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(text: str) -> float:
    unit = text[-1].lower()
    factors = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3}
    return float(text[:-1]) * factors[unit] if unit in factors else float(text)


def logical_lines(text: str) -> list[str]:
    lines = []
    current = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if line.endswith("\\"):
            current += line[:-1].strip() + " "
        else:
            lines.append(current + line)
            current = ""
    if current:
        fail("Incomplete Spectre continuation in input.scs")
    return lines


def topology() -> tuple[list[str], str]:
    if not NETLIST.is_file() or not TB_OA.is_file():
        fail("Virtuoso testbench netlist is missing. Run test_netlist_tb.ocn first; see GUIDE.md.")
    if NETLIST.stat().st_mtime < TB_OA.stat().st_mtime:
        fail("Virtuoso testbench changed after netlisting. Regenerate input.scs first.")
    text = NETLIST.read_text()
    if "// Design cell name: tb_mcml_charge_pump" not in text:
        fail("This is not the tb_mcml_charge_pump netlist.")
    lines = logical_lines(text)
    in_dut = False
    devices = []
    sources = {}
    for line in lines:
        if line.startswith("subckt mcml_charge_pump "):
            in_dut = True
            continue
        if line == "ends mcml_charge_pump":
            in_dut = False
            continue
        if in_dut:
            mos = re.match(r"^(\w+)\s+\(([^)]+)\)\s+(gpdk045_[np]mos1v)\s+(.+)$", line)
            cap = re.match(r"^(\w+)\s+\(([^)]+)\)\s+capacitor\s+c=([^\s]+)", line)
            if mos:
                name, nodes, model, params = mos.groups()
                geometry = dict(re.findall(r"\b(\w+)=\(?([^\s)]+)\)?", params))
                expected_geometry = {"w", "l", "nf", "as", "ad", "ps", "pd", "nrd", "nrs", "sa", "sb", "sd", "m"}
                if set(geometry) != expected_geometry:
                    fail(f"Unexpected MOS geometry on {name}: {sorted(set(geometry) ^ expected_geometry)}")
                mapped = "NMOS_VTG" if "nmos" in model else "PMOS_VTG"
                ns = ["0" if n == "Gnd" else n for n in nodes.split()]
                options = " ".join(f"{key.upper()}={geometry[key]}" for key in ("w", "l", "nf", "as", "ad", "ps", "pd", "nrd", "nrs", "sa", "sb", "sd", "m"))
                devices.append(f"M_{name} {' '.join(ns)} {mapped} {options}")
            elif cap:
                name, nodes, value = cap.groups()
                ns = ["0" if n == "Gnd" else n for n in nodes.split()]
                devices.append(f"C_{name} {' '.join(ns)} {value}")
            else:
                fail(f"Unrecognized DUT element; update and review the converter: {line}")
        else:
            if line.startswith("V_"):
                sources[line.split()[0]] = line
    if len([d for d in devices if d.startswith("M_")]) != 13:
        fail("Expected 13 DUT MOSFETs in the generated Virtuoso netlist.")
    if len([d for d in devices if d.startswith("C_")]) != 2:
        fail("Expected exactly the internal CL and Ci capacitors.")
    if not any(d.startswith("M_M5 n_tail Vbias 0 0 NMOS_VTG W=480n L=45n ") for d in devices):
        fail("Vbias is not connected to the 480 nm / 45 nm M5 tail-device gate.")
    if not any(d.startswith("C_CL ") and np.isclose(number(d.split()[-1]), 300e-15, rtol=1e-12) for d in devices):
        fail("Internal CL is not 300 fF.")
    if not any(d.startswith("C_Ci ") and np.isclose(number(d.split()[-1]), 50e-15, rtol=1e-12) for d in devices):
        fail("Internal Ci is not 50 fF.")
    if "DUT0 (DN DN_b 0 UP UP_b Vbias Vdd Vop) mcml_charge_pump" not in lines:
        fail("Unexpected DUT pin order, output net, or ground connection.")
    common = {
        "V_VDD": r"\(Vdd 0\) vsource dc=1(?:\.0)? type=dc",
        "V_BIAS": r"\(Vbias 0\) vsource dc=0\.45 type=dc",
    }
    pulses = {
        "UP": r"\(UP 0\) vsource type=pulse val0=0 val1=1(?:\.0)?.*period=100p delay=0 rise=5p fall=5p width=25p",
        "UP_b": r"\(UP_b 0\) vsource type=pulse val0=1(?:\.0)? val1=0.*period=100p delay=0 rise=5p fall=5p width=25p",
        "DN": r"\(DN 0\) vsource type=pulse val0=0 val1=1(?:\.0)?.*period=100p delay=0 rise=5p fall=5p width=25p",
        "DN_b": r"\(DN_b 0\) vsource type=pulse val0=1(?:\.0)? val1=0.*period=100p delay=0 rise=5p fall=5p width=25p",
    }
    dc = {
        "UP": r"\(UP 0\) vsource dc=0 type=dc",
        "UP_b": r"\(UP_b 0\) vsource dc=1(?:\.0)? type=dc",
        "DN": r"\(DN 0\) vsource dc=0 type=dc",
        "DN_b": r"\(DN_b 0\) vsource dc=1(?:\.0)? type=dc",
    }
    mode = "charge" if "type=pulse" in sources.get("V_UP", "") else "discharge"
    expected = dict(common)
    for pin in ("UP", "UP_b", "DN", "DN_b"):
        expected["V_" + pin.upper()] = pulses[pin] if (pin.startswith("UP") and mode == "charge") or (pin.startswith("DN") and mode == "discharge") else dc[pin]
    for name, pattern in expected.items():
        if not re.search(pattern, sources.get(name, "")):
            fail(f"Unexpected or missing Virtuoso source {name}: {sources.get(name, '<absent>')}")
    if set(sources) != set(expected):
        fail(f"Unexpected extra voltage source(s): {sorted(set(sources)-set(expected))}")
    return devices, mode


def deck(devices: list[str], mode: str, duration: str | None = None) -> str:
    header = [
        f"* Verified {mode} from Virtuoso shivam/tb_mcml_charge_pump",
        "* FreePDK45 nominal VTG replaces simplified gpdk045 Spectre models.",
        *(f'.include "{m}"' for m in MODELS),
        "V_VDD Vdd 0 DC 1.0",
        "V_BIAS Vbias 0 DC 0.45",
    ]
    if mode == "charge":
        controls = [
            "V_UP UP 0 PULSE(0 1 0 5p 5p 25p 100p)",
            "V_UP_B UP_b 0 PULSE(1 0 0 5p 5p 25p 100p)",
            "V_DN DN 0 DC 0",
            "V_DN_B DN_b 0 DC 1",
        ]
        ic = ".ic V(Vop)=0.54"
    elif mode == "discharge":
        controls = [
            "V_UP UP 0 DC 0",
            "V_UP_B UP_b 0 DC 1",
            "V_DN DN 0 PULSE(0 1 0 5p 5p 25p 100p)",
            "V_DN_B DN_b 0 PULSE(1 0 0 5p 5p 25p 100p)",
        ]
        ic = ".ic V(Vop)=0.62"
    elif mode in ("charge_dc", "discharge_dc"):
        if mode == "charge_dc":
            controls = ["V_UP UP 0 DC 1", "V_UP_B UP_b 0 DC 0", "V_DN DN 0 DC 0", "V_DN_B DN_b 0 DC 1"]
        else:
            controls = ["V_UP UP 0 DC 0", "V_UP_B UP_b 0 DC 1", "V_DN DN 0 DC 1", "V_DN_B DN_b 0 DC 0"]
        controls.append("V_FORCE Vop 0 DC 0.5")
        ic = ""
    else:
        fail(f"Unknown mode {mode}")
    body = header + controls + devices + ([ic] if ic else []) + [
        ".options reltol=1e-3 vabstol=1e-6 iabstol=1e-12",
        ".temp 27",
    ]
    if duration:
        body += [
            f".tran 0.5p {duration} 0 0.5p",
            ".save V(Vop) V(UP) V(UP_b) V(DN) V(DN_b) V(n_tail) V(Vdd) V(Vbias) I(V_VDD)",
            ".control",
            "set wr_singlescale",
            "set wr_vecnames",
            "run",
            f"wrdata {mode}_{duration}.dat v(vop) v(up) v(up_b) v(dn) v(dn_b) v(n_tail) v(vdd) v(vbias) i(V_VDD)",
            "quit",
            ".endc",
        ]
    else:
        body += [
            ".dc V_FORCE 0 1 0.01",
            ".save I(V_FORCE)",
            ".control",
            "set wr_singlescale",
            "set wr_vecnames",
            "run",
            f"wrdata {mode}.dat i(V_FORCE)",
            "quit",
            ".endc",
        ]
    return "\n".join(body + [".end", ""])


def run_case(devices: list[str], mode: str, duration: str | None = None) -> np.ndarray:
    stem = f"{mode}_{duration}" if duration else mode
    circuit = OUT / f"{stem}.cir"
    circuit.write_text(deck(devices, mode, duration))
    result = subprocess.run(["ngspice", "-b", circuit.name], cwd=OUT, capture_output=True, text=True)
    (OUT / f"{stem}.log").write_text(result.stdout + result.stderr)
    if result.returncode or "No. of Data Rows" not in result.stdout or re.search(r"(^|\n)(Error|Warning):", result.stdout + result.stderr, re.I):
        fail(f"ngspice did not complete cleanly; inspect {stem}.log")
    data = np.loadtxt(OUT / f"{stem}.dat", skiprows=1)
    if data.ndim != 2 or data.shape[0] < 10:
        fail(f"Insufficient data from {stem}")
    return data


def interpolate(time: np.ndarray, values: np.ndarray, at: float) -> float:
    return float(np.interp(at, time, values))


def crossings(time: np.ndarray, values: np.ndarray, threshold: float, rising: bool) -> list[float]:
    a, b = values[:-1], values[1:]
    idx = np.flatnonzero((a < threshold) & (b >= threshold) if rising else (a > threshold) & (b <= threshold))
    return [float(time[i] + (threshold - a[i]) * (time[i+1] - time[i]) / (b[i] - a[i])) for i in idx if b[i] != a[i]]


def delays(data: np.ndarray, mode: str) -> dict:
    t = data[:, 0]
    output = data[:, 1]
    control = data[:, 2 if mode == "charge" else 4]
    edges = crossings(t, control, 0.5, True)
    if len(edges) < 20:
        return {"valid": False, "reason": "Fewer than 20 input pulses"}
    rows = []
    for n in range(11, 21):
        ti = edges[n-1]
        before = interpolate(t, output, ti - 10e-12)
        after = interpolate(t, output, ti + 40e-12)
        mid = (before + after) / 2
        local = (t >= ti) & (t <= ti + 40e-12)
        tc = crossings(t[local], output[local], mid, mode == "charge")
        if abs(after-before) < 1e-5 or len(tc) != 1 or tc[0] < ti:
            return {"valid": False, "reason": f"No unique local output crossing for pulse {n}", "samples": rows}
        rows.append({"pulse": n, "input_s": ti, "output_s": tc[0], "delay_ps": (tc[0]-ti)*1e12, "before_v": before, "after_v": after})
    return {"valid": True, "mean_ps": float(np.mean([r["delay_ps"] for r in rows])), "samples": rows}


def average_power(data: np.ndarray) -> dict:
    t, vdd, branch = data[:, 0], data[:, 7], data[:, 9]
    t1, t2 = 1e-9, 10e-9
    inside = (t > t1) & (t < t2)
    ti = np.r_[t1, t[inside], t2]
    power = -np.interp(ti, t, vdd) * np.interp(ti, t, branch)
    value = float(np.trapezoid(power, ti) / (t2-t1))
    return {"power_w": value, "power_uw": value*1e6, "window_s": [t1, t2], "mean_vdd_current_a": float(np.trapezoid(-np.interp(ti, t, branch), ti)/(t2-t1))}


def quiet_samples(data: np.ndarray, mode: str) -> dict:
    t, output = data[:, 0], data[:, 1]
    control = data[:, 2 if mode == "charge" else 4]
    edges = crossings(t, control, 0.5, True)
    if len(edges) < 5:
        return {"settled": False, "reason": "Fewer than five pulses"}
    samples = [interpolate(t, output, edge - 5e-12) for edge in edges[-5:]]
    delta = abs(samples[-1] - samples[0])
    return {"settled": delta <= 1e-5, "settling_tolerance_v": 1e-5, "samples_v": samples, "first_to_last_v": delta, "mean_v": float(np.mean(samples)), "stop_s": float(t[-1])}


def dynamic_range(charge: np.ndarray, discharge: np.ndarray) -> dict:
    voltage = charge[:, 0]
    if charge.shape != discharge.shape or not np.allclose(voltage, discharge[:, 0], atol=1e-12):
        fail("Charge and discharge DC sweep grids differ.")
    up, dn = charge[:, 1], -discharge[:, 1]
    ref = int(np.argmin(abs(voltage - 0.5)))
    if abs(voltage[ref]-0.5) > 1e-9 or up[ref] <= 0 or dn[ref] <= 0:
        return {"valid": False, "reason": "Reference current at 0.5 V is not positive in both modes", "charge_ref_a": float(up[ref]), "discharge_ref_a": float(dn[ref])}
    charge_error = 100 * abs(up-up[ref])/up[ref]
    discharge_error = 100 * abs(dn-dn[ref])/dn[ref]
    mismatch = np.where(up+dn > 0, 200*abs(up-dn)/(up+dn), np.inf)
    passing = (charge_error <= 10) & (discharge_error <= 10) & (mismatch <= 10)
    result = {
        "valid": bool(passing[ref]),
        "charge_ref_a": float(up[ref]),
        "discharge_ref_a": float(dn[ref]),
        "reference_errors_pct": [float(charge_error[ref]), float(discharge_error[ref]), float(mismatch[ref])],
        "criterion": "charge/discharge current variation <=10% of 0.5 V reference and UP/DN mismatch <=10%",
        "sweep_step_v": 0.01,
    }
    if passing[ref]:
        lo = hi = ref
        while lo > 0 and passing[lo-1]: lo -= 1
        while hi < len(voltage)-1 and passing[hi+1]: hi += 1
        result.update({"low_v": float(voltage[lo]), "high_v": float(voltage[hi]), "width_v": float(voltage[hi]-voltage[lo])})
    else:
        result["reason"] = "10% criterion fails at the 0.5 V reference"
    np.savetxt(OUT / "dc_compliance.csv", np.c_[voltage, up, dn, charge_error, discharge_error, mismatch, passing.astype(int)], delimiter=",", header="vop_v,i_charge_a,i_discharge_a,charge_error_pct,discharge_error_pct,mismatch_pct,passes", comments="")
    return result


def make_plots(charge: np.ndarray, discharge: np.ndarray, dc_ch: np.ndarray, dc_dn: np.ndarray, metrics: dict) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), constrained_layout=True)
    for data, label, color in ((charge, "charging", "#146f8b"), (discharge, "discharging", "#c45c3a")):
        axes[0].plot(data[:,0]*1e9, data[:,1], label=label, color=color)
    axes[0].set(xlabel="Time (ns)", ylabel="Vop (V)", title="Virtuoso DUT topology simulated by ngspice")
    axes[0].legend(frameon=False)
    for data, mode, color in ((charge, "UP", "#146f8b"), (discharge, "DN", "#c45c3a")):
        axes[1].plot(data[:,0]*1e9, -data[:,7]*data[:,9]*1e6, label=f"{mode} supply power", color=color, lw=0.9)
    axes[1].set(xlim=(1,2), xlabel="Time (ns)", ylabel="Power from VDD (µW)")
    axes[1].legend(frameon=False)
    axes[2].plot(dc_ch[:,0], dc_ch[:,1]*1e6, label="charge current", color="#146f8b")
    axes[2].plot(dc_dn[:,0], -dc_dn[:,1]*1e6, label="discharge current", color="#c45c3a")
    if metrics["dynamic_range"].get("valid"):
        axes[2].axvspan(metrics["dynamic_range"]["low_v"], metrics["dynamic_range"]["high_v"], color="green", alpha=.1, label="10% compliance interval")
    axes[2].set(xlabel="Forced Vop (V)", ylabel="Current (µA)", title="DC current compliance")
    axes[2].legend(frameon=False)
    for ax in axes: ax.grid(alpha=.25)
    fig.suptitle("Measured ngspice 45.2 results • FreePDK45 VTG models • 1.0 V, 27 °C")
    fig.savefig(OUT / "verified_results.png", dpi=170)
    plt.close(fig)


def write_viva_import(charge: np.ndarray, discharge: np.ndarray, metrics: dict) -> None:
    """Generate ViVA display code from actual numeric results, with clear provenance."""
    path = OUT / "show_verified_ngspice.il"
    lines = [
        "; Generated from measured ngspice data. Display only; no Spectre run is implied.",
        "; Full-resolution measurements and simulator logs remain beside this file.",
        'printf("\\nIMPORTED ngspice 45.2 / FreePDK45 results from Virtuoso netlist\\n")',
        f'printf("Netlist SHA256: {metrics["provenance"]["virtuoso_netlist_sha256"]}\\n")',
        "newWindow()",
        "displayMode('strip)",
        'let((rows n x y ctl watts k w)',
    ]
    for label, data, control_col in (("charging", charge, 2), ("discharging", discharge, 4)):
        sampled = data[::4]
        if sampled[-1, 0] != data[-1, 0]:
            sampled = np.vstack([sampled, data[-1]])
        lines.append(f'  ; {label}: time in seconds, Vop in volts, active control in volts, VDD power in watts')
        lines.append("  rows = list(")
        for row in sampled:
            t, vop, ctl, power = row[0], row[1], row[control_col], -row[7]*row[9]
            lines.append(f"    list({t:.10g} {vop:.10g} {ctl:.10g} {power:.10g})")
        lines += [
            "  )",
            "  n = length(rows)",
            "  x = drCreateVec('double n)",
            "  y = drCreateVec('double n)",
            "  ctl = drCreateVec('double n)",
            "  watts = drCreateVec('double n)",
            "  k = 0",
            "  foreach(row rows",
            "    drSetElem(x k car(row))",
            "    drSetElem(y k cadr(row))",
            "    drSetElem(ctl k caddr(row))",
            "    drSetElem(watts k cadddr(row))",
            "    k = k + 1",
            "  )",
            f'  printf("{label}: %d measured points plotted (display decimated 4:1)\\n" n)',
            f'  plot(drCreateWaveform(x y) ?expr list("ngspice imported: {label} Vop (V)"))',
            f'  plot(drCreateWaveform(x ctl) ?expr list("ngspice imported: {label} control (V)"))',
            f'  plot(drCreateWaveform(x watts) ?expr list("ngspice imported: {label} VDD power (W)"))',
        ]
    lines += [
        ")",
        f'printf("Charge delay: {metrics["charging"]["delay"]["mean_ps"]:.4f} ps; discharge delay: {metrics["discharging"]["delay"]["mean_ps"]:.4f} ps\\n")',
        f'printf("Charge power: {metrics["charging"]["power"]["power_uw"]:.4f} uW; discharge power: {metrics["discharging"]["power"]["power_uw"]:.4f} uW\\n")',
        f'printf("10%% current-compliance dynamic range valid: {"YES" if metrics["dynamic_range"]["valid"] else "NO"}\\n")',
    ]
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    for p in MODELS:
        if not p.is_file(): fail(f"Missing model file: {p}")
    OUT.mkdir(exist_ok=True)
    devices, source_mode = topology()
    charge = run_case(devices, "charge", "10ns")
    discharge = run_case(devices, "discharge", "10ns")
    dc_ch = run_case(devices, "charge_dc")
    dc_dn = run_case(devices, "discharge_dc")
    if charge.shape[1] != 10 or discharge.shape[1] != 10 or dc_ch.shape[1] != 2:
        fail("Unexpected ngspice column count; inspect generated data files.")
    metrics = {
        "provenance": {
            "virtuoso_netlist": str(NETLIST),
            "virtuoso_netlist_sha256": digest(NETLIST),
            "models": [{"path": str(p), "sha256": digest(p)} for p in MODELS],
            "simulator": next((line.strip() for line in subprocess.run(["ngspice", "-v"], capture_output=True, text=True).stdout.splitlines() if "ngspice-" in line), "ngspice version unavailable"),
            "model_substitution": "FreePDK45 nominal VTG replaces simplified gpdk045 Spectre models",
            "virtuoso_source_mode": source_mode,
        },
        "charging": {"delay": delays(charge, "charge"), "power": average_power(charge)},
        "discharging": {"delay": delays(discharge, "discharge"), "power": average_power(discharge)},
    }
    dr = dynamic_range(dc_ch, dc_dn)
    metrics["dynamic_range"] = dr
    if metrics["charging"]["delay"].get("valid") and metrics["discharging"]["delay"].get("valid"):
        direction = max(("charging", "discharging"), key=lambda m: metrics[m]["delay"]["mean_ps"])
        metrics["reported_delay"] = {"mode": direction, "ps": metrics[direction]["delay"]["mean_ps"]}
        paper_ps = 16.71
        measured_ps = metrics["reported_delay"]["ps"]
        signed_error_pct = 100 * (measured_ps - paper_ps) / paper_ps
        metrics["paper_delay_comparison"] = {
            "paper_tt_ps": paper_ps,
            "measured_ps": measured_ps,
            "measured_mode": direction,
            "difference_ps": measured_ps - paper_ps,
            "signed_error_pct": signed_error_pct,
            "absolute_error_pct": abs(signed_error_pct),
            "illustrative_10pct_band_ps": [paper_ps * 0.9, paper_ps * 1.1],
            "within_illustrative_10pct_band": abs(signed_error_pct) <= 10,
            "comparability": "Numerical proximity only: paper Table 2 uses 10 pF; this DUT uses 300 fF and FreePDK45 nominal VTG; paper edge extraction is unspecified.",
        }
        metrics["pdp"] = {"mode": direction, "fj": metrics[direction]["power"]["power_uw"] * metrics[direction]["delay"]["mean_ps"] / 1000}
    else:
        metrics["reported_delay"] = {"valid": False, "reason": "At least one directional delay failed local crossing criterion"}
        metrics["pdp"] = {"valid": False, "reason": "A valid worst-direction delay is required"}
    settled = {}
    for duration in ("10ns", "20ns", "40ns", "80ns"):
        if duration != "10ns":
            ch = run_case(devices, "charge", duration)
            dn = run_case(devices, "discharge", duration)
        else:
            ch, dn = charge, discharge
        settled = {"charging": quiet_samples(ch, "charge"), "discharging": quiet_samples(dn, "discharge")}
        if settled["charging"]["settled"] and settled["discharging"]["settled"]:
            settled["output_swing_v"] = settled["charging"]["mean_v"] - settled["discharging"]["mean_v"]
            break
    metrics["output_swing"] = settled
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    make_plots(charge, discharge, dc_ch, dc_dn, metrics)
    write_viva_import(charge, discharge, metrics)
    summary = {
        "charge_delay_ps": metrics["charging"]["delay"].get("mean_ps"),
        "discharge_delay_ps": metrics["discharging"]["delay"].get("mean_ps"),
        "paper_delay_absolute_error_pct": metrics.get("paper_delay_comparison", {}).get("absolute_error_pct"),
        "charge_power_uw": metrics["charging"]["power"]["power_uw"],
        "discharge_power_uw": metrics["discharging"]["power"]["power_uw"],
        "pdp_fj": metrics["pdp"].get("fj"),
        "output_swing_v": metrics["output_swing"].get("output_swing_v"),
        "current_compliance_dynamic_range_valid": metrics["dynamic_range"]["valid"],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
