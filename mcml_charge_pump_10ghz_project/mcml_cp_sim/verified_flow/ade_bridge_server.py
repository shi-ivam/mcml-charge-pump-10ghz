#!/usr/bin/env python3
"""Host-side ngspice solver for the local Virtuoso ADE bridge.

Only the checked shivam/tb_mcml_charge_pump netlist is accepted. Results are
labelled ngspice throughout; this service does not impersonate Cadence Spectre.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import socketserver
import subprocess
import sys
import threading
import time
import traceback

import numpy as np
import run

ROOT = Path(__file__).resolve().parent
SOCKET = ROOT / "ade_bridge.sock"
READY = ROOT / "results/ade_popup_ready.il"
VIVA_PSF = {mode: ROOT / "results" / f"viva_psf_{mode}" for mode in ("charge", "discharge")}
SWING_PSF = {mode: ROOT / "results" / f"viva_psf_swing_{mode}" for mode in ("charge", "discharge")}
VIVA_VIEWER = ROOT.parents[1] / "cadence_work/show_native_psf_results.il"
RUN_LOCK = threading.Lock()


def write_psf(psf: Path, data: np.ndarray, mode: str, duration: str) -> None:
    psf.mkdir(parents=True, exist_ok=True)
    # The placeholder simulator previously wrote malformed runObjFile and
    # simRunData files. Cadence's results browser rejects the whole directory
    # when the malformed runObjFile is present.
    for stale in ("runObjFile", "simRunData"):
        (psf / stale).unlink(missing_ok=True)
    stamp = time.ctime()
    log = f'''HEADER
"PSFversion" "1.00"
"Log Generator" "ngspice ADE bridge 1.0"
"Log Time Stamp" "{stamp}"
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
"ngspice 45.2 / FreePDK45 VTG, {mode}, {duration}"
)
END
'''
    for name in ("logFile", "artistLogFile"):
        (psf / name).write_text(log)
    (psf / "variables_file").write_text(f'''HEADER
"PSFversion" "1.00"
"simulator" "ngspice-bridge"
"version" "ngspice-45.2"
"date" "{stamp}"
"design" "shivam/tb_mcml_charge_pump/schematic"
"analysis" "design_variables"
TYPE
"V" "voltage" [ "V" ]
VALUE
"Vdd" 1.0
"Vbias" 0.45
END
''')
    names = ("Vop", "UP", "UP_b", "DN", "DN_b", "n_tail", "Vdd", "Vbias")
    with (psf / "tran.tran").open("w") as f:
        f.write(f'''HEADER
"PSFversion" "1.00"
"simulator" "ngspice-bridge"
"version" "ngspice-45.2"
"date" "{stamp}"
"design" "shivam/tb_mcml_charge_pump/schematic"
"analysis" "tran"
TYPE
"sweep" FLOAT DOUBLE
"node" FLOAT DOUBLE PROP(
"units" "V"
)
"branch" FLOAT DOUBLE PROP(
"units" "A"
)
SWEEP
"time" "sweep" PROP(
"units" "s"
)
TRACE
''')
        for name in names:
            f.write(f'"{name}" "node"\n"/{name}" "node"\n')
        f.write('"I(V_VDD)" "branch"\n"V_VDD:p" "branch"\nVALUE\n')
        for row in data:
            f.write('"time" %.12e\n' % row[0])
            for col, name in enumerate(names, 1):
                f.write('"%s" %.12e\n"/%s" %.12e\n' % (name, row[col], name, row[col]))
            f.write('"I(V_VDD)" %.12e\n"V_VDD:p" %.12e\n' % (row[9], row[9]))
        f.write("END\n")
    # Cadence's PSF reader accepts this numeric dataset after conversion to
    # its binary PSF representation. The local `psf` utility lives in the
    # running Cadence container, while ngspice runs on the host.
    listing = subprocess.run(
        ["docker", "ps", "--filter", "ancestor=cadence-runner:latest", "--format", "{{.ID}}"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    if len(listing) != 1:
        raise RuntimeError("Expected exactly one running cadence-runner container for PSF conversion")
    binary = psf / "tran.tran.bin"
    converted = subprocess.run(
        ["docker", "exec", listing[0], "/home/shivam/cadence/env.sh", "psf", "-b", str(psf / "tran.tran"), "-o", str(binary)],
        capture_output=True, text=True,
    )
    if converted.returncode or not binary.is_file() or binary.stat().st_size == 0:
        raise RuntimeError("Cadence PSF conversion failed: " + converted.stdout + converted.stderr)
    binary.replace(psf / "tran.tran")


def popup(metrics: dict, mode: str, duration: str) -> None:
    m = metrics
    dr = m["dynamic_range"]
    paper = m["paper_delay_comparison"]
    report = (
        "VERIFIED NUMERICAL RUN: ngspice 45.2 / FreePDK45 VTG\\n"
        "Source: current Virtuoso tb_mcml_charge_pump netlist\\n"
        f"ADE waveform: {mode}, {duration}\\n"
        "Vbias: 0.45 V, connected to M5 tail gate\\n"
        "Full-project measurements: 10 ns transients + 0-1 V DC sweep\\n\\n"
        f"UP delay: {m['charging']['delay']['mean_ps']:.3f} ps\\n"
        f"DN delay: {m['discharging']['delay']['mean_ps']:.3f} ps\\n"
        f"Paper TT delay: {paper['paper_tt_ps']:.2f} ps; measured difference: {paper['absolute_error_pct']:.2f}%\\n"
        "Comparison only: paper 10 pF load; this circuit 300 fF load.\\n"
        f"UP VDD power: {m['charging']['power']['power_uw']:.3f} uW\\n"
        f"DN VDD power: {m['discharging']['power']['power_uw']:.3f} uW\\n"
        f"Worst-direction PDP: {m['pdp']['fj']:.5f} fJ\\n"
        f"Settled output swing: {m['output_swing']['output_swing_v']:.6f} V\\n"
        f"10% current-compliance dynamic range: {'PASS' if dr['valid'] else 'NO VALID INTERVAL'}\\n"
        f"Mismatch at 0.5 V: {dr['reference_errors_pct'][2]:.2f}%\\n\\n"
        "ViVA reads Cadence PSF files; the numerical solver is ngspice, not Spectre."
    )
    # JSON quoting is safe for a SKILL string after substituting literal backslash-n.
    label = json.dumps(report.replace("\\n", "\n"))
    code = f'''printf("\\nADE ngspice bridge: verified measured results ready.\\n")
load({json.dumps(str(VIVA_VIEWER))})
hiDisplayAppDBox(
  ?name 'mcmlNgspiceResult
  ?dboxBanner "ADE run: ngspice / FreePDK45 results"
  ?dboxText {label}
  ?dialogType hicInformationDialog
  ?dialogStyle 'modal
  ?buttonLayout 'Close
)
'''
    temp = READY.with_suffix(".tmp")
    temp.write_text(code)
    temp.replace(READY)


def resolve_stop(netlist: str) -> str:
    match = re.search(r"(?mi)^\s*tran\s+tran\b[^\n]*?\bstop=([0-9.eE+-]+[fpnum]?)", netlist)
    if not match:
        return "10n"
    value = match.group(1)
    if run.number(value) <= 0 or run.number(value) > 100e-9:
        raise ValueError(f"Unsupported ADE transient stop: {value}")
    return value


def execute(request: dict) -> dict:
    actual = Path(request["netlist"]).resolve()
    if actual != run.NETLIST.resolve():
        raise ValueError("Only the checked shivam/tb_mcml_charge_pump testbench is supported; open ADE from that schematic.")
    devices, mode = run.topology()
    duration = resolve_stop(actual.read_text())
    psf = Path(request["raw_dir"]).resolve()
    log_path = Path(request["log_file"]).resolve()
    result = subprocess.run([sys.executable, str(ROOT / "run.py")], cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Verified ngspice flow failed:\n" + result.stdout + result.stderr)
    # ADE's requested stop is honored in its own PSF. Metric extraction always
    # uses independently saved 10 ns and DC analyses.
    if run.number(duration) == 10e-9:
        data = np.loadtxt(run.OUT / f"{mode}_10ns.dat", skiprows=1)
    else:
        data = run.run_case(devices, mode, duration)
    write_psf(psf, data, mode, duration)
    for side in ("charge", "discharge"):
        full = np.loadtxt(run.OUT / f"{side}_10ns.dat", skiprows=1)
        write_psf(VIVA_PSF[side], full, side, "10n")
    metrics = json.loads((run.OUT / "metrics.json").read_text())
    for side, key in (("charge", "charging"), ("discharge", "discharging")):
        settled_ns = int(round(metrics["output_swing"][key]["stop_s"] * 1e9))
        settled = np.loadtxt(run.OUT / f"{side}_{settled_ns}ns.dat", skiprows=1)
        write_psf(SWING_PSF[side], settled, side, f"{settled_ns}n")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "ADE NGSPICE BRIDGE — NOT CADENCE SPECTRE\n"
        f"Virtuoso netlist: {actual}\n"
        f"Netlist SHA256: {metrics['provenance']['virtuoso_netlist_sha256']}\n"
        f"Numerical solver: {metrics['provenance']['simulator']}\n"
        "Models: FreePDK45 nominal VTG, replacing simplified gpdk045 models\n"
        f"ADE transient: {mode}, stop={duration}, maxstep=0.5p\n"
        "Additional verified analyses: charge/discharge 10ns and 0-1V DC sweeps\n"
        f"UP delay={metrics['charging']['delay']['mean_ps']:.6f} ps\n"
        f"DN delay={metrics['discharging']['delay']['mean_ps']:.6f} ps\n"
        f"UP power={metrics['charging']['power']['power_uw']:.6f} uW\n"
        f"DN power={metrics['discharging']['power']['power_uw']:.6f} uW\n"
        f"PDP={metrics['pdp']['fj']:.6f} fJ\n"
        f"Settled swing={metrics['output_swing']['output_swing_v']:.6f} V\n"
        f"Dynamic range valid={metrics['dynamic_range']['valid']}\n"
        f"ngspice rows in ADE transient={len(data)}\n"
        "Simulation completed by ngspice bridge.\n"
    )
    popup(metrics, mode, duration)
    return {"ok": True, "mode": mode, "stop": duration, "rows": len(data), "metrics": str(run.OUT / "metrics.json")}


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            req = json.loads(self.rfile.readline().decode())
            with RUN_LOCK:
                result = execute(req)
        except Exception as exc:
            result = {"ok": False, "error": str(exc)}
            with (ROOT / "ade_bridge_errors.log").open("a") as f:
                f.write(time.ctime() + "\n" + traceback.format_exc() + "\n")
        self.wfile.write((json.dumps(result) + "\n").encode())


class Server(socketserver.UnixStreamServer):
    allow_reuse_address = True


if __name__ == "__main__":
    if SOCKET.exists(): SOCKET.unlink()
    with Server(str(SOCKET), Handler) as server:
        os.chmod(SOCKET, 0o666)
        print(f"ADE ngspice bridge listening on {SOCKET}", flush=True)
        server.serve_forever()
