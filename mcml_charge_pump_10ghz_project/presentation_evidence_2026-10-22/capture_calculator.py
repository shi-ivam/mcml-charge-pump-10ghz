#!/usr/bin/env python3
"""Capture actual ADE L Calculator evaluations from the live Xvfb Virtuoso session.

The formulas read Cadence PSF waveforms produced by the verified bridge run.
The DC mismatch formula uses the two currents in the saved ngspice DC sweep.
This script automates the existing GUI; it does not draw or alter screenshots.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
import re
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SHOTS = HERE / "screenshots"
RESULTS = ROOT / "mcml_charge_pump_10ghz_project/mcml_cp_sim/verified_flow/results"
XDOTOOL = "/tmp/vlsi_x11_tools/usr/bin/xdotool"
XCLIP = "/tmp/vlsi_x11_tools/usr/bin/xclip"
WINDOW = "0x200b83"
ENV = os.environ.copy()
ENV.update(DISPLAY=":98", LD_LIBRARY_PATH="/tmp/vlsi_x11_tools/usr/lib/x86_64-linux-gnu")


def run(*args: str, input_text: str | None = None) -> None:
    subprocess.run(args, input=None if input_text is None else input_text.encode(), env=ENV, check=True)


def action(*args: str) -> None:
    run(XDOTOOL, *args)
    time.sleep(0.18)


def screenshot(name: str) -> Path:
    path = SHOTS / name
    run("ffmpeg", "-loglevel", "error", "-f", "x11grab", "-window_id", WINDOW,
        "-i", ":98", "-frames:v", "1", "-y", str(path))
    return path


def capture(name: str, expression: str) -> None:
    run(XCLIP, "-selection", "clipboard", input_text=expression)
    action("windowraise", WINDOW)
    # Remove the one expression displayed in Stack after the previous capture.
    action("mousemove", "260", "676", "click", "1")
    action("mousemove", "218", "741", "click", "1")
    action("mousemove", "450", "355", "click", "1", "key", "ctrl+a", "ctrl+v")
    action("mousemove", "350", "620", "click", "1")  # Push original formula to Stack.
    action("mousemove", "472", "313", "click", "1")  # Cadence Evaluate & Plot.
    time.sleep(0.35)
    path = screenshot(name)
    print(f"{path.name}: {expression[:80]}")


def main() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    blocks = re.findall(r"```skill\n(.*?)\n```", (ROOT / "GUIDE.md").read_text(), re.S)
    charge = RESULTS / "viva_psf_charge"
    discharge = RESULTS / "viva_psf_discharge"
    power = lambda psf: (f'let((d i) d="{psf}" '
                         'i=getData("I(V_VDD)" ?result \'tran ?resultsDir d) '
                         '-1e6*average(clip(i 1e-9 10e-9)))')
    with (RESULTS / "dc_compliance.csv").open(newline="") as file:
        row = next(r for r in csv.DictReader(file) if abs(float(r["vop_v"]) - 0.5) < 1e-12)
    ich = row["i_charge_a"]
    idn = row["i_discharge_a"]
    mismatch = f"200*abs({ich}-{idn})/({ich}+{idn})"
    expressions = [
        ("05_delay_charge_edge.png", blocks[2]),
        ("06_delay_charge_mean.png", blocks[3]),
        ("07_delay_discharge_edge.png", blocks[4]),
        ("08_delay_discharge_mean.png", blocks[5]),
        ("09_delay_paper_difference.png", blocks[6]),
        ("10_power_charge.png", power(charge)),
        ("11_power_discharge.png", power(discharge)),
        ("12_swing_charge_high.png", blocks[7]),
        ("13_swing_discharge_low.png", blocks[8]),
        ("14_swing_combined.png", blocks[9]),
        ("15_dc_mismatch_at_0p5v.png", mismatch),
    ]
    for name, expression in expressions:
        capture(name, expression)


if __name__ == "__main__":
    main()
